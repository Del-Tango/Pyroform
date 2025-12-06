"""
Pyroform Data Models
"""
from dataclasses import dataclass
from typing import List, Dict, Any, Set, Union, Optional
from enum import Enum


class ActionType(Enum):
    CONFIGURE: str = "configure"
    SCORCH: str = "scorch"
    MOUNT: str = "mount"
    VALIDATE: str = "validate"
    SNAPSHOT: str = "snapshot"


@dataclass
class User:
    label: str
    name: str
    password: str
    groups: List[str]


@dataclass
class Group:
    label: str
    name: str
    users: List[str]


@dataclass
class Device:
    label: str
    path: str
    partition: int
    mountpoint: str
    state: List[str]  # dir|fl,path,owner,group,permissions


@dataclass
class Exclude:
    users: Union[List[str], None]
    groups: Union[List[str], None]
    devices: Union[List[str], None]
    directories: Union[List[str], None]
    files: Union[List[str], None]
    links: Union[List[str], None]


@dataclass
class PyroConfig:
    label: str
    users: List[User]
    groups: List[Group]
    devices: List[Device]
    excludes: Exclude

    def __post_init__(self):
        """Validate required fields after initialization"""
        if not self.label:
            raise ValueError("PyroConfig must have a label")

        # Ensure lists are initialized even if None
        self.users = self.users or []
        self.groups = self.groups or []
        self.devices = self.devices or []
        self.excludes = self.excludes or Exclude()


@dataclass
class FileInfo:
    path: str
    owner: str
    group: str
    permissions: str
    type: str


@dataclass
class FileSystemEntry:
    """Represents a filesystem entry (file, directory, or symlink)."""
    path: str
    type: str  # 'file', 'directory', or 'symlink'
    owner: str
    group: str
    permissions: str
    mountpoint: str
    target: Optional[str] = None


@dataclass
class SystemUser:
    """Represents a system user."""
    username: str
    uid: int
    gid: int
    home_directory: str
    shell: str
    gecos: str
    groups: List[str]


@dataclass
class SystemGroup:
    """Represents a system group."""
    groupname: str
    gid: int
    members: List[str]


@dataclass
class MountedDevice:
    """Represents a mounted device."""
    device_path: str
    mountpoint: str
    filesystem_type: str
    mount_options: str
    partition: str
    partitions: List[Dict[str, str]]
    files: List[FileSystemEntry]
    directories: List[FileSystemEntry]
    symlinks: List[FileSystemEntry]


@dataclass
class ScorchResult:
    """Result of scorch operation"""

    dry_run: bool
    errors: List[Any]
    success: bool
    details: Dict[str, Any]


@dataclass
class ConfigureResult:
    """ """

    resources_added: List[Dict[str, Any]]
    dry_run: bool
    errors: List[Any]
    success: bool
    details: Dict[str, Any]

@dataclass
class SnapshotResult:
    """ """

    snapshot: Dict[str, Any]
    errors: List[Any]
    success: bool
    details: Dict[str, Any]


@dataclass
class MountResult:
    """ """

    resources_mounted: List[Dict[str, Any]]
    errors: List[Any]
    success: bool
    details: Dict[str, Any]


@dataclass
class ValidationResult:
    """Result of system validation"""

    is_valid: bool
    system_state: Dict[str, list]
    discrepancies: Dict[str, list]
    summary: Dict[str, Any]
    errors: List[Any]
    details: Dict[str, Any]


@dataclass
class ValidationSummary:
    """Summary of validation results."""
    total_checks: int
    passed: int
    failed: int
    warnings: int
    total_issues: int
    critical_issues: int
    is_valid: bool



# CODE DUMP

