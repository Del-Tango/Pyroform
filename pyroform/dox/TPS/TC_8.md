# Directory Structure Creation
- Priority: High
- Description: Test directory creation and permission setting
- Preconditions: Users from previous test exist
- Validated by: [TAR TC_8](../TAR/TC_8.md)

## Test Data (fs_test.yaml):
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

## Test Steps:

1. Run commands
```bash
~$ pyroform configure -i fs_test.yaml --dry-run
~$ pyroform configure -i fs_test.yaml -y
```
2. Verify directory structure created
3. Verify ownership and permissions
4. Clean up
```bash
~$ rm -rf /tmp/pyrotest
```

## Expected Results:

- Directories created with correct paths
- Ownership set correctly (user:group)
- Permissions set as specified
- File placeholder created
