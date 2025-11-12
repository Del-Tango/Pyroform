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
~$ pyroform --configure --scorch
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

## Test Data (test_config.pyro.yaml):
```yaml
Label: "Test Configuration"
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
```

## Test Steps:

1. Create test_config.yaml with above content and run commands
2. Run validation command
```bash
~$ pyroform validate -i test_config.yaml
```
3. Run dry-run configuration command
```bash
~$ pyroform configure -i test_config.yaml --dry-run
```

## Expected Results:

- YAML file parsed without errors
- Configuration object created correctly
- Dry-run completes successfully

--------------------------------------------------------------------------------

# [ TC 4 ]: ID: TC-4 / JSON Configuration Parsing

Priority: High
Description: Test JSON configuration file parsing
Preconditions:

Test Data (test_config.json):
```json
{
  "Label": "Test JSON Config",
  "Users": [
    {
      "label": "json_user",
      "Name": "jsonuser",
      "Password": "json123",
      "Groups": ["jsongroup"]
    }
  ],
  "Groups": [
    {
      "label": "json_group",
      "Name": "jsongroup",
      "Users": ["jsonuser"]
    }
  ],
  "Devices": []
}
```

Test Steps:

1. Create test_config.json with above content
2. Run commands
```bash
~$ pyroform validate -i test_config.json
~$ pyroform configure -i test_config.json --dry-run
```

Expected Results:

- JSON file parsed without errors
- Configuration object created correctly
- Dry-run completes successfully

--------------------------------------------------------------------------------

# [ TC 5 ]: ID: TC-5 / Invalid Configuration Files

Priority: Medium
Description: Test error handling for invalid configuration files
Preconditions:

Test Steps:

1. Create file with invalid YAML syntax
2. Create file with invalid JSON syntax
3. Create file missing required fields
4. Create file with invalid field types
5. Attempt to parse each with pyroform validate
```bash
~$ pyroform validate -i test_invalid.pyro.yaml
```

Expected Results:

- Clear error messages for syntax errors
- Validation fails for missing required fields
- Type errors reported appropriately

--------------------------------------------------------------------------------

# [ TC 6 ]: ID: TC-6 / User Creation (Dry Run)

Priority: High
Description: Test user creation in dry-run mode
Preconditions:

Test Data (users_test.yaml):
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
```

Test Steps:

1. Verify users don't exist: id pyrotest1 && id pyrotest2
2. Run command
```bash
~$ pyroform configure -i users_test.yaml --dry-run -v
```
3. Check output for planned user/group operations
4. Verify users still don't exist after dry-run

Expected Results:

- Dry-run shows planned user/group creation
- No actual users/groups created on system
- Verbose output shows detailed planning

--------------------------------------------------------------------------------

# [ TC 7 ]: ID: TC-7 / Actual User Creation

Priority: High
Description: Test actual user and group creation
Preconditions: Test users don't exist on system

Test Steps:

1. Run command
```bash
~$ pyroform configure -i users_test.yaml -y (auto-confirm)
```
2. Verify users created: id pyrotest1 && id pyrotest2
3. Verify groups created: getent group pyrogroup1 && getent group pyrogroup2
4. Verify group membership: groups pyrotest1 && groups pyrotest2
5. Clean up:
```bash
~$ userdel -r pyrotest1 && userdel -r pyrotest2
```

Expected Results:

- Users created with correct names
- Groups created and users added to them
- Home directories created
- Clean removal possible

--------------------------------------------------------------------------------

# [ TC 8 ]: ID: TC-8 / Directory Structure Creation

Priority: High
Description: Test directory creation and permission setting
Preconditions: Users from previous test exist

Test Data (fs_test.yaml):
```yaml
Label: "Filesystem Test"
Devices:
  - label: "test_fs"
    Path: "none"
    Partition: 0
    Mountpoint: "/tmp/pyrotest"
    State:
      - "dir,/tmp/pyrotest,root,root,755"
      - "dir,/tmp/pyrotest/data,pyrotest1,pyrogroup1,750"
      - "dir,/tmp/pyrotest/logs,root,pyrogroup1,775"
      - "fl,/tmp/pyrotest/README,pyrotest1,pyrogroup1,644"
```

Test Steps:

1. Run commands
```bash
pyroform configure -i fs_test.yaml --dry-run
pyroform configure -i fs_test.yaml -y
```
2. Verify directory structure created
3. Verify ownership and permissions
4. Clean up
```bash
~$ rm -rf /tmp/pyrotest
```

Expected Results:

- Directories created with correct paths
- Ownership set correctly (user:group)
- Permissions set as specified
- File placeholder created

--------------------------------------------------------------------------------

# [ TC 9 ]: ID: TC-9 / Scorch Dry Run

Priority: High
Description: Test scorch operation in dry-run mode
Preconditions: System has some test users/files not in config

Test Steps:

1. Create orphaned user:
```bash
~$ useradd scorchtest
```
2. Create orphaned file:
```bash
~$ touch /tmp/orphaned.file
```
3. Run commands
```bash
~$ pyroform scorch -i minimal_config.yaml --dry-run -v
```
4. Review what would be removed
5. Verify nothing actually removed

Expected Results:

- Dry-run shows orphaned resources
- No actual removal occurs
- Clear indication of dry-run mode

--------------------------------------------------------------------------------

# [ TC 10 ]: ID: TC-10 / Scorch Safety Prompts

Priority: High
Description: Test scorch safety confirmation
Preconditions:

Test Steps:

1. Create orphaned user:
```bash
~$ useradd scorchtest2
```
2. Run command
```bash
~$ pyroform scorch -i minimal_config.yaml (no auto-confirm)
# When prompted, answer "no"
```
3. Verify user still exists
4. Run with -y flag
```bash
~$ pyroform scorch -i minimal_config.yaml -y
```
5. Verify user removed

Expected Results:

- Safety prompt displayed for destructive operation
- Operation aborted when user declines
- Operation proceeds when auto-confirmed

--------------------------------------------------------------------------------

# [ TC 11 ]: ID: TC-11 / System Validation

Priority: High
Description: Test system validation against current state
Preconditions:

Test Steps:

1. Configure system with known state
2. Run command
```bash
~$ pyroform validate -i known_state.yaml
```
3. Verify validation passes (no discrepancies)
4. Make intentional changes to break configuration
5. Run validation again, verify failures detected

Expected Results:

- Validation passes when system matches config
- Validation fails with specific discrepancies
- Clear reporting of what's wrong

--------------------------------------------------------------------------------

# [ TC 12 ]: ID: TC-12 / Multi-step Workflow

Priority: Medium
Description: Test complete workflow execution
Preconditions:

Test Data (workflow_test.yaml):
```yaml
name: "Test Workflow"
description: "Complete test workflow"
auto_confirm: true

steps:
  - name: "Initial Validation"
    action: "validate"
    input_path: "workflow_config.yaml"
    dry_run: true

  - name: "Create Structure"
    action: "configure"
    input_path: "workflow_config.yaml"
    dry_run: false

  - name: "Final Validation"
    action: "validate"
    input_path: "workflow_config.yaml"
    dry_run: false
```

Test Steps:

1. Create workflow configuration file
2. Run command
```bash
~$ pyroform workflow -w workflow_test.yaml
```
3. Observe step-by-step execution
4. Verify all steps complete successfully
5. Check generated report

Expected Results:

- Workflow executes all steps in order
- Dry-run and actual steps handled correctly
- Report generated with workflow results

--------------------------------------------------------------------------------

# [ TC 13 ]: ID: TC-13 / Permission Denied Handling

Priority: High
Description: Test error handling for permission issues
Preconditions:

Test Steps:

1. Create config that tries to modify system directories
2. Run as non-root user
3. Attempt operations that require elevated privileges
4. Verify graceful error handling

Expected Results:

- Clear error messages for permission issues
- Operations fail gracefully without system damage
- Appropriate exit codes

--------------------------------------------------------------------------------

# [ TC 14 ]: ID: TC-14 / Invalid Command Prevention

Priority: High
Description: Test prevention of dangerous commands
Preconditions:

Test Steps:

1. Create config with forbidden commands in device state
2. Attempt to execute configuration
3. Verify dangerous commands are blocked

Expected Results:

- Forbidden commands detected and blocked
- Clear warning messages
- Operation fails safely

--------------------------------------------------------------------------------

# [ TC 15 ]: ID: TC-15 / Report Generation

Priority: Medium
Description: Test report generation in various formats
Preconditions:

Test Steps:

1. Run any action with --dump-report flag
2. Verify report file created
3. Check report content for completeness
4. Test JSON and YAML report formats
5. Verify report includes timing information

Expected Results:

- Report files created in specified location
- Reports contain action details and results
- Timing information included
- Both JSON and YAML formats supported

--------------------------------------------------------------------------------

# [ TC 16 ]: ID: TC-16 / System Cleanup

Priority: High
Description: Verify complete cleanup after testing
Preconditions:

Test Steps:

1. List all test resources created during testing
2. Execute cleanup procedures
3. Verify system returned to original state
4. Check for any leftover files, users, or groups

Expected Results:

- All test users removed
- All test groups removed
- All test files/directories removed
- System state restored

--------------------------------------------------------------------------------

# [ Conclusion ]: 

