# User Creation (Dry Run)
- Priority: High
- Description: Test user creation in dry-run mode
- Preconditions:
- Validated by: [TAR TC_6](../TAR/TC_6.md)

## Test Data (users_test.yaml):
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

## Test Steps:

1. Verify users don't exist:
```bash
~$ id pyrotest1 && id pyrotest2
```
2. Run command
```bash
~$ pyroform configure -i users_test.yaml --dry-run -v
```
3. Check output for planned user/group operations
4. Verify users still don't exist after dry-run

## Expected Results:

- Dry-run shows planned user/group creation
- No actual users/groups created on system
- Verbose output shows detailed planning
