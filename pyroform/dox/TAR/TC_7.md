# Actual User Creation
- Test Environment: Docker container with Debian GNU/Linux 13 (trixie) 6.6.15-amd64
- Tester: D:Ta
- Date: 17/11/2025
- Pyroform Version: 1.0.0
- Validates: [TPS TC_7](../TPS/TC_7.md)
- Preconditions: users_test.pyro.yaml file from TC_6 available
- Status:
[X] PASS
[ ] FAIL
[ ] BLOCKED

# Archive

## 1. Run configure command (auto-confirm)
```text
    root@1e1b62138bef:/app/Pyroform# pyroform configure -i users_test.pyro.yaml -y

        ___________________________________________________________________________

          *                          *   Pyroform   *                           *
        ___________________________________________________________________________
                        Regards, the Alveare Solutions #!/Society -x


    [ INFO ]: Logging configured: /usr/local/lib/python3.13/dist-packages/log/pyroflow/pyroflow.log
    [ INFO ]: State monitoring configured for inter-process control
    [ INFO ]: Parsing Pyro state file (users_test.pyro.yaml)...
    [ INFO ]: State file data: {
        "Label": "User Management Test",
        "Users": [
            {
                "label": "test_user_1",
                "Name": "pyrotest1",
                "Password": "testpass1",
                "Groups": [
                    "pyrogroup1"
                ]
            },
            {
                "label": "test_user_2",
                "Name": "pyrotest2",
                "Password": "testpass2",
                "Groups": [
                    "pyrogroup1",
                    "pyrogroup2"
                ]
            }
        ],
        "Groups": [
            {
                "label": "group_1",
                "Name": "pyrogroup1",
                "Users": [
                    "pyrotest1",
                    "pyrotest2"
                ]
            },
            {
                "label": "group_2",
                "Name": "pyrogroup2",
                "Users": [
                    "pyrotest2"
                ]
            }
        ]
    }
    [ INFO ]: FlowCTRL Sketch {
        "name": "Pyroform Auto-Generated Sketch User Management Test",
        "Users": [
            {
                "name": "Creating System User pyrotest1",
                "cmd": " for group in pyrogroup1; do groupadd -f $group; done && useradd -m -p 'testpass1' -G 'pyrogroup1' 'pyrotest1' || exit 0",
                "setup-cmd": "id pyrotest1 && echo 'User pyrotest1 already exists' || exit 0",
                "teardown-cmd": "",
                "on-ok-cmd": "echo 'User pyrotest1 exists or created successfully'",
                "on-nok-cmd": "echo 'Failed to create user pyrotest1'",
                "fatal-nok": false
            },
            {
                "name": "Creating System User pyrotest2",
                "cmd": " for group in pyrogroup1 pyrogroup2; do groupadd -f $group; done && useradd -m -p 'testpass2' -G 'pyrogroup1,pyrogroup2' 'pyrotest2' || exit 0",
                "setup-cmd": "id pyrotest2 && echo 'User pyrotest2 already exists' || exit 0",
                "teardown-cmd": "",
                "on-ok-cmd": "echo 'User pyrotest2 exists or created successfully'",
                "on-nok-cmd": "echo 'Failed to create user pyrotest2'",
                "fatal-nok": false
            }
        ],
        "Groups": [
            {
                "name": "Creating System Group pyrogroup1",
                "cmd": " groupadd -f 'pyrogroup1' && for user in pyrotest1 pyrotest2; do id $user || useradd -m $user; usermod -a -G 'pyrogroup1' $user; done",
                "setup-cmd": "getent group pyrogroup1 && echo 'Group pyrogroup1 already exists' || exit 0",
                "teardown-cmd": "",
                "on-ok-cmd": "echo 'Group pyrogroup1 exists'",
                "on-nok-cmd": "echo 'Failed to create group pyrogroup1'",
                "fatal-nok": false
            },
            {
                "name": "Creating System Group pyrogroup2",
                "cmd": " groupadd -f 'pyrogroup2' && for user in pyrotest2; do id $user || useradd -m $user; usermod -a -G 'pyrogroup2' $user; done",
                "setup-cmd": "getent group pyrogroup2 && echo 'Group pyrogroup2 already exists' || exit 0",
                "teardown-cmd": "",
                "on-ok-cmd": "echo 'Group pyrogroup2 exists'",
                "on-nok-cmd": "echo 'Failed to create group pyrogroup2'",
                "fatal-nok": false
            }
        ]
    }
    [ INFO ]: Purging all state and report data
    [ OK ]: All data purged
    [ INFO ]: Loading sketch file: pyroflow.sketch.json
    [ OK ]: Loaded procedure: Pyroform Auto-Generated Sketch User Management Test
    [ INFO ]: Starting procedure execution with state monitoring
    [ INFO ]: Procedure state set to STARTED
    [ INFO ]: State monitoring active - process can be controlled externally
    [ INFO ]: Beginning controlled procedure execution...
    [ INFO ]: Processing stage: Users
    [ INFO ]: Processing action: Creating System User pyrotest1
    [ INFO ]: Executing Procedure Stage Action: Creating System User pyrotest1
    CMD> id pyrotest1 && echo 'User pyrotest1 already exists' || exit 0


    CMD>  for group in pyrogroup1; do groupadd -f $group; done && useradd -m -p 'testpass1' -G 'pyrogroup1' 'pyrotest1' || exit 0


    CMD> echo 'User pyrotest1 exists or created successfully'
    User pyrotest1 exists or created successfully

    [ OK ]: Action completed: Creating System User pyrotest1
    [ INFO ]: Processing action: Creating System User pyrotest2
    [ INFO ]: Executing Procedure Stage Action: Creating System User pyrotest2
    CMD> id pyrotest2 && echo 'User pyrotest2 already exists' || exit 0


    CMD>  for group in pyrogroup1 pyrogroup2; do groupadd -f $group; done && useradd -m -p 'testpass2' -G 'pyrogroup1,pyrogroup2' 'pyrotest2' || exit 0


    CMD> echo 'User pyrotest2 exists or created successfully'
    User pyrotest2 exists or created successfully

    [ OK ]: Action completed: Creating System User pyrotest2
    [ OK ]: Stage completed: Users
    [ INFO ]: Processing stage: Groups
    [ INFO ]: Processing action: Creating System Group pyrogroup1
    [ INFO ]: Executing Procedure Stage Action: Creating System Group pyrogroup1
    CMD> getent group pyrogroup1 && echo 'Group pyrogroup1 already exists' || exit 0
    pyrogroup1:x:1000:pyrotest1,pyrotest2
    Group pyrogroup1 already exists

    CMD>  groupadd -f 'pyrogroup1' && for user in pyrotest1 pyrotest2; do id $user || useradd -m $user; usermod -a -G 'pyrogroup1' $user; done
    uid=1000(pyrotest1) gid=1001(pyrotest1) groups=1001(pyrotest1),1000(pyrogroup1)
    uid=1001(pyrotest2) gid=1003(pyrotest2) groups=1003(pyrotest2),1000(pyrogroup1),1002(pyrogroup2)

    CMD> echo 'Group pyrogroup1 exists'
    Group pyrogroup1 exists

    [ OK ]: Action completed: Creating System Group pyrogroup1
    [ INFO ]: Processing action: Creating System Group pyrogroup2
    [ INFO ]: Executing Procedure Stage Action: Creating System Group pyrogroup2
    CMD> getent group pyrogroup2 && echo 'Group pyrogroup2 already exists' || exit 0
    pyrogroup2:x:1002:pyrotest2
    Group pyrogroup2 already exists

    CMD>  groupadd -f 'pyrogroup2' && for user in pyrotest2; do id $user || useradd -m $user; usermod -a -G 'pyrogroup2' $user; done
    uid=1001(pyrotest2) gid=1003(pyrotest2) groups=1003(pyrotest2),1000(pyrogroup1),1002(pyrogroup2)

    CMD> echo 'Group pyrogroup2 exists'
    Group pyrogroup2 exists

    [ OK ]: Action completed: Creating System Group pyrogroup2
    [ OK ]: Stage completed: Groups
    [ OK ]: Procedure completed: SUCCESS
```

## 2. Verify users created
```text
    root@1e1b62138bef:/app/Pyroform# id pyrotest1 && id pyrotest2
    uid=1000(pyrotest1) gid=1001(pyrotest1) groups=1001(pyrotest1),1000(pyrogroup1)
    uid=1001(pyrotest2) gid=1003(pyrotest2) groups=1003(pyrotest2),1000(pyrogroup1),1002(pyrogroup2)
```

## 3. Verify groups created
```text
    root@1e1b62138bef:/app/Pyroform# getent group pyrogroup1 && getent group pyrogroup2
    pyrogroup1:x:1000:pyrotest1,pyrotest2
    pyrogroup2:x:1002:pyrotest2
```

## 4. Verify group membership
```text
    root@1e1b62138bef:/app/Pyroform# groups pyrotest1 && groups pyrotest2
    pyrotest1 : pyrotest1 pyrogroup1
    pyrotest2 : pyrotest2 pyrogroup1 pyrogroup2
```

## 5. Cleanup
```text
    root@1e1b62138bef:/app/Pyroform# userdel -r pyrotest1 && userdel -r pyrotest2
    userdel: pyrotest1 mail spool (/var/mail/pyrotest1) not found
    userdel: pyrotest2 mail spool (/var/mail/pyrotest2) not found

    root@1e1b62138bef:/app/Pyroform# groupdel pyrogroup1 && groupdel pyrogroup2; echo $?
    0
```
