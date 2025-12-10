# Directory Structure Creation
- Priority: High
- Description: Test directory creation and permission setting
- Preconditions: Users from previous test exist
- Validated by: [TAR TC_8](../TAR/TC_8.md)

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
