# Test Performance Specification

# [ Description ]: Pyroform TPS

- Objective: Manual testing of Pyroform functionality across all components and actions.
- Scope: CLI interface, configuration parsing, system operations, error handling, and safety features.
- Environment: Clean Linux test environment (Debian VM / Docker container recommended)

--------------------------------------------------------------------------------

# [ TC 1 ]: CLI Help and Version

- Priority: High
- Description: Verify CLI help system and version information
- Preconditions: Pyroform installed in test environment
- Validated by: [TAR TC_1](./TAR/TC_1.md)

## Test Steps:

1. Run version command
```bash
~$ pyroform --version
```
2. Run help commands
```bash
~$ pyroform --help
~$ pyroform snapshot --help
~$ pyroform configure --help
~$ pyroform scorch --help
~$ pyroform mount --help
~$ pyroform validate --help
~$ pyroform workflow --help
```

## Expected Results:

- Version displays correctly (e.g., "Pyroform version 1.0.0")
- Main help shows banner and available commands
- Each subcommand shows appropriate help text
- Banner displays correctly for all commands

--------------------------------------------------------------------------------

# [ TC 2 ]: Invalid CLI Usage

- Priority: High
- Description: Verify error handling for invalid CLI usage
- Preconditions: Pyroform installed in test environment
- Validated by: [TAR TC_2](./TAR/TC_2.md)

## Test Steps:

1. Run command with no arguments
```bash
~$ pyroform
~$ echo $?
```
2. Run command with invalid action
```bash
~$ pyroform invalid-command
~$ echo $?
```
3. Run command with invalid option flag
```bash
~$ pyroform configure --invalid-flag
~$ echo $?
```
4. Run incomplete command with no Pyro file
```bash
~$ pyroform configure
~$ echo $?
```
5. Run command with multiple actions
```
~$ pyroform configure scorch
~$ echo $?
```

## Expected Results:

- Appropriate error messages for invalid usage
- Clear guidance on correct usage
- Non-zero exit codes for errors

--------------------------------------------------------------------------------

# [ TC 3 ]: YAML Configuration Parsing

- Priority: High
- Description: Test YAML configuration file parsing
- Preconditions:
- Validated by: [TAR TC_3](./TAR/TC_3.md)

## Test Data (test_simple_config.pyro.yaml):
```yaml
Label: "Test Simple Configuration"
Users:
  - label: "test_user"
    Name: "testuser"
    Password: "test123"
    Groups: ["testgroup"]
Groups:
  - label: "test_group"
    Name: "testgroup"
    Users: ["testuser"]
Devices:
  - label: "test_device"
    Path: "/tmp/test_mount"
    Partition: 1
    Mountpoint: "/mnt/test"
    State: []
Excludes:
  Users:
    - root
    - daemon
    - bin
    - sys
    - sync
    - games
    - man
    - lp
    - mail
    - news
    - uucp
    - proxy
    - www-data
    - backup
    - list
    - irc
    - _apt
    - nobody
  Groups:
    - root
    - daemon
    - bin
    - sys
    - adm
    - tty
    - disk
    - lp
    - mail
    - news
    - uucp
    - man
    - proxy
    - kmem
    - dialout
    - fax
    - voice
    - cdrom
    - floppy
    - tape
    - sudo
    - audio
    - dip
    - www-data
    - backup
    - operator
    - list
    - irc
    - src
    - shadow
    - utmp
    - video
    - sasl
    - plugdev
    - staff
    - games
    - users
    - nogroup
    - _ssh
  Directories:
    - /app
    - /bin
    - /boot
    - /dev
    - /etc
    - /home
    - /lib
    - /lib64
    - /media
    - /mnt
    - /opt
    - /proc
    - /protected
    - /root
    - /run
    - /sbin
    - /srv
    - /sys
    - /usr
    - /var
```

## Test Steps:

1. Create test_simple_config.pyro.yaml with specified content
2. Run validation command
```bash
~$ pyroform validate -i test_simple_config.pyro.yaml
```
3. Run dry-run configuration command
```bash
~$ pyroform configure -i test_simple_config.pyro.yaml --dry-run
```

## Expected Results:

- YAML file parsed without errors
- Configuration object created correctly
- Dry-run completes successfully

--------------------------------------------------------------------------------

# [ TC 4 ]: JSON Configuration Parsing

- Priority: High
- Description: Test JSON configuration file parsing
- Preconditions:
- Validated by: [TAR TC_4](./TAR/TC_4.md)

## Test Data (test_simple_config.pyro.json):
```json
{
  "Label": "Test Simple Configuration",
  "Users": [
    {
      "label": "test_user",
      "Name": "testuser",
      "Password": "test123",
      "Groups": ["testgroup"]
    }
  ],
  "Groups": [
    {
      "label": "test_group",
      "Name": "testgroup",
      "Users": ["testuser"]
    }
  ],
  "Devices": [
    {
      "label": "test_device",
      "Path": "/tmp/test_mount",
      "Partition": 1,
      "Mountpoint": "/mnt/test",
      "State": []
    }
  ],
  "Excludes": {
    "Users": [
      "root",
      "daemon",
      "bin",
      "sys",
      "sync",
      "games",
      "man",
      "lp",
      "mail",
      "news",
      "uucp",
      "proxy",
      "www-data",
      "backup",
      "list",
      "irc",
      "_apt",
      "nobody"
    ],
    "Groups": [
      "root",
      "daemon",
      "bin",
      "sys",
      "adm",
      "tty",
      "disk",
      "lp",
      "mail",
      "news",
      "uucp",
      "man",
      "proxy",
      "kmem",
      "dialout",
      "fax",
      "voice",
      "cdrom",
      "floppy",
      "tape",
      "sudo",
      "audio",
      "dip",
      "www-data",
      "backup",
      "operator",
      "list",
      "irc",
      "src",
      "shadow",
      "utmp",
      "video",
      "sasl",
      "plugdev",
      "staff",
      "games",
      "users",
      "nogroup",
      "_ssh"
    ],
    "Directories": [
      "/app",
      "/bin",
      "/boot",
      "/dev",
      "/etc",
      "/home",
      "/lib",
      "/lib64",
      "/media",
      "/mnt",
      "/opt",
      "/proc",
      "/protected",
      "/root",
      "/run",
      "/sbin",
      "/srv",
      "/sys",
      "/usr",
      "/var"
    ]
  }
}
```

## Test Steps:

1. Create test_config.pyro.json with above content
2. Run validation command
```bash
~$ pyroform validate -i test_config.pyro.json
```
3. Run configuration command with dry-run flag
```bash
~$ pyroform configure -i test_config.pyro.json --dry-run
```

## Expected Results:

- JSON file parsed without errors
- Configuration object created correctly
- Dry-run completes successfully

--------------------------------------------------------------------------------

# [ TC 5 ]: Invalid Configuration Files

- Priority: Medium
- Description: Test error handling for invalid configuration files
- Preconditions:
- Validated by: [TAR TC_5](./TAR/TC_5.md)

## Test Data:

### Pyro file with invalid JSON syntax (invalid_syntax.pyro.json)
```json
{
  "Label": "Test Invalid JSON Syntax Configuration",
  "Users": [
    {
      "label": "json_user",
      "Name": "jsonuser",
      "Password": "json123",
      "Groups": ["jsongroup"],
    }
  ],
  "Groups": [
    {
      "label": "json_group",
      "Name": "jsongroup",
      "Users": ["jsonuser"],
    }
  ],
  "Devices": []
}
```

### Pyro file with invalid YAML syntax (invalid_syntax.pyro.yaml)
```yaml
Label: "Test Invalid YAML Syntax Configuration"
Users:
  - label: "test_user"
    Name: "testuser"
    Password: "test123"
    Groups: ["testgroup"]
Groups
  - label: "test_group"
    Name: "testgroup"
    Users: ["testuser"]
Devices:
  - label "test_device"
    Path: "/tmp/test_mount"
    Partition: 1
    Mountpoint: "/mnt/test"
    State: []
```

### Pyro file with missing required fields (missing_fields.pyro.yaml)
```yaml
Label: "Test Missing Fields YAML Configuration"
Users:
  - label: "test_user"
    Password: "test123"
    Groups: ["testgroup"]
Groups:
    Name: "testgroup"
    Users: ["testuser"]
Devices:
  - label: "test_device"
    Path: "/tmp/test_mount"
    Partition: 1
    Mountpoint: "/mnt/test"
```

### Pyro file with invalid field types (invalid_fields.pyro.yaml)
```yaml
Label: "Test Invalid Fields YAML Configuration"
Users:
  - label: "test_user"
    Name: "testuser"
    Password: true
    Groups: ["testgroup"]
Groups:
  - label: "test_group"
    Name: "testgroup"
    Users: false
Devices:
  - label: "test_device"
    Path: "/tmp/test_mount"
    Partition: 1
    Mountpoint: "/mnt/test"
    State: 123
```

## Test Steps:

1. Create file with invalid YAML syntax (invalid_syntax.pyro.yaml)
2. Create file with invalid JSON syntax (invalid_syntax.pyro.json)
3. Create file missing required fields  (missing_fields.pyro.yaml)
4. Create file with invalid field types (invalid_fields.pyro.yaml)
5. Attempt to parse each with pyroform validate commands
```bash
~$ pyroform validate -i invalid_syntax.pyro.yaml
~$ pyroform validate -i invalid_syntax.pyro.json
~$ pyroform validate -i missing_fields.pyro.yaml
~$ pyroform validate -i invalid_fields.pyro.yaml
```

## Expected Results:

- Clear error messages for syntax errors
- Validation fails for missing required fields
- Type errors reported appropriately

--------------------------------------------------------------------------------

# [ TC 6 ]: User Creation (Dry Run)

- Priority: High
- Description: Test user creation in dry-run mode
- Preconditions:
- Validated by: [TAR TC_6](./TAR/TC_6.md)

## Test Data (users_test.pyro.yaml):
```yaml
Label: "User Management Test"
Users:
  - label: "test_user_1"
    Name: "pyrotest1"
    Password: "testpass1"
    Groups: ["pyrogroup1"]
  - label: "test_user_2"
    Name: "pyrotest2"
    Password: "testpass2"
    Groups: ["pyrogroup1", "pyrogroup2"]
Groups:
  - label: "group_1"
    Name: "pyrogroup1"
    Users: ["pyrotest1", "pyrotest2"]
  - label: "group_2"
    Name: "pyrogroup2"
    Users: ["pyrotest2"]
Excludes:
  Users:
    - root
    - daemon
    - bin
    - sys
    - sync
    - games
    - man
    - lp
    - mail
    - news
    - uucp
    - proxy
    - www-data
    - backup
    - list
    - irc
    - _apt
    - nobody
  Groups:
    - root
    - daemon
    - bin
    - sys
    - adm
    - tty
    - disk
    - lp
    - mail
    - news
    - uucp
    - man
    - proxy
    - kmem
    - dialout
    - fax
    - voice
    - cdrom
    - floppy
    - tape
    - sudo
    - audio
    - dip
    - www-data
    - backup
    - operator
    - list
    - irc
    - src
    - shadow
    - utmp
    - video
    - sasl
    - plugdev
    - staff
    - games
    - users
    - nogroup
    - _ssh
```

## Test Steps:

1. Create Pyro file with content specified in test data (users_test.pyro.yaml)
2. Verify users don't exist:
```bash
~$ id pyrotest1; id pyrotest2
```
3. Run command
```bash
~$ pyroform configure -i users_test.pyro.yaml --dry-run
```
4. Check output for planned user/group operations
5. Verify users still don't exist after dry-run
```bash
~$ id pyrotest1; id pyrotest2
```

## Expected Results:

- Dry-run shows planned user/group creation
- No actual users/groups created on system
- Verbose output shows detailed planning

--------------------------------------------------------------------------------

# [ TC 7 ]: Actual User Creation

- Priority: High
- Description: Test actual user and group creation
- Preconditions:
    - Pyro file `users_test.pyro.yaml` created during execution of [TC_6](./TAR/TC_6.md);
    - Test users don't exist on system;
- Validated by: [TAR TC_7](./TAR/TC_7.md)

## Test Steps:

1. Run configure command (auto-confirm)
```bash
~$ pyroform configure -i users_test.pyro.yaml -y
```
2. Verify users created:
```bash
~$ id pyrotest1; id pyrotest2
```
3. Verify groups created:
```bash
~$ getent group pyrogroup1; getent group pyrogroup2
```
4. Verify group membership:
```bash
~$ groups pyrotest1; groups pyrotest2
```
5. Cleanup:
```bash
~$ userdel -r pyrotest1; userdel -r pyrotest2
~$ groupdel pyrogroup1; groupdel pyrogroup2; echo $?
```

## Expected Results:

- Users created with correct names
- Groups created and users added to them
- Home directories created
- Clean removal possible

--------------------------------------------------------------------------------

# [ TC 8 ]: Directory Structure Creation

- Priority: High
- Description: Test directory creation and permission setting
- Preconditions: Users from previous test exist
- Validated by: [TAR TC_8](./TAR/TC_8.md)

## Test Data (fs_test.pyro.yaml):
```yaml
Label: "Filesystem Test Without Block Device Path"
Devices:
  - label: "test_fs"
    Path: ""
    Partition: 0
    Mountpoint: "/tmp/pyrotest"
    State:
      - "dir,/tmp/pyrotest,root,root,755"
      - "dir,/tmp/pyrotest/data,pyrotest1,pyrogroup1,750"
      - "dir,/tmp/pyrotest/logs,root,pyrogroup1,775"
      - "fl,/tmp/pyrotest/README,pyrotest1,pyrogroup1,644"
      - "ln,/tmp/pyrotest/readme_shortcut,pyrotest1,pyrogroup1,777,/tmp/pyrotest/README"
Excludes:
  Directories:
    - /app
    - /bin
    - /boot
    - /dev
    - /etc
    - /home
    - /lib
    - /lib64
    - /media
    - /mnt
    - /opt
    - /proc
    - /protected
    - /root
    - /run
    - /sbin
    - /srv
    - /sys
    - /usr
    - /var
```

## Test Steps:

1. Create Pyro file with content from test data (fs_test.pyro.yaml)
```bash
~$ vim fs_test.pyro.yaml
```
2. Run configure command with dry-run option flag
```bash
~$ pyroform configure -i fs_test.pyro.yaml --dry-run
```
3. Run configure command (auto-confirm)
```bash
~$ pyroform configure -i fs_test.pyro.yaml -y
```
4. Verify created directory structure
```bash
~$ tree /tmp/pyrotest
```
5. Verify ownership and permissions
```bash
~$ ls -allah /tmp/pyrotest
```
6. Clean up
```bash
~$ rm -rf /tmp/pyrotest; echo $?
```

## Expected Results:

- Directories created with correct paths
- Ownership set correctly (user:group)
- Permissions set as specified
- File placeholder created

--------------------------------------------------------------------------------

# [ TC 9 ]: Scorch Dry Run

- Priority: High
- Description: Test scorch operation in dry-run mode
- Preconditions: System has some test users/groups/files not in config
- Validated by: [TAR TC_9](./TAR/TC_9.md)

## Test Data (full_system.pyro.yaml)
```yaml
Label: "Full System Management Test"
Users:
  - label: "test_user_1"
    Name: "pyrotest1"
    Password: "testpass1"
    Groups: ["pyrogroup1"]
  - label: "test_user_2"
    Name: "pyrotest2"
    Password: "testpass2"
    Groups: ["pyrogroup1", "pyrogroup2"]
Groups:
  - label: "group_1"
    Name: "pyrogroup1"
    Users: ["pyrotest1", "pyrotest2"]
  - label: "group_2"
    Name: "pyrogroup2"
    Users: ["pyrotest2"]
Devices:
  - label: "Primary Storage"
    Path: "/dev/sda"
    Partition: 1
    Mountpoint: "/tmp/pyrotest"
    State:
      - "dir,/tmp/pyrotest,root,root,755"
      - "dir,/tmp/pyrotest/data,pyrotest1,pyrogroup1,750"
      - "dir,/tmp/pyrotest/logs,root,pyrogroup1,775"
      - "fl,/tmp/pyrotest/README,pyrotest1,pyrogroup1,644"
      - "ln,/tmp/pyrotest/readme_shortcut,pyrotest1,pyrogroup1,777,/tmp/pyrotest/README"
Excludes:
  Directories:
    - /app
    - /bin
    - /boot
    - /dev
    - /etc
    - /home
    - /lib
    - /lib64
    - /media
    - /mnt
    - /opt
    - /proc
    - /protected
    - /root
    - /run
    - /sbin
    - /srv
    - /sys
    - /usr
    - /var
```

## Test Steps:

1. Create Pyro file full_system.pyro.yaml with content from test data
```bash
~$ vim full_system.pyro.yaml
```
2. Create extra user:
```bash
~$ useradd scorchtest; echo $?
```
3. Create extra file:
```bash
~$ touch /tmp/shall_not_be_scorched.dummy; echo $?
```
4. Dry run scorch command
```bash
~$ pyroform scorch -i full_system.pyro.yaml --dry-run
```
5. Review what would be removed
6. Verify nothing actually removed
```
~$ id scorchtest
~$ ls -allah /tmp/shall_not_be_scorched.dummy
```

## Expected Results:

- Dry-run shows orphaned resources
- No actual removal occurs
- Clear indication of dry-run mode

--------------------------------------------------------------------------------

# [ TC 10 ]: Scorch Safety Prompts

- Priority: High
- Description: Test scorch safety confirmation
- Preconditions:
- Validated by: [TAR TC_10](./TAR/TC_10.md)

## Test data (scorch_user.pyro.yaml)
```yaml
Label: User Scorch Test
Users:
  - label: test_user_1
    Name: pyrotest1
    Password: testpass1
    Groups:
      - pyrogroup1
  - label: test_user_2
    Name: pyrotest2
    Password: testpass2
    Groups:
      - pyrogroup1
      - pyrogroup2
Excludes:
  Users:
    - root
    - daemon
    - bin
    - sys
    - sync
    - games
    - man
    - lp
    - mail
    - news
    - uucp
    - proxy
    - www-data
    - backup
    - list
    - irc
    - _apt
    - nobody
```

## Test Steps:

1. Create Pyro file with content presented in test data (scorch_user.pyro.yaml)
```bash
~$ vim scorch_user.pyro.yaml
```
2. Create orphaned user:
```bash
~$ useradd scorchtest; echo $?
```
3. Run command (no auto-confirm)
```bash
~$ pyroform scorch -i scorch_user.pyro.yaml
# When prompted, answer "n|no|N|NO"
```
4. Verify user still exists
```bash
~$ id scorchtest
```
5. Run with -y flag
```bash
~$ pyroform scorch -i scorch_user.pyro.yaml -y
```
6. Verify user removed
```bash
~$ id scorchtest
```

## Expected Results:

- Safety prompt displayed for destructive operation
- Operation aborted when user declines
- Operation proceeds when auto-confirmed

--------------------------------------------------------------------------------

# [ TC 11 ]: System Validation

- Priority: High
- Description: Test system validation against current state
- Preconditions:
- Validated by: [TAR TC_11](./TAR/TC_11.md)

## Test data (validate_user.pyro.yaml)
```yaml
Label: "System User Validation Test"
Users:
  - label: "test_user_1"
    Name: "pyrotest1"
    Password: "testpass1"
    Groups: ["pyrogroup1"]
  - label: "test_user_2"
    Name: "pyrotest2"
    Password: "testpass2"
    Groups: ["pyrogroup2"]
Groups:
  - label: "group_1"
    Name: "pyrogroup1"
    Users: ["pyrotest1"]
  - label: "group_2"
    Name: "pyrogroup2"
    Users: ["pyrotest2"]
  - label: "group_3"
    Name: "pyrotest1"
    Users: ["pyrotest1"]
  - label: "group_4"
    Name: "pyrotest2"
    Users: ["pyrotest2"]
Excludes:
  Users:
    - root
    - daemon
    - bin
    - sys
    - sync
    - games
    - man
    - lp
    - mail
    - news
    - uucp
    - proxy
    - www-data
    - backup
    - list
    - irc
    - _apt
    - nobody
  Groups:
    - root
    - daemon
    - bin
    - sys
    - adm
    - tty
    - disk
    - lp
    - mail
    - news
    - uucp
    - man
    - proxy
    - kmem
    - dialout
    - fax
    - voice
    - cdrom
    - floppy
    - tape
    - sudo
    - audio
    - dip
    - www-data
    - backup
    - operator
    - list
    - irc
    - src
    - shadow
    - utmp
    - video
    - sasl
    - plugdev
    - staff
    - games
    - users
    - nogroup
    - _ssh
```

## Test Steps:

1. Create Pyro file with content from test data
```bash
~$ vim validate_user.pyro.yaml
```
2. Configure system with known state
```bash
~$ pyroform configure -i validate_user.pyro.yaml
```
3. Run validate command. Verify validation passes (no discrepancies)
```bash
~$ pyroform validate -i validate_user.pyro.yaml
```
4. Make intentional changes to break configuration
```bash
~$ useradd intruder; echo $?
```
5. Run validation again, verify failures detected
```bash
~$ pyroform validate -i validate_user.pyro.yaml
```

## Expected Results:

- Validation passes when system matches config
- Validation fails with specific discrepancies
- Clear reporting of what's wrong

--------------------------------------------------------------------------------

# [ TC 12 ]: Multi-step Workflow

- Priority: Medium
- Description: Test complete workflow execution
- Preconditions:
- Validated by: [TAR TC_12](./TAR/TC_12.md)

## Test Data

### workflow_step.pyro.yaml:
```yaml
Label: "System User Validation Test"
Users:
  - label: "test_user_1"
    Name: "pyrotest1"
    Password: "testpass1"
    Groups: ["pyrogroup1"]
  - label: "test_user_2"
    Name: "pyrotest2"
    Password: "testpass2"
    Groups: ["pyrogroup2"]
Groups:
  - label: "group_1"
    Name: "pyrogroup1"
    Users: ["pyrotest1"]
  - label: "group_2"
    Name: "pyrogroup2"
    Users: ["pyrotest2"]
  - label: "group_3"
    Name: "pyrotest1"
    Users: ["pyrotest1"]
  - label: "group_4"
    Name: "pyrotest2"
    Users: ["pyrotest2"]
Excludes:
  Users:
    - root
    - daemon
    - bin
    - sys
    - sync
    - games
    - man
    - lp
    - mail
    - news
    - uucp
    - proxy
    - www-data
    - backup
    - list
    - irc
    - _apt
    - nobody
  Groups:
    - root
    - daemon
    - bin
    - sys
    - adm
    - tty
    - disk
    - lp
    - mail
    - news
    - uucp
    - man
    - proxy
    - kmem
    - dialout
    - fax
    - voice
    - cdrom
    - floppy
    - tape
    - sudo
    - audio
    - dip
    - www-data
    - backup
    - operator
    - list
    - irc
    - src
    - shadow
    - utmp
    - video
    - sasl
    - plugdev
    - staff
    - games
    - users
    - nogroup
    - _ssh
```

### workflow_test.pyro.yaml:
```yaml
name: "Test Multi-Step Workflow"
description: "Complete test workflow"
auto_confirm: true

steps:
  - name: "Initial Validation"
    action: "validate"
    input_path: "workflow_step.pyro.yaml"
    dry_run: false

  - name: "Machine State Snapshot"
    action: "snapshot"
    input_path: "workflow_step.pyro.yaml"
    output_path: "workflow_snapshot.pyro.yaml"
    dry_run: false

  - name: "Mock Pyroform Machine"
    action: "configure"
    input_path: "workflow_step.pyro.yaml"
    dry_run: true

  - name: "Pyroform Machine"
    action: "configure"
    input_path: "workflow_step.pyro.yaml"
    dry_run: false

  - name: "Final Validation"
    action: "validate"
    input_path: "workflow_step.pyro.yaml"
    dry_run: false
```

## Test Steps:

1. Create Pyro files with content from test data:
- workflow_test.pyro.yaml
- workflow_step.pyro.yaml
2. Run command
```bash
~$ pyroform workflow -w workflow_test.pyro.yaml
```
3. Observe step-by-step execution and verify all steps complete successfully
5. Check generated report..?

## Expected Results:

- Workflow executes all steps in order
- Dry-run and actual steps handled correctly
- Report generated with workflow results

--------------------------------------------------------------------------------

# [ TC 13 ]: # Tooling Configuration Via YAML Files

- Priority: Medium
- Description: Test tooling is configurable via YAML config file but overwritten by CLI options
- Preconditions:
- Validated by: [TAR TC_13](./TAR/TC_13.md)

## Test Data:

### pyroform.conf.yaml
```yaml
log_level: 'INFO'
log_file: '/tmp/pyroform.log'
auto_confirm: false
dry_run: false
report: false
cleanup: true
```

### pyroform_devel.conf.yaml
```yaml
log_level: 'DEBUG'
log_file: 'pyroform.log'
auto_confirm: true
dry_run: true
report: true
cleanup: false
```

### dummy.pyro.yaml
```yaml
Label: "Dummy User Validation Test"
Users:
  - label: "Big Guy"
    Name: "root"
    Password: "toor"
    Groups: []
Excludes:
  Users:
    - root
    - daemon
    - bin
    - sys
    - sync
    - games
    - man
    - lp
    - mail
    - news
    - uucp
    - proxy
    - www-data
    - backup
    - list
    - irc
    - _apt
    - nobody
```

## Test Steps:

1. Create YAML config files with contents specified in test data
```bash
~$ vim pyroform.conf.yaml pyroform_devel.conf.yaml
```
2. Create YAML Pyro file with contents specified in test data
```bash
~$ vim dummy.pyro.yaml
```

3. Run validation command with default config file
```bash
~$ pyroform validate -i dummy.pyro.yaml --config-file pyroform.conf.yaml
```
4. Check logging level is INFO

5. Run Pyro validation command with development config file
```bash
~$ pyroform validate -i dummy.pyro.yaml --config-file pyroform_devel.conf.yaml
```
6. Check logging level is DEBUG

7. Run Pyro scorch dry-run command with development config file (no --dry-run CLI option)
```bash
~$ pyroform scorch -i dummy.pyro.yaml --config-file pyroform_devel.conf.yaml
```
8. Check auto_confirm without passing (--yes) option
9. Check dry_run without passing (--dry-run) option
10. Check report generated without passing (--dump-report) option
11. Check log file location dictated by config file without passing (--log-file) option

12. Run Pyro scorch dry-run command with CLI options overriding config file settings
```bash
~$ pyroform scorch -i dummy.pyro.yaml --config-file pyroform.conf.yaml --dry-run --yes --log-file test_pyroform.log --debug --dump-report
```
13. Check auto_confirm flag set with CLI option --yes overriding config file
14. Check dry_run flag set with CLI option --dry-run overriding config file
15. Check report generation flag set with CLI option --dump-report overriding config file
16. Check log file location dictated by CLI option --log-file overriding config file
17. Check log level set to DEBUG by CLI option --debug overriding config file

## Expected Results:

- Logging level controlled by config file but overwritten by CLI arg
- Log file path controlled by config file but overwritten by CLI arg
- Auto confirm controlled by config file but overwritten by CLI arg
- Dry run controlled by config file but overwritten by CLI arg
- Report generation controlled by config file but overwritten by CLI arg

--------------------------------------------------------------------------------

# [ Conclusion ]: 

