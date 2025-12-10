# Scorch Dry Run
- Priority: High
- Description: Test scorch operation in dry-run mode
- Preconditions: System has some test users/groups/files not in config
- Validated by: [TAR TC_9](../TAR/TC_9.md)

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
