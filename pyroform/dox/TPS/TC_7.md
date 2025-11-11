ID: TC-7 / Actual User Creation
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
