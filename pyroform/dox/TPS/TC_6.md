# User Creation (Dry Run)
- Priority: High
- Description: Test user creation in dry-run mode
- Preconditions:
- Validated by: [TAR TC_6](../TAR/TC_6.md)

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
