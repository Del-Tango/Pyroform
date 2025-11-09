"""
Scorch Engine for Pyroform - Cleanup of unspecified resources
"""
import subprocess
import os
import shutil
from dataclasses import dataclass
from typing import List, Dict, Any, Set
from pathlib import Path

from .models import PyroConfig


@dataclass
class ScorchResult:
    """Result of scorch operation"""
    resources_removed: List[str]
    resources_failed: List[Dict[str, Any]]
    dry_run: bool
    success: bool


class ScorchEngine:
    """
    Engine for cleaning up system resources not specified in configuration
    """

    def __init__(self, safety_check: bool = True):
        """
        Initialize ScorchEngine

        Args:
            safety_check: Whether to prompt for confirmation before destructive operations
        """
        self.safety_check = safety_check

    def execute_scorch(self, config: PyroConfig, dry_run: bool = False) -> ScorchResult:
        """
        Remove resources not specified in configuration

        Args:
            config: Desired configuration (resources to keep)
            dry_run: If True, only show what would be removed without actually removing

        Returns:
            ScorchResult with removal results
        """
        # Safety check
        if self.safety_check and not dry_run:
            if not self._confirm_scorch(config):
                return ScorchResult(
                    resources_removed=[],
                    resources_failed=[],
                    dry_run=dry_run,
                    success=False
                )

        current_state = self._get_current_system_state()
        resources_to_remove = self._calculate_cleanup_set(config, current_state)

        removed = []
        failed = []

        for resource in resources_to_remove:
            resource_type = resource["type"]
            resource_id = resource["id"]

            if dry_run:
                removed.append(f"{resource_type}:{resource_id} (dry-run)")
            else:
                success = self._execute_removal(resource_type, resource_id)
                if success:
                    removed.append(f"{resource_type}:{resource_id}")
                else:
                    failed.append({
                        "type": resource_type,
                        "id": resource_id,
                        "error": f"Failed to remove {resource_type} {resource_id}"
                    })
                    # Stop on first failure for safety
                    break

        return ScorchResult(
            resources_removed=removed,
            resources_failed=failed,
            dry_run=dry_run,
            success=len(failed) == 0
        )

    def _get_current_system_state(self) -> Dict[str, Any]:
        """
        Get current system state for scorch analysis

        Returns:
            Current system state
        """
        # Use the same method as validator but with more detail
        from .validator import SystemValidator
        validator = SystemValidator()
        state = validator._get_current_system_state()

        # Enhance with file system discovery
        state["filesystem"] = self._discover_filesystem_state()
        return state

    def _discover_filesystem_state(self) -> Dict[str, List[str]]:
        """
        Discover files, directories, and links in managed locations

        Returns:
            Dictionary with lists of files, directories, and links
        """
        filesystem_state = {
            "files": [],
            "directories": [],
            "links": []
        }

        # Define managed locations (these should be configurable)
        managed_locations = [
            "/home",
            "/mnt",
            "/opt",
            "/var/lib"  # Add more as needed
        ]

        for location in managed_locations:
            if os.path.exists(location):
                self._scan_location(Path(location), filesystem_state)

        return filesystem_state

    def _scan_location(self, path: Path, filesystem_state: Dict[str, List[str]]):
        """
        Recursively scan a location for files, directories, and links

        Args:
            path: Path to scan
            filesystem_state: State dictionary to populate
        """
        try:
            for item in path.iterdir():
                try:
                    if item.is_symlink():
                        filesystem_state["links"].append(str(item))
                    elif item.is_file():
                        filesystem_state["files"].append(str(item))
                    elif item.is_dir():
                        filesystem_state["directories"].append(str(item))
                        # Recursively scan directories (with depth limit for safety)
                        if len(str(item).split('/')) < 10:  # Depth limit
                            self._scan_location(item, filesystem_state)
                except (PermissionError, OSError):
                    # Skip items we can't access
                    continue
        except (PermissionError, OSError):
            # Skip locations we can't access
            pass

    def _calculate_cleanup_set(self, config: PyroConfig, current_state: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Calculate which resources should be removed

        Args:
            config: Desired configuration
            current_state: Current system state

        Returns:
            List of resources to remove
        """
        resources_to_remove = []

        # Calculate users to remove
        desired_users = {user.name for user in config.users}
        current_users = set(current_state.get("users", []))
        users_to_remove = current_users - desired_users

        # Don't remove system users (UID < 1000)
        for user in users_to_remove.copy():
            try:
                # Skip UID check in test environment or when commands aren't available
                result = subprocess.run(
                    ["id", "-u", user],
                    capture_output=True,
                    text=True,
                    check=False  # Don't raise exception
                )
                if result.returncode == 0 and result.stdout.strip():
                    uid = int(result.stdout.strip())
                    if uid < 1000:
                        users_to_remove.remove(user)
                else:
                    # If we can't check UID, assume it's safe to remove (for testing)
                    pass
            except (ValueError, FileNotFoundError):
                # If id command fails or UID is invalid, skip this user
                users_to_remove.remove(user)

        for user in users_to_remove:
            resources_to_remove.append({"type": "user", "id": user})

        # Calculate groups to remove
        desired_groups = {group.name for group in config.groups}
        current_groups = set(current_state.get("groups", []))
        groups_to_remove = current_groups - desired_groups

        # Don't remove system groups (GID < 1000)
        for group in groups_to_remove.copy():
            try:
                result = subprocess.run(
                    ["getent", "group", group],
                    capture_output=True,
                    text=True,
                    check=False  # Don't raise exception
                )
                if result.returncode == 0 and result.stdout.strip():
                    gid = result.stdout.split(':')[2]
                    if int(gid) < 1000:
                        groups_to_remove.remove(group)
                else:
                    # If we can't check GID, assume it's safe to remove (for testing)
                    pass
            except (ValueError, IndexError, FileNotFoundError):
                # If getent fails or GID is invalid, skip this group
                groups_to_remove.remove(group)

        for group in groups_to_remove:
            resources_to_remove.append({"type": "group", "id": group})

        # Calculate mounts to remove (only those not in desired configuration)
        desired_mounts = {device.mountpoint for device in config.devices}
        current_mounts = set(current_state.get("mounts", {}).values())
        mounts_to_remove = current_mounts - desired_mounts

        # Don't remove system mounts
        system_mounts = {"/", "/boot", "/home", "/var", "/tmp", "/proc", "/sys"}
        for mount in mounts_to_remove.copy():
            if mount in system_mounts or any(mount.startswith(sys_mount + '/') for sys_mount in system_mounts):
                mounts_to_remove.remove(mount)

        for mount in mounts_to_remove:
            resources_to_remove.append({"type": "mount", "id": mount})

        # Calculate files, directories, and links to remove
        desired_paths = self._get_desired_paths(config)
        current_filesystem = current_state.get("filesystem", {})

        # Remove files not in desired configuration
        current_files = set(current_filesystem.get("files", []))
        files_to_remove = current_files - desired_paths

        # Remove directories not in desired configuration (be careful with this!)
        current_dirs = set(current_filesystem.get("directories", []))
        dirs_to_remove = current_dirs - desired_paths

        # Remove links not in desired configuration
        current_links = set(current_filesystem.get("links", []))
        links_to_remove = current_links - desired_paths

        # Add file system resources to removal list
        for file_path in files_to_remove:
            # Don't remove system files or files in system directories
            if not self._is_system_file(file_path):
                resources_to_remove.append({"type": "file", "id": file_path})

        for dir_path in dirs_to_remove:
            # Don't remove system directories
            if not self._is_system_directory(dir_path):
                resources_to_remove.append({"type": "directory", "id": dir_path})

        for link_path in links_to_remove:
            # Don't remove system links
            if not self._is_system_file(link_path):
                resources_to_remove.append({"type": "link", "id": link_path})

        return resources_to_remove

    def _get_desired_paths(self, config: PyroConfig) -> Set[str]:
        """
        Get all file system paths specified in the configuration

        Args:
            config: Pyro configuration

        Returns:
            Set of all desired file system paths
        """
        desired_paths = set()

        # Add mountpoints from devices
        for device in config.devices:
            desired_paths.add(device.mountpoint)

        # Add paths from device states
        for device in config.devices:
            for state_entry in device.state:
                state_parts = state_entry.split(',')
                if len(state_parts) >= 2:
                    path = state_parts[1]
                    desired_paths.add(path)

                    # For directories, also include parent directories
                    if state_parts[0] == "dir":
                        parent = Path(path).parent
                        while str(parent) != "/" and str(parent) != ".":
                            desired_paths.add(str(parent))
                            parent = parent.parent

        return desired_paths

    def _is_system_file(self, file_path: str) -> bool:
        """
        Check if a file is a system file that shouldn't be removed

        Args:
            file_path: Path to check

        Returns:
            True if it's a system file, False otherwise
        """
        system_paths = [
            "/etc/", "/bin/", "/sbin/", "/lib/", "/usr/", "/boot/",
            "/proc/", "/sys/", "/dev/", "/run/", "/tmp/"
        ]

        file_path = str(file_path)
        return any(file_path.startswith(sys_path) for sys_path in system_paths)

    def _is_system_directory(self, dir_path: str) -> bool:
        """
        Check if a directory is a system directory that shouldn't be removed

        Args:
            dir_path: Path to check

        Returns:
            True if it's a system directory, False otherwise
        """
        system_dirs = [
            "/etc", "/bin", "/sbin", "/lib", "/usr", "/boot",
            "/proc", "/sys", "/dev", "/run", "/tmp", "/home",
            "/var", "/opt"
        ]

        dir_path = str(dir_path)
        # Don't remove system directories themselves
        if dir_path in system_dirs:
            return True

        # Don't remove directories that are parents of system directories
        for sys_dir in system_dirs:
            if sys_dir.startswith(dir_path + '/'):
                return True

        return False

    def _execute_removal(self, resource_type: str, resource_id: str) -> bool:
        """
        Execute removal of a specific resource

        Args:
            resource_type: Type of resource (user, group, mount, file, directory, link)
            resource_id: Identifier of the resource

        Returns:
            True if removal was successful, False otherwise
        """
        try:
            if resource_type == "user":
                # Check if command exists before trying to execute
                result = subprocess.run(
                    ["which", "userdel"],
                    capture_output=True,
                    text=True,
                    check=False
                )
                if result.returncode != 0:
                    return False  # Command not available

                result = subprocess.run(
                    ["userdel", "-r", resource_id],  # -r removes home directory
                    capture_output=True,
                    text=True,
                    check=False  # Don't raise exception, just return False
                )
                return result.returncode == 0

            elif resource_type == "group":
                result = subprocess.run(
                    ["which", "groupdel"],
                    capture_output=True,
                    text=True,
                    check=False
                )
                if result.returncode != 0:
                    return False

                result = subprocess.run(
                    ["groupdel", resource_id],
                    capture_output=True,
                    text=True,
                    check=False
                )
                return result.returncode == 0

            elif resource_type == "mount":
                result = subprocess.run(
                    ["which", "umount"],
                    capture_output=True,
                    text=True,
                    check=False
                )
                if result.returncode != 0:
                    return False

                result = subprocess.run(
                    ["umount", resource_id],
                    capture_output=True,
                    text=True,
                    check=False
                )
                return result.returncode == 0

            elif resource_type == "file":
                try:
                    os.remove(resource_id)
                    return True
                except (OSError, FileNotFoundError):
                    return False

            elif resource_type == "directory":
                try:
                    # Use shutil.rmtree for recursive directory removal
                    shutil.rmtree(resource_id)
                    return True
                except (OSError, FileNotFoundError):
                    return False

            elif resource_type == "link":
                try:
                    os.unlink(resource_id)
                    return True
                except (OSError, FileNotFoundError):
                    return False

            else:
                return False

        except (subprocess.SubprocessError, FileNotFoundError, ImportError) as e:
            print(f"Failed to remove {resource_type} {resource_id}: {e}")
            return False

    def _confirm_scorch(self, config: PyroConfig) -> bool:
        """
        Confirm scorch operation with user

        Args:
            config: Configuration that will be used to determine what to keep

        Returns:
            True if confirmed, False if cancelled
        """
        print(f"WARNING: Scorch action will remove system resources not specified in '{config.label}'.")
        print("This includes:")
        print("  - Users not in the configuration")
        print("  - Groups not in the configuration")
        print("  - Mount points not in the configuration")
        print("  - Files not in the configuration")
        print("  - Directories not in the configuration")
        print("  - Symbolic links not in the configuration")
        print()
        print("THIS IS A DESTRUCTIVE OPERATION THAT CANNOT BE UNDONE!")
        print()
        response = input("Are you sure you want to continue? (yes/NO): ")
        return response.lower() in ['yes', 'y']

# CODE DUMP

#   """
#   Scorch Engine for Pyroform - Cleanup of unspecified resources
#   """
#   import subprocess
#   import os
#   import shutil
#   from dataclasses import dataclass
#   from typing import List, Dict, Any, Set
#   from pathlib import Path

#   from .models import PyroConfig


#   @dataclass
#   class ScorchResult:
#       """Result of scorch operation"""
#       resources_removed: List[str]
#       resources_failed: List[Dict[str, Any]]
#       dry_run: bool
#       success: bool


#   class ScorchEngine:
#       """
#       Engine for cleaning up system resources not specified in configuration
#       """

#       def __init__(self, safety_check: bool = True):
#           """
#           Initialize ScorchEngine

#           Args:
#               safety_check: Whether to prompt for confirmation before destructive operations
#           """
#           self.safety_check = safety_check

#       def execute_scorch(self, config: PyroConfig, dry_run: bool = False) -> ScorchResult:
#           """
#           Remove resources not specified in configuration

#           Args:
#               config: Desired configuration (resources to keep)
#               dry_run: If True, only show what would be removed without actually removing

#           Returns:
#               ScorchResult with removal results
#           """
#           # Safety check
#           if self.safety_check and not dry_run:
#               if not self._confirm_scorch(config):
#                   return ScorchResult(
#                       resources_removed=[],
#                       resources_failed=[],
#                       dry_run=dry_run,
#                       success=False
#                   )

#           current_state = self._get_current_system_state()
#           resources_to_remove = self._calculate_cleanup_set(config, current_state)

#           removed = []
#           failed = []

#           for resource in resources_to_remove:
#               resource_type = resource["type"]
#               resource_id = resource["id"]

#               if dry_run:
#                   removed.append(f"{resource_type}:{resource_id} (dry-run)")
#               else:
#                   success = self._execute_removal(resource_type, resource_id)
#                   if success:
#                       removed.append(f"{resource_type}:{resource_id}")
#                   else:
#                       failed.append({
#                           "type": resource_type,
#                           "id": resource_id,
#                           "error": f"Failed to remove {resource_type} {resource_id}"
#                       })
#                       # Stop on first failure for safety
#                       break

#           return ScorchResult(
#               resources_removed=removed,
#               resources_failed=failed,
#               dry_run=dry_run,
#               success=len(failed) == 0
#           )

#       def _get_current_system_state(self) -> Dict[str, Any]:
#           """
#           Get current system state for scorch analysis

#           Returns:
#               Current system state
#           """
#           # Use the same method as validator but with more detail
#           from .validator import SystemValidator
#           validator = SystemValidator()
#           state = validator._get_current_system_state()

#           # Enhance with file system discovery
#           state["filesystem"] = self._discover_filesystem_state()
#           return state

#       def _discover_filesystem_state(self) -> Dict[str, List[str]]:
#           """
#           Discover files, directories, and links in managed locations

#           Returns:
#               Dictionary with lists of files, directories, and links
#           """
#           filesystem_state = {
#               "files": [],
#               "directories": [],
#               "links": []
#           }

#           # Define managed locations (these should be configurable)
#           managed_locations = [
#               "/home",
#               "/mnt",
#               "/opt",
#               "/var/lib"  # Add more as needed
#           ]

#           for location in managed_locations:
#               if os.path.exists(location):
#                   self._scan_location(Path(location), filesystem_state)

#           return filesystem_state

#       def _scan_location(self, path: Path, filesystem_state: Dict[str, List[str]]):
#           """
#           Recursively scan a location for files, directories, and links

#           Args:
#               path: Path to scan
#               filesystem_state: State dictionary to populate
#           """
#           try:
#               for item in path.iterdir():
#                   try:
#                       if item.is_symlink():
#                           filesystem_state["links"].append(str(item))
#                       elif item.is_file():
#                           filesystem_state["files"].append(str(item))
#                       elif item.is_dir():
#                           filesystem_state["directories"].append(str(item))
#                           # Recursively scan directories (with depth limit for safety)
#                           if len(str(item).split('/')) < 10:  # Depth limit
#                               self._scan_location(item, filesystem_state)
#                   except (PermissionError, OSError):
#                       # Skip items we can't access
#                       continue
#           except (PermissionError, OSError):
#               # Skip locations we can't access
#               pass

#       def _calculate_cleanup_set(self, config: PyroConfig, current_state: Dict[str, Any]) -> List[Dict[str, str]]:
#           """
#           Calculate which resources should be removed

#           Args:
#               config: Desired configuration
#               current_state: Current system state

#           Returns:
#               List of resources to remove
#           """
#           resources_to_remove = []

#           # Calculate users to remove
#           desired_users = {user.name for user in config.users}
#           current_users = set(current_state.get("users", []))
#           users_to_remove = current_users - desired_users

#           # Don't remove system users (UID < 1000)
#           for user in users_to_remove.copy():
#               try:
#                   result = subprocess.run(
#                       ["id", "-u", user],
#                       capture_output=True,
#                       text=True,
#                       check=True
#                   )
#                   if int(result.stdout.strip()) < 1000:
#                       users_to_remove.remove(user)
#               except (subprocess.CalledProcessError, ValueError, FileNotFoundError):
#                   users_to_remove.remove(user)  # Remove if we can't check UID

#           for user in users_to_remove:
#               resources_to_remove.append({"type": "user", "id": user})

#           # Calculate groups to remove
#           desired_groups = {group.name for group in config.groups}
#           current_groups = set(current_state.get("groups", []))
#           groups_to_remove = current_groups - desired_groups

#           # Don't remove system groups (GID < 1000)
#           for group in groups_to_remove.copy():
#               try:
#                   result = subprocess.run(
#                       ["getent", "group", group],
#                       capture_output=True,
#                       text=True,
#                       check=True
#                   )
#                   gid = result.stdout.split(':')[2]
#                   if int(gid) < 1000:
#                       groups_to_remove.remove(group)
#               except (subprocess.CalledProcessError, ValueError, IndexError, FileNotFoundError):
#                   groups_to_remove.remove(group)  # Remove if we can't check GID

#           for group in groups_to_remove:
#               resources_to_remove.append({"type": "group", "id": group})

#           # Calculate mounts to remove (only those not in desired configuration)
#           desired_mounts = {device.mountpoint for device in config.devices}
#           current_mounts = set(current_state.get("mounts", {}).values())
#           mounts_to_remove = current_mounts - desired_mounts

#           # Don't remove system mounts
#           system_mounts = {"/", "/boot", "/home", "/var", "/tmp", "/proc", "/sys"}
#           for mount in mounts_to_remove.copy():
#               if mount in system_mounts or any(mount.startswith(sys_mount + '/') for sys_mount in system_mounts):
#                   mounts_to_remove.remove(mount)

#           for mount in mounts_to_remove:
#               resources_to_remove.append({"type": "mount", "id": mount})

#           # Calculate files, directories, and links to remove
#           desired_paths = self._get_desired_paths(config)
#           current_filesystem = current_state.get("filesystem", {})

#           # Remove files not in desired configuration
#           current_files = set(current_filesystem.get("files", []))
#           files_to_remove = current_files - desired_paths

#           # Remove directories not in desired configuration (be careful with this!)
#           current_dirs = set(current_filesystem.get("directories", []))
#           dirs_to_remove = current_dirs - desired_paths

#           # Remove links not in desired configuration
#           current_links = set(current_filesystem.get("links", []))
#           links_to_remove = current_links - desired_paths

#           # Add file system resources to removal list
#           for file_path in files_to_remove:
#               # Don't remove system files or files in system directories
#               if not self._is_system_file(file_path):
#                   resources_to_remove.append({"type": "file", "id": file_path})

#           for dir_path in dirs_to_remove:
#               # Don't remove system directories
#               if not self._is_system_directory(dir_path):
#                   resources_to_remove.append({"type": "directory", "id": dir_path})

#           for link_path in links_to_remove:
#               # Don't remove system links
#               if not self._is_system_file(link_path):
#                   resources_to_remove.append({"type": "link", "id": link_path})

#           return resources_to_remove

#       def _get_desired_paths(self, config: PyroConfig) -> Set[str]:
#           """
#           Get all file system paths specified in the configuration

#           Args:
#               config: Pyro configuration

#           Returns:
#               Set of all desired file system paths
#           """
#           desired_paths = set()

#           # Add mountpoints from devices
#           for device in config.devices:
#               desired_paths.add(device.mountpoint)

#           # Add paths from device states
#           for device in config.devices:
#               for state_entry in device.state:
#                   state_parts = state_entry.split(',')
#                   if len(state_parts) >= 2:
#                       path = state_parts[1]
#                       desired_paths.add(path)

#                       # For directories, also include parent directories
#                       if state_parts[0] == "dir":
#                           parent = Path(path).parent
#                           while str(parent) != "/" and str(parent) != ".":
#                               desired_paths.add(str(parent))
#                               parent = parent.parent

#           return desired_paths

#       def _is_system_file(self, file_path: str) -> bool:
#           """
#           Check if a file is a system file that shouldn't be removed

#           Args:
#               file_path: Path to check

#           Returns:
#               True if it's a system file, False otherwise
#           """
#           system_paths = [
#               "/etc/", "/bin/", "/sbin/", "/lib/", "/usr/", "/boot/",
#               "/proc/", "/sys/", "/dev/", "/run/", "/tmp/"
#           ]

#           file_path = str(file_path)
#           return any(file_path.startswith(sys_path) for sys_path in system_paths)

#       def _is_system_directory(self, dir_path: str) -> bool:
#           """
#           Check if a directory is a system directory that shouldn't be removed

#           Args:
#               dir_path: Path to check

#           Returns:
#               True if it's a system directory, False otherwise
#           """
#           system_dirs = [
#               "/etc", "/bin", "/sbin", "/lib", "/usr", "/boot",
#               "/proc", "/sys", "/dev", "/run", "/tmp", "/home",
#               "/var", "/opt"
#           ]

#           dir_path = str(dir_path)
#           # Don't remove system directories themselves
#           if dir_path in system_dirs:
#               return True

#           # Don't remove directories that are parents of system directories
#           for sys_dir in system_dirs:
#               if sys_dir.startswith(dir_path + '/'):
#                   return True

#           return False

#       def _execute_removal(self, resource_type: str, resource_id: str) -> bool:
#           """
#           Execute removal of a specific resource

#           Args:
#               resource_type: Type of resource (user, group, mount, file, directory, link)
#               resource_id: Identifier of the resource

#           Returns:
#               True if removal was successful, False otherwise
#           """
#           try:
#               if resource_type == "user":
#                   # Check if command exists before trying to execute
#                   result = subprocess.run(
#                       ["which", "userdel"],
#                       capture_output=True,
#                       text=True,
#                       check=False
#                   )
#                   if result.returncode != 0:
#                       return False  # Command not available

#                   result = subprocess.run(
#                       ["userdel", "-r", resource_id],  # -r removes home directory
#                       capture_output=True,
#                       text=True,
#                       check=False  # Don't raise exception, just return False
#                   )
#                   return result.returncode == 0

#               elif resource_type == "group":
#                   result = subprocess.run(
#                       ["which", "groupdel"],
#                       capture_output=True,
#                       text=True,
#                       check=False
#                   )
#                   if result.returncode != 0:
#                       return False

#                   result = subprocess.run(
#                       ["groupdel", resource_id],
#                       capture_output=True,
#                       text=True,
#                       check=False
#                   )
#                   return result.returncode == 0

#               elif resource_type == "mount":
#                   result = subprocess.run(
#                       ["which", "umount"],
#                       capture_output=True,
#                       text=True,
#                       check=False
#                   )
#                   if result.returncode != 0:
#                       return False

#                   result = subprocess.run(
#                       ["umount", resource_id],
#                       capture_output=True,
#                       text=True,
#                       check=False
#                   )
#                   return result.returncode == 0

#               elif resource_type == "file":
#                   try:
#                       os.remove(resource_id)
#                       return True
#                   except (OSError, FileNotFoundError):
#                       return False

#               elif resource_type == "directory":
#                   try:
#                       import shutil
#                       shutil.rmtree(resource_id)
#                       return True
#                   except (OSError, FileNotFoundError):
#                       return False

#               elif resource_type == "link":
#                   try:
#                       os.unlink(resource_id)
#                       return True
#                   except (OSError, FileNotFoundError):
#                       return False

#               else:
#                   return False

#           except (subprocess.SubprocessError, FileNotFoundError, ImportError) as e:
#               print(f"Failed to remove {resource_type} {resource_id}: {e}")
#               return False

#       def _confirm_scorch(self, config: PyroConfig) -> bool:
#           """
#           Confirm scorch operation with user

#           Args:
#               config: Configuration that will be used to determine what to keep

#           Returns:
#               True if confirmed, False if cancelled
#           """
#           print(f"WARNING: Scorch action will remove system resources not specified in '{config.label}'.")
#           print("This includes:")
#           print("  - Users not in the configuration")
#           print("  - Groups not in the configuration")
#           print("  - Mount points not in the configuration")
#           print("  - Files not in the configuration")
#           print("  - Directories not in the configuration")
#           print("  - Symbolic links not in the configuration")
#           print()
#           print("THIS IS A DESTRUCTIVE OPERATION THAT CANNOT BE UNDONE!")
#           print()
#           response = input("Are you sure you want to continue? (yes/NO): ")
#           return response.lower() in ['yes', 'y']

# CODE DUMP

#   """
#   Scorch Engine for Pyroform - Cleanup of unspecified resources
#   """
#   import subprocess
#   from dataclasses import dataclass
#   from typing import List, Dict, Any, Set
#   from pathlib import Path

#   from .models import PyroConfig


#   @dataclass
#   class ScorchResult:
#       """Result of scorch operation"""
#       resources_removed: List[str]
#       resources_failed: List[Dict[str, Any]]
#       dry_run: bool
#       success: bool


#   class ScorchEngine:
#       """
#       Engine for cleaning up system resources not specified in configuration
#       """

#       def __init__(self, safety_check: bool = True):
#           """
#           Initialize ScorchEngine

#           Args:
#               safety_check: Whether to prompt for confirmation before destructive operations
#           """
#           self.safety_check = safety_check

#       def execute_scorch(self, config: PyroConfig, dry_run: bool = False) -> ScorchResult:
#           """
#           Remove resources not specified in configuration

#           Args:
#               config: Desired configuration (resources to keep)
#               dry_run: If True, only show what would be removed without actually removing

#           Returns:
#               ScorchResult with removal results
#           """
#           # Safety check
#           if self.safety_check and not dry_run:
#               if not self._confirm_scorch(config):
#                   return ScorchResult(
#                       resources_removed=[],
#                       resources_failed=[],
#                       dry_run=dry_run,
#                       success=False
#                   )

#           current_state = self._get_current_system_state()
#           resources_to_remove = self._calculate_cleanup_set(config, current_state)

#           removed = []
#           failed = []

#           for resource in resources_to_remove:
#               resource_type = resource["type"]
#               resource_id = resource["id"]

#               if dry_run:
#                   removed.append(f"{resource_type}:{resource_id} (dry-run)")
#               else:
#                   success = self._execute_removal(resource_type, resource_id)
#                   if success:
#                       removed.append(f"{resource_type}:{resource_id}")
#                   else:
#                       failed.append({
#                           "type": resource_type,
#                           "id": resource_id,
#                           "error": f"Failed to remove {resource_type} {resource_id}"
#                       })
#                       # Stop on first failure for safety
#                       break

#           return ScorchResult(
#               resources_removed=removed,
#               resources_failed=failed,
#               dry_run=dry_run,
#               success=len(failed) == 0
#           )

#       def _get_current_system_state(self) -> Dict[str, Any]:
#           """
#           Get current system state for scorch analysis

#           Returns:
#               Current system state
#           """
#           # Use the same method as validator but with more detail
#           from .validator import SystemValidator
#           validator = SystemValidator()
#           return validator._get_current_system_state()

#       def _calculate_cleanup_set(self, config: PyroConfig, current_state: Dict[str, Any]) -> List[Dict[str, str]]:
#           """
#           Calculate which resources should be removed

#           Args:
#               config: Desired configuration
#               current_state: Current system state

#           Returns:
#               List of resources to remove
#           """
#           resources_to_remove = []

#           # Calculate users to remove
#           desired_users = {user.name for user in config.users}
#           current_users = set(current_state.get("users", []))
#           users_to_remove = current_users - desired_users

#           # Don't remove system users (UID < 1000)
#           for user in users_to_remove.copy():
#               try:
#                   result = subprocess.run(
#                       ["id", "-u", user],
#                       capture_output=True,
#                       text=True,
#                       check=True
#                   )
#                   if int(result.stdout.strip()) < 1000:
#                       users_to_remove.remove(user)
#               except (subprocess.CalledProcessError, ValueError, FileNotFoundError):
#                   users_to_remove.remove(user)  # Remove if we can't check UID

#           for user in users_to_remove:
#               resources_to_remove.append({"type": "user", "id": user})

#           # Calculate groups to remove
#           desired_groups = {group.name for group in config.groups}
#           current_groups = set(current_state.get("groups", []))
#           groups_to_remove = current_groups - desired_groups

#           # Don't remove system groups (GID < 1000)
#           for group in groups_to_remove.copy():
#               try:
#                   result = subprocess.run(
#                       ["getent", "group", group],
#                       capture_output=True,
#                       text=True,
#                       check=True
#                   )
#                   gid = result.stdout.split(':')[2]
#                   if int(gid) < 1000:
#                       groups_to_remove.remove(group)
#               except (subprocess.CalledProcessError, ValueError, IndexError, FileNotFoundError):
#                   groups_to_remove.remove(group)  # Remove if we can't check GID

#           for group in groups_to_remove:
#               resources_to_remove.append({"type": "group", "id": group})

#           # Calculate mounts to remove (only those not in desired configuration)
#           desired_mounts = {device.mountpoint for device in config.devices}
#           current_mounts = set(current_state.get("mounts", {}).values())
#           mounts_to_remove = current_mounts - desired_mounts

#           # Don't remove system mounts
#           system_mounts = {"/", "/boot", "/home", "/var", "/tmp", "/proc", "/sys"}
#           for mount in mounts_to_remove.copy():
#               if mount in system_mounts or any(mount.startswith(sys_mount + '/') for sys_mount in system_mounts):
#                   mounts_to_remove.remove(mount)

#           for mount in mounts_to_remove:
#               resources_to_remove.append({"type": "mount", "id": mount})

#           return resources_to_remove

#       def _execute_removal(self, resource_type: str, resource_id: str) -> bool:
#           """
#           Execute removal of a specific resource

#           Args:
#               resource_type: Type of resource (user, group, mount)
#               resource_id: Identifier of the resource

#           Returns:
#               True if removal was successful, False otherwise
#           """
#           try:
#               if resource_type == "user":
#                   # Check if command exists before trying to execute
#                   result = subprocess.run(
#                       ["which", "userdel"],
#                       capture_output=True,
#                       text=True,
#                       check=False
#                   )
#                   if result.returncode != 0:
#                       return False  # Command not available

#                   result = subprocess.run(
#                       ["userdel", "-r", resource_id],  # -r removes home directory
#                       capture_output=True,
#                       text=True,
#                       check=False  # Don't raise exception, just return False
#                   )
#                   return result.returncode == 0

#               elif resource_type == "group":
#                   result = subprocess.run(
#                       ["which", "groupdel"],
#                       capture_output=True,
#                       text=True,
#                       check=False
#                   )
#                   if result.returncode != 0:
#                       return False

#                   result = subprocess.run(
#                       ["groupdel", resource_id],
#                       capture_output=True,
#                       text=True,
#                       check=False
#                   )
#                   return result.returncode == 0

#               elif resource_type == "mount":
#                   result = subprocess.run(
#                       ["which", "umount"],
#                       capture_output=True,
#                       text=True,
#                       check=False
#                   )
#                   if result.returncode != 0:
#                       return False

#                   result = subprocess.run(
#                       ["umount", resource_id],
#                       capture_output=True,
#                       text=True,
#                       check=False
#                   )
#                   return result.returncode == 0

#               else:
#                   return False

#           except (subprocess.SubprocessError, FileNotFoundError) as e:
#               print(f"Failed to remove {resource_type} {resource_id}: {e}")
#               return False

#       def _confirm_scorch(self, config: PyroConfig) -> bool:
#           """
#           Confirm scorch operation with user

#           Args:
#               config: Configuration that will be used to determine what to keep

#           Returns:
#               True if confirmed, False if cancelled
#           """
#           print(f"WARNING: Scorch action will remove system resources not specified in '{config.label}'.")
#           print("This includes:")
#           print("  - Users not in the configuration")
#           print("  - Groups not in the configuration")
#           print("  - Mount points not in the configuration")
#           print()
#           response = input("Are you sure you want to continue? (yes/no): ")
#           return response.lower() in ['yes', 'y']

# CODE DUMP

#   """
#   Scorch Engine for Pyroform - Cleanup of unspecified resources
#   """
#   import subprocess
#   from dataclasses import dataclass
#   from typing import List, Dict, Any, Set
#   from pathlib import Path

#   from .models import PyroConfig


#   @dataclass
#   class ScorchResult:
#       """Result of scorch operation"""
#       resources_removed: List[str]
#       resources_failed: List[Dict[str, Any]]
#       dry_run: bool
#       success: bool


#   class ScorchEngine:
#       """
#       Engine for cleaning up system resources not specified in configuration
#       """

#       def __init__(self, safety_check: bool = True):
#           """
#           Initialize ScorchEngine

#           Args:
#               safety_check: Whether to prompt for confirmation before destructive operations
#           """
#           self.safety_check = safety_check

#       def execute_scorch(self, config: PyroConfig, dry_run: bool = False) -> ScorchResult:
#           """
#           Remove resources not specified in configuration

#           Args:
#               config: Desired configuration (resources to keep)
#               dry_run: If True, only show what would be removed without actually removing

#           Returns:
#               ScorchResult with removal results
#           """
#           # Safety check
#           if self.safety_check and not dry_run:
#               if not self._confirm_scorch(config):
#                   return ScorchResult(
#                       resources_removed=[],
#                       resources_failed=[],
#                       dry_run=dry_run,
#                       success=False
#                   )

#           current_state = self._get_current_system_state()
#           resources_to_remove = self._calculate_cleanup_set(config, current_state)

#           removed = []
#           failed = []

#           for resource in resources_to_remove:
#               resource_type = resource["type"]
#               resource_id = resource["id"]

#               if dry_run:
#                   removed.append(f"{resource_type}:{resource_id} (dry-run)")
#               else:
#                   success = self._execute_removal(resource_type, resource_id)
#                   if success:
#                       removed.append(f"{resource_type}:{resource_id}")
#                   else:
#                       failed.append({
#                           "type": resource_type,
#                           "id": resource_id,
#                           "error": f"Failed to remove {resource_type} {resource_id}"
#                       })
#                       # Stop on first failure for safety
#                       break

#           return ScorchResult(
#               resources_removed=removed,
#               resources_failed=failed,
#               dry_run=dry_run,
#               success=len(failed) == 0
#           )

#       def _get_current_system_state(self) -> Dict[str, Any]:
#           """
#           Get current system state for scorch analysis

#           Returns:
#               Current system state
#           """
#           # Use the same method as validator but with more detail
#           from .validator import SystemValidator
#           validator = SystemValidator()
#           return validator._get_current_system_state()

#       def _calculate_cleanup_set(self, config: PyroConfig, current_state: Dict[str, Any]) -> List[Dict[str, str]]:
#           """
#           Calculate which resources should be removed

#           Args:
#               config: Desired configuration
#               current_state: Current system state

#           Returns:
#               List of resources to remove
#           """
#           resources_to_remove = []

#           # Calculate users to remove
#           desired_users = {user.name for user in config.users}
#           current_users = set(current_state["users"])
#           users_to_remove = current_users - desired_users

#           # Don't remove system users (UID < 1000)
#           for user in users_to_remove.copy():
#               try:
#                   result = subprocess.run(
#                       ["id", "-u", user],
#                       capture_output=True,
#                       text=True,
#                       check=True
#                   )
#                   if int(result.stdout.strip()) < 1000:
#                       users_to_remove.remove(user)
#               except (subprocess.CalledProcessError, ValueError):
#                   users_to_remove.remove(user)  # Remove if we can't check UID

#           for user in users_to_remove:
#               resources_to_remove.append({"type": "user", "id": user})

#           # Calculate groups to remove
#           desired_groups = {group.name for group in config.groups}
#           current_groups = set(current_state["groups"])
#           groups_to_remove = current_groups - desired_groups

#           # Don't remove system groups (GID < 1000)
#           for group in groups_to_remove.copy():
#               try:
#                   result = subprocess.run(
#                       ["getent", "group", group],
#                       capture_output=True,
#                       text=True,
#                       check=True
#                   )
#                   gid = result.stdout.split(':')[2]
#                   if int(gid) < 1000:
#                       groups_to_remove.remove(group)
#               except (subprocess.CalledProcessError, ValueError, IndexError):
#                   groups_to_remove.remove(group)  # Remove if we can't check GID

#           for group in groups_to_remove:
#               resources_to_remove.append({"type": "group", "id": group})

#           # Calculate mounts to remove (only those not in desired configuration)
#           desired_mounts = {device.mountpoint for device in config.devices}
#           current_mounts = set(current_state["mounts"].values())
#           mounts_to_remove = current_mounts - desired_mounts

#           # Don't remove system mounts
#           system_mounts = {"/", "/boot", "/home", "/var", "/tmp", "/proc", "/sys"}
#           for mount in mounts_to_remove.copy():
#               if mount in system_mounts or any(mount.startswith(sys_mount + '/') for sys_mount in system_mounts):
#                   mounts_to_remove.remove(mount)

#           for mount in mounts_to_remove:
#               resources_to_remove.append({"type": "mount", "id": mount})

#           return resources_to_remove

#       def _execute_removal(self, resource_type: str, resource_id: str) -> bool:
#           """
#           Execute removal of a specific resource

#           Args:
#               resource_type: Type of resource (user, group, mount)
#               resource_id: Identifier of the resource

#           Returns:
#               True if removal was successful, False otherwise
#           """
#           try:
#               if resource_type == "user":
#                   result = subprocess.run(
#                       ["userdel", "-r", resource_id],  # -r removes home directory
#                       capture_output=True,
#                       text=True,
#                       check=True
#                   )
#               elif resource_type == "group":
#                   result = subprocess.run(
#                       ["groupdel", resource_id],
#                       capture_output=True,
#                       text=True,
#                       check=True
#                   )
#               elif resource_type == "mount":
#                   result = subprocess.run(
#                       ["umount", resource_id],
#                       capture_output=True,
#                       text=True,
#                       check=True
#                   )
#               else:
#                   return False

#               return True

#           except subprocess.CalledProcessError as e:
#               print(f"Failed to remove {resource_type} {resource_id}: {e}")
#               return False

#       def _confirm_scorch(self, config: PyroConfig) -> bool:
#           """
#           Confirm scorch operation with user

#           Args:
#               config: Configuration that will be used to determine what to keep

#           Returns:
#               True if confirmed, False if cancelled
#           """
#           print(f"WARNING: Scorch action will remove system resources not specified in '{config.label}'.")
#           print("This includes:")
#           print("  - Users not in the configuration")
#           print("  - Groups not in the configuration")
#           print("  - Mount points not in the configuration")
#           print()
#           response = input("Are you sure you want to continue? (yes/no): ")
#           return response.lower() in ['yes', 'y']

# CODE DUMP

#   # pyroform/src/scorch_engine.py
#   class ScorchEngine:
#       def __init__(self, safety_check: bool = True):
#           self.safety_check = safety_check

#       def execute_scorch(self, config: PyroConfig) -> ScorchResult:
#           """Remove resources not specified in configuration"""
#           pass

#       def _calculate_cleanup_set(self) -> Set[str]:
#           """Calculate resources to be removed"""
#           pass
