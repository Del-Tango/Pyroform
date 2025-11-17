# User Creation (Dry Run)
- Test Environment: Docker container with Amazon Linux 2023.6.20241121 6.6.15-amd64
- Tester: D:Ta
- Date: 17/11/2025
- Pyroform Version: 1.0.0
- Validates: [TPS TC_6](../TPS/TC_6.md)
- Status:
[X] PASS
[ ] FAIL
[ ] BLOCKED

# Archive

## 1. Create Pyro file
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

## 2. Check that mentioned users don't exist on the system
```text
    bash-5.2# id pyrotest1 && id pyrotest2
    id: 'pyrotest1': no such user
```

## 3. Run configure acion with the dry-run option flag
```text
bash-5.2# pyroform configure -i dump/users_test.pyro.yaml --dry-run 2> /dev/null | grep -v DEBUG

    ___________________________________________________________________________

    *                          *   Pyroform   *                           *
    ___________________________________________________________________________
                    Regards, the Alveare Solutions #!/Society -x


[ INFO ]: Logging configured: /tmp/pyroflow/pyroflow.log
[ INFO ]: State monitoring configured for inter-process control
[ INFO ]: Parsing Pyro state file (dump/users_test.pyro.yaml)...
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
            "cmd": "# for group in 'pyrogroup1'; do groupadd -f $group; done && useradd -m -p 'testpass1' -G 'pyrogroup1' 'pyrotest1'",
            "setup-cmd": "id pyrotest1",
            "teardown-cmd": "",
            "on-ok-cmd": "echo 'User pyrotest1 exists or created successfully'",
            "on-nok-cmd": "echo 'Failed to create user pyrotest1'",
            "fatal-nok": false
        },
        {
            "name": "Creating System User pyrotest2",
            "cmd": "# for group in 'pyrogroup1 pyrogroup2'; do groupadd -f $group; done && useradd -m -p 'testpass2' -G 'pyrogroup1,pyrogroup2' 'pyrotest2'",
            "setup-cmd": "id pyrotest2",
            "teardown-cmd": "",
            "on-ok-cmd": "echo 'User pyrotest2 exists or created successfully'",
            "on-nok-cmd": "echo 'Failed to create user pyrotest2'",
            "fatal-nok": false
        }
    ],
    "Groups": [
        {
            "name": "create_group_pyrogroup1",
            "cmd": "# groupadd -f 'pyrogroup1' && for user in 'pyrotest1 pyrotest2'; do id $user &>/dev/null || useradd -m $user; usermod -a -G 'pyrogroup1' $user; done",
            "setup-cmd": "groupadd pyrogroup1",
            "teardown-cmd": "",
            "on-ok-cmd": "echo 'Group pyrogroup1 exists'",
            "on-nok-cmd": "echo 'Creating group pyrogroup1'",
            "fatal-nok": false
        },
        {
            "name": "create_group_pyrogroup2",
            "cmd": "# groupadd -f 'pyrogroup2' && for user in 'pyrotest2'; do id $user &>/dev/null || useradd -m $user; usermod -a -G 'pyrogroup2' $user; done",
            "setup-cmd": "groupadd pyrogroup2",
            "teardown-cmd": "",
            "on-ok-cmd": "echo 'Group pyrogroup2 exists'",
            "on-nok-cmd": "echo 'Creating group pyrogroup2'",
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


CMD> # for group in 'pyrogroup1'; do groupadd -f $group; done && useradd -m -p 'testpass1' -G 'pyrogroup1' 'pyrotest1'


CMD> echo 'User pyrotest1 exists or created successfully'
User pyrotest1 exists or created successfully

[ OK ]: Action completed: Creating System User pyrotest1
[ INFO ]: Processing action: Creating System User pyrotest2
[ INFO ]: Executing Procedure Stage Action: Creating System User pyrotest2
CMD> id pyrotest2 && echo 'User pyrotest2 already exists' || exit 0


CMD> # for group in 'pyrogroup1 pyrogroup2'; do groupadd -f $group; done && useradd -m -p 'testpass2' -G 'pyrogroup1,pyrogroup2' 'pyrotest2'


CMD> echo 'User pyrotest2 exists or created successfully'
User pyrotest2 exists or created successfully

[ OK ]: Action completed: Creating System User pyrotest2
[ OK ]: Stage completed: Users
[ INFO ]: Processing stage: Groups
[ INFO ]: Processing action: Creating System Group pyrogroup1
[ INFO ]: Executing Procedure Stage Action: Creating System Group pyrogroup1
CMD> getent group pyrogroup1 && echo 'Group pyrogroup1 already exists' || exit 0


CMD> # groupadd -f 'pyrogroup1' && for user in 'pyrotest1 pyrotest2'; do id $user &>/dev/null || useradd -m $user; usermod -a -G 'pyrogroup1' $user; done


CMD> echo 'Group pyrogroup1 exists'
Group pyrogroup1 exists

[ OK ]: Action completed: Creating System Group pyrogroup1
[ INFO ]: Processing action: Creating System Group pyrogroup2
[ INFO ]: Executing Procedure Stage Action: Creating System Group pyrogroup2
CMD> getent group pyrogroup2 && echo 'Group pyrogroup2 already exists' || exit 0


CMD> # groupadd -f 'pyrogroup2' && for user in 'pyrotest2'; do id $user &>/dev/null || useradd -m $user; usermod -a -G 'pyrogroup2' $user; done


CMD> echo 'Group pyrogroup2 exists'
Group pyrogroup2 exists

[ OK ]: Action completed: Creating System Group pyrogroup2
[ OK ]: Stage completed: Groups
[ OK ]: Procedure completed: SUCCESS
```

## 4. Analiza commands generated by Pyro action configure
```text
...
CMD> # for group in 'pyrogroup1'; do groupadd -f $group; done && useradd -m -p 'testpass1' -G 'pyrogroup1' 'pyrotest1'
CMD> # for group in 'pyrogroup1 pyrogroup2'; do groupadd -f $group; done && useradd -m -p 'testpass2' -G 'pyrogroup1,pyrogroup2' 'pyrotest2'
CMD> # groupadd -f 'pyrogroup1' && for user in 'pyrotest1 pyrotest2'; do id $user &>/dev/null || useradd -m $user; usermod -a -G 'pyrogroup1' $user; done
CMD> # groupadd -f 'pyrogroup2' && for user in 'pyrotest2'; do id $user &>/dev/null || useradd -m $user; usermod -a -G 'pyrogroup2' $user; done
...
```
## 5. Verify users still don't exist after dry-run
```text
bash-5.2#  id pyrotest1 && id pyrotest2
id: 'pyrotest1': no such user
```
