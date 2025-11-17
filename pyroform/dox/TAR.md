# Test Archive

# [ Description ]: Pyroform TAR

- Objective: Archive of Pyroform manual testing functionalities as described in the TPS.
- Scope: CLI interface, configuration parsing, system operations, error handling, and safety features.
- Environment: Clean Docker container with Debian image.

--------------------------------------------------------------------------------

# [ TC 1 ]: CLI Help and Version

- Test Environment: Docker container with Amazon Linux 2023.6.20241121 6.6.15-amd64
- Tester: D:Ta
- Date: 11/11/2025
- Pyroform Version: 1.0.0
- Validates: [TPS TC_1](./TPS/TC_1.md)
- Status:
[X] PASS
[ ] FAIL
[ ] BLOCKED

# Remarks

- Help messages on action sub-commands would be betters suited if they addressed only the action in question.

# Archive:

## 1. Display Version
```text
    bash-5.2# pyroform --version

        ___________________________________________________________________________

        *                          *   Pyroform   *                           *
        ___________________________________________________________________________
                        Regards, the Alveare Solutions #!/Society -x

    Pyroform version 1.0.0
```

## 2. Display Help
```text
    bash-5.2# pyroform --help

        ___________________________________________________________________________

        *                          *   Pyroform   *                           *
        ___________________________________________________________________________
                        Regards, the Alveare Solutions #!/Society -x

    Usage: pyroform [OPTIONS]

    Pyroform Linux Configurator

    Options:
    -S, --scorch            Trigger action scorch using input Pyro file(s)
    -M, --mount             Trigger action mount using input Pyro file(s)
    -C, --configure         Trigger action configure using input Pyro file(s)
    -V, --validate          Trigger action validate using input Pyro file(s)
    -i, --input PATH        Path to Pyro file (JSON|YAML) or directory
                            containing Pyro files
    -o, --output PATH       Path to FlowCTRL sketch file (JSON) or directory for
                            generated files
    -c, --config-file PATH  Path to Pyroform config file (JSON|YAML)
    -l, --log-file PATH     Path to Pyroform and FlowCTRL log file
    -r, --dump-report       Flag to generate report file with STDOUT, STDERR
                            plus summary
    -s, --silent            Flag to suppress STDOUT
    -d, --debug             Flag that makes logging and STDOUT messages more
                            verbose
    -v, --version           Action that displays Pyroform version
    -y, --yes               Flag to confirm all manual prompts such that manual
                            interaction from user is not required
    --help                  Show this message and exit.


    bash-5.2# pyroform configure --help

        ___________________________________________________________________________

        *                          *   Pyroform   *                           *
        ___________________________________________________________________________
                        Regards, the Alveare Solutions #!/Society -x

    Usage: pyroform [OPTIONS]

    Pyroform Linux Configurator

    Options:
    -S, --scorch            Trigger action scorch using input Pyro file(s)
    -M, --mount             Trigger action mount using input Pyro file(s)
    -C, --configure         Trigger action configure using input Pyro file(s)
    -V, --validate          Trigger action validate using input Pyro file(s)
    -i, --input PATH        Path to Pyro file (JSON|YAML) or directory
                            containing Pyro files
    -o, --output PATH       Path to FlowCTRL sketch file (JSON) or directory for
                            generated files
    -c, --config-file PATH  Path to Pyroform config file (JSON|YAML)
    -l, --log-file PATH     Path to Pyroform and FlowCTRL log file
    -r, --dump-report       Flag to generate report file with STDOUT, STDERR
                            plus summary
    -s, --silent            Flag to suppress STDOUT
    -d, --debug             Flag that makes logging and STDOUT messages more
                            verbose
    -v, --version           Action that displays Pyroform version
    -y, --yes               Flag to confirm all manual prompts such that manual
                            interaction from user is not required
    --help                  Show this message and exit.


    bash-5.2# pyroform scorch --help

        ___________________________________________________________________________

        *                          *   Pyroform   *                           *
        ___________________________________________________________________________
                        Regards, the Alveare Solutions #!/Society -x

    Usage: pyroform [OPTIONS]

    Pyroform Linux Configurator

    Options:
    -S, --scorch            Trigger action scorch using input Pyro file(s)
    -M, --mount             Trigger action mount using input Pyro file(s)
    -C, --configure         Trigger action configure using input Pyro file(s)
    -V, --validate          Trigger action validate using input Pyro file(s)
    -i, --input PATH        Path to Pyro file (JSON|YAML) or directory
                            containing Pyro files
    -o, --output PATH       Path to FlowCTRL sketch file (JSON) or directory for
                            generated files
    -c, --config-file PATH  Path to Pyroform config file (JSON|YAML)
    -l, --log-file PATH     Path to Pyroform and FlowCTRL log file
    -r, --dump-report       Flag to generate report file with STDOUT, STDERR
                            plus summary
    -s, --silent            Flag to suppress STDOUT
    -d, --debug             Flag that makes logging and STDOUT messages more
                            verbose
    -v, --version           Action that displays Pyroform version
    -y, --yes               Flag to confirm all manual prompts such that manual
                            interaction from user is not required
    --help                  Show this message and exit.


    bash-5.2# pyroform mount --help

        ___________________________________________________________________________

        *                          *   Pyroform   *                           *
        ___________________________________________________________________________
                        Regards, the Alveare Solutions #!/Society -x

    Usage: pyroform [OPTIONS]

    Pyroform Linux Configurator

    Options:
    -S, --scorch            Trigger action scorch using input Pyro file(s)
    -M, --mount             Trigger action mount using input Pyro file(s)
    -C, --configure         Trigger action configure using input Pyro file(s)
    -V, --validate          Trigger action validate using input Pyro file(s)
    -i, --input PATH        Path to Pyro file (JSON|YAML) or directory
                            containing Pyro files
    -o, --output PATH       Path to FlowCTRL sketch file (JSON) or directory for
                            generated files
    -c, --config-file PATH  Path to Pyroform config file (JSON|YAML)
    -l, --log-file PATH     Path to Pyroform and FlowCTRL log file
    -r, --dump-report       Flag to generate report file with STDOUT, STDERR
                            plus summary
    -s, --silent            Flag to suppress STDOUT
    -d, --debug             Flag that makes logging and STDOUT messages more
                            verbose
    -v, --version           Action that displays Pyroform version
    -y, --yes               Flag to confirm all manual prompts such that manual
                            interaction from user is not required
    --help                  Show this message and exit.


    bash-5.2# pyroform validate --help

        ___________________________________________________________________________

        *                          *   Pyroform   *                           *
        ___________________________________________________________________________
                        Regards, the Alveare Solutions #!/Society -x

    Usage: pyroform [OPTIONS]

    Pyroform Linux Configurator

    Options:
    -S, --scorch            Trigger action scorch using input Pyro file(s)
    -M, --mount             Trigger action mount using input Pyro file(s)
    -C, --configure         Trigger action configure using input Pyro file(s)
    -V, --validate          Trigger action validate using input Pyro file(s)
    -i, --input PATH        Path to Pyro file (JSON|YAML) or directory
                            containing Pyro files
    -o, --output PATH       Path to FlowCTRL sketch file (JSON) or directory for
                            generated files
    -c, --config-file PATH  Path to Pyroform config file (JSON|YAML)
    -l, --log-file PATH     Path to Pyroform and FlowCTRL log file
    -r, --dump-report       Flag to generate report file with STDOUT, STDERR
                            plus summary
    -s, --silent            Flag to suppress STDOUT
    -d, --debug             Flag that makes logging and STDOUT messages more
                            verbose
    -v, --version           Action that displays Pyroform version
    -y, --yes               Flag to confirm all manual prompts such that manual
                            interaction from user is not required
    --help                  Show this message and exit.



    bash-5.2# pyroform workflow --help

        ___________________________________________________________________________

        *                          *   Pyroform   *                           *
        ___________________________________________________________________________
                        Regards, the Alveare Solutions #!/Society -x

    Usage: pyroform [OPTIONS]

    Pyroform Linux Configurator

    Options:
    -S, --scorch            Trigger action scorch using input Pyro file(s)
    -M, --mount             Trigger action mount using input Pyro file(s)
    -C, --configure         Trigger action configure using input Pyro file(s)
    -V, --validate          Trigger action validate using input Pyro file(s)
    -i, --input PATH        Path to Pyro file (JSON|YAML) or directory
                            containing Pyro files
    -o, --output PATH       Path to FlowCTRL sketch file (JSON) or directory for
                            generated files
    -c, --config-file PATH  Path to Pyroform config file (JSON|YAML)
    -l, --log-file PATH     Path to Pyroform and FlowCTRL log file
    -r, --dump-report       Flag to generate report file with STDOUT, STDERR
                            plus summary
    -s, --silent            Flag to suppress STDOUT
    -d, --debug             Flag that makes logging and STDOUT messages more
                            verbose
    -v, --version           Action that displays Pyroform version
    -y, --yes               Flag to confirm all manual prompts such that manual
                            interaction from user is not required
    --help                  Show this message and exit.
```

--------------------------------------------------------------------------------

# [ TC 2 ]: Invalid CLI Usage

- Test Environment: Docker container with Amazon Linux 2023.6.20241121 6.6.15-amd64
- Tester: D:Ta
- Date: 11/11/2025
- Pyroform Version: 1.0.0
- Validates: [TPS TC_2](./TPS/TC_2.md)
- Status:
[x] PASS
[ ] FAIL
[ ] BLOCKED

# Remarks

- Case 4 should have better error messages. In it's current form can be missleading.

# Archive

## 1. No arguments
```text
    bash-5.2# pyroform

        ___________________________________________________________________________

        *                          *   Pyroform   *                           *
        ___________________________________________________________________________
                        Regards, the Alveare Solutions #!/Society -x

    Usage: pyroform [OPTIONS]
    Try 'pyroform --help' for help.

    Error: No action specified. Use --scorch, --mount, --configure, or --validate

    bash-5.2# echo $?
    2
```

## 2. Invalid action
```text
    bash-5.2# pyroform invalid-command
    Usage: pyroform [OPTIONS]
    Try 'pyroform --help' for help.

    Error: Got unexpected extra argument (invalid-command)

    bash-5.2# echo $?
    2
```

## 3. Invalid option flag
```text
    bash-5.2# pyroform configure --invalid-flag
    Usage: pyroform [OPTIONS]
    Try 'pyroform --help' for help.

    Error: No such option: --invalid-flag Did you mean --validate?

    bash-5.2# echo $?
    2
```

## 4. Incomplete command
```text
    bash-5.2# pyroform configure
    Usage: pyroform [OPTIONS]
    Try 'pyroform --help' for help.

    Error: Got unexpected extra argument (configure)

    bash-5.2# echo $?
    2
```

## 5. Multiple actions
```text
    bash-5.2# pyroform --configure --scorch

        ___________________________________________________________________________

        *                          *   Pyroform   *                           *
        ___________________________________________________________________________
                        Regards, the Alveare Solutions #!/Society -x

    Usage: pyroform [OPTIONS]
    Try 'pyroform --help' for help.

    Error: Exactly one action must be specified: --scorch, --mount, --configure, or --validate

    bash-5.2# echo $?
    2
```

--------------------------------------------------------------------------------

# [ TC 3 ]: YAML Configuration Parsing

- Test Environment: Docker container with Amazon Linux 2023.6.20241121 6.6.15-amd64
- Tester: D:Ta
- Date: 16/11/2025, 14/11/2025, 11/11/2025
- Pyroform Version: 1.0.0
- Validates: [TPS TC_3](./TPS/TC_3.md)
- Status:
[X] PASS
[ ] FAIL
[ ] BLOCKED

# Remarks
N/A

# Archive

## 1. Create dummy Pyro file
```text
    bash-5.2# cat test_config.pyro.yaml
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

## 2. Run validation command using previously created Pyro file
```text
    bash-5.2# pyroform validate -i test_config.pyro.yaml

        ___________________________________________________________________________

        *                          *   Pyroform   *                           *
        ___________________________________________________________________________
                        Regards, the Alveare Solutions #!/Society -x


    [ INFO ]: Parsing Pyro state file (test_config.pyro.yaml)...
    [ INFO ]: State file data: {
        "Label": "Test Configuration",
        "Users": [
            {
                "label": "test_user",
                "Name": "testuser",
                "Password": "test123",
                "Groups": [
                    "testgroup"
                ]
            }
        ],
        "Groups": [
            {
                "label": "test_group",
                "Name": "testgroup",
                "Users": [
                    "testuser"
                ]
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
        ]
    }
    [ NOK ]: Discrepancies [
        {
            "type": "user",
            "name": "testuser",
            "issue": "User does not exist",
            "critical": true
        },
        {
            "type": "group",
            "name": "testgroup",
            "issue": "Group does not exist",
            "critical": true
        },
        {
            "type": "mount",
            "device": "/tmp/test_mount",
            "mountpoint": "/mnt/test",
            "issue": "Device not mounted",
            "critical": false
        }
    ]
    [ NOK ]: Machine state does not correspond with Pyro config Test Configuration
    [ NOK ]: (2) critical issues identified
    [ NOK ]: (3) total issues identified
    [ NOK ]: Machine state does not correspond!

```

## 3. Dry-run of configuration
```text
    bash-5.2# pyroform --configure -i test_config.pyro.yaml --dry-run

    ___________________________________________________________________________

    *                          *   Pyroform   *                           *
    ___________________________________________________________________________
                    Regards, the Alveare Solutions #!/Society -x


[ INFO ]: Logging configured: /tmp/pyroflow/pyroflow.log
[ INFO ]: State monitoring configured for inter-process control
[ INFO ]: Parsing Pyro state file (dump/test_config.pyro.yaml)...
[ INFO ]: State file data: {
    "Label": "Test Configuration",
    "Users": [
        {
            "label": "test_user",
            "Name": "testuser",
            "Password": "test123",
            "Groups": [
                "testgroup"
            ]
        }
    ],
    "Groups": [
        {
            "label": "test_group",
            "Name": "testgroup",
            "Users": [
                "testuser"
            ]
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
    ]
}
[ INFO ]: FlowCTRL Sketch {
    "name": "Pyroform Auto-Generated Sketch Test Configuration",
    "Users": [
        {
            "name": "Creating System User testuser",
            "cmd": "# for group in 'testgroup'; do groupadd -f $group; done && useradd -m -p 'test123' -G 'testgroup' 'testuser'",
            "setup-cmd": "id testuser",
            "teardown-cmd": "",
            "on-ok-cmd": "echo 'User testuser exists or created successfully'",
            "on-nok-cmd": "echo 'Failed to create user testuser'",
            "fatal-nok": false
        }
    ],
    "Groups": [
        {
            "name": "Creating System Group testgroup",
            "cmd": "# groupadd -f 'testgroup' && for user in 'testuser'; do id $user &>/dev/null || useradd -m $user; usermod -a -G 'testgroup' $user; done",
            "setup-cmd": "groupadd testgroup",
            "teardown-cmd": "",
            "on-ok-cmd": "echo 'Group testgroup exists'",
            "on-nok-cmd": "echo 'Creating group testgroup'",
            "fatal-nok": false
        }
    ],
    "Devices": [
        {
            "name": "Creating System Mountpoint Directory mnt_test",
            "cmd": "# mkdir -p /mnt/test",
            "setup-cmd": "test -d /mnt/test",
            "teardown-cmd": "",
            "on-ok-cmd": "echo 'Mountpoint /mnt/test exists'",
            "on-nok-cmd": "echo 'Creating mountpoint /mnt/test'",
            "fatal-nok": true
        },
        {
            "name": "Mounting Block Device test_device",
            "cmd": "# mount /tmp/test_mount /mnt/test",
            "setup-cmd": "mount | grep -q '/tmp/test_mount on /mnt/test'",
            "teardown-cmd": "",
            "on-ok-cmd": "echo 'Device /tmp/test_mount already mounted to /mnt/test'",
            "on-nok-cmd": "echo 'Mounting /tmp/test_mount to /mnt/test'",
            "fatal-nok": true
        }
    ]
}
[ INFO ]: Purging all state and report data
[ OK ]: All data purged
[ INFO ]: Loading sketch file: pyroflow.sketch.json
[ OK ]: Loaded procedure: Pyroform Auto-Generated Sketch Test Configuration
[ INFO ]: Starting procedure execution with state monitoring
[ INFO ]: Procedure state set to STARTED
[ INFO ]: State monitoring active - process can be controlled externally
[ INFO ]: Beginning controlled procedure execution...
[ INFO ]: Processing stage: Users
[ INFO ]: Processing action: Creating System User testuser
[ INFO ]: Executing Procedure Stage Action: Creating System User testuser
CMD> id testuser


[ NOK ]: id: ‘testuser’: no such user

CMD> # for group in 'testgroup'; do groupadd -f $group; done && useradd -m -p 'test123' -G 'testgroup' 'testuser'


CMD> echo 'User testuser exists or created successfully'
User testuser exists or created successfully

[ OK ]: Action completed: Creating System User testuser
[ OK ]: Stage completed: Users
[ INFO ]: Processing stage: Groups
[ INFO ]: Processing action: create_group_testgroup
[ INFO ]: Executing Procedure Stage Action: create_group_testgroup
CMD> groupadd testgroup


[ NOK ]: /bin/sh: line 1: groupadd: command not found

CMD> # groupadd -f 'testgroup' && for user in 'testuser'; do id $user &>/dev/null || useradd -m $user; usermod -a -G 'testgroup' $user; done


CMD> echo 'Group testgroup exists'
Group testgroup exists

[ OK ]: Action completed: create_group_testgroup
[ OK ]: Stage completed: Groups
[ INFO ]: Processing stage: Devices
[ INFO ]: Processing action: create_mountpoint__mnt_test
[ INFO ]: Executing Procedure Stage Action: create_mountpoint__mnt_test
CMD> test -d /mnt/test


CMD> # mkdir -p /mnt/test


CMD> echo 'Mountpoint /mnt/test exists'
Mountpoint /mnt/test exists

[ OK ]: Action completed: create_mountpoint__mnt_test
[ INFO ]: Processing action: mount_device_test_device
[ INFO ]: Executing Procedure Stage Action: mount_device_test_device
CMD> mount | grep -q '/tmp/test_mount on /mnt/test'


CMD> # mount /tmp/test_mount /mnt/test


CMD> echo 'Device /tmp/test_mount already mounted to /mnt/test'
Device /tmp/test_mount already mounted to /mnt/test

[ OK ]: Action completed: mount_device_test_device
[ OK ]: Stage completed: Devices
[ OK ]: Procedure completed: SUCCESS
```

### Miscellaneous


--------------------------------------------------------------------------------

# [ TC 4 ]: JSON Configuration Parsing

- Test Environment: Docker container with Amazon Linux 2023.6.20241121 6.6.15-amd64
- Tester: D:Ta
- Date: 16/11/2025
- Pyroform Version: 1.0.0
- Validates: [TPS TC_4](./TPS/TC_4.md)
- Status:
[X] PASS
[ ] FAIL
[ ] BLOCKED

# Archive

## 1. Create dummy Pyro file
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

## 2. Run validation command using previously create Pyro file
```text
    bash-5.2# pyroform validate -i dump/test_config.pyro.json

        ___________________________________________________________________________

        *                          *   Pyroform   *                           *
        ___________________________________________________________________________
                        Regards, the Alveare Solutions #!/Society -x


    [ INFO ]: Logging configured: /tmp/pyroflow/pyroflow.log
    [ INFO ]: State monitoring configured for inter-process control
    [ INFO ]: Parsing Pyro state file (dump/test_config.pyro.json)...
    [ INFO ]: State file data: {
        "Label": "Test JSON Config",
        "Users": [
            {
                "label": "json_user",
                "Name": "jsonuser",
                "Password": "json123",
                "Groups": [
                    "jsongroup"
                ]
            }
        ],
        "Groups": [
            {
                "label": "json_group",
                "Name": "jsongroup",
                "Users": [
                    "jsonuser"
                ]
            }
        ],
        "Devices": []
    }
    [ NOK ]: Discrepancies [
        {
            "type": "user",
            "name": "jsonuser",
            "issue": "User does not exist",
            "critical": true
        },
        {
            "type": "group",
            "name": "jsongroup",
            "issue": "Group does not exist",
            "critical": true
        }
    ]
    [ NOK ]: Machine state does not correspond with Pyro config Test JSON Config
    [ NOK ]: (2) critical issues identified
    [ NOK ]: (2) total issues identified
    [ NOK ]: Machine state does not correspond!
```

## 3. Dry-run of configuration
```text
bash-5.2# pyroform configure -i dump/test_config.pyro.json --dry-run

    ___________________________________________________________________________

    *                          *   Pyroform   *                           *
    ___________________________________________________________________________
                    Regards, the Alveare Solutions #!/Society -x


[ INFO ]: Logging configured: /tmp/pyroflow/pyroflow.log
[ INFO ]: State monitoring configured for inter-process control
[ INFO ]: Parsing Pyro state file (dump/test_config.pyro.json)...
[ INFO ]: State file data: {
    "Label": "Test JSON Config",
    "Users": [
        {
            "label": "json_user",
            "Name": "jsonuser",
            "Password": "json123",
            "Groups": [
                "jsongroup"
            ]
        }
    ],
    "Groups": [
        {
            "label": "json_group",
            "Name": "jsongroup",
            "Users": [
                "jsonuser"
            ]
        }
    ],
    "Devices": []
}
[ INFO ]: FlowCTRL Sketch {
    "name": "Pyroform Auto-Generated Sketch Test JSON Config",
    "Users": [
        {
            "name": "Creating System User jsonuser",
            "cmd": "# for group in 'jsongroup'; do groupadd -f $group; done && useradd -m -p 'json123' -G 'jsongroup' 'jsonuser'",
            "setup-cmd": "id jsonuser",
            "teardown-cmd": "",
            "on-ok-cmd": "echo 'User jsonuser exists or created successfully'",
            "on-nok-cmd": "echo 'Failed to create user jsonuser'",
            "fatal-nok": false
        }
    ],
    "Groups": [
        {
            "name": "create_group_jsongroup",
            "cmd": "# groupadd -f 'jsongroup' && for user in 'jsonuser'; do id $user &>/dev/null || useradd -m $user; usermod -a -G 'jsongroup' $user; done",
            "setup-cmd": "groupadd jsongroup",
            "teardown-cmd": "",
            "on-ok-cmd": "echo 'Group jsongroup exists'",
            "on-nok-cmd": "echo 'Creating group jsongroup'",
            "fatal-nok": false
        }
    ]
}
 INFO ]: Purging all state and report data
[ OK ]: All data purged
[ INFO ]: Loading sketch file: pyroflow.sketch.json
[ OK ]: Loaded procedure: Pyroform Auto-Generated Sketch Test JSON Config
[ INFO ]: Starting procedure execution with state monitoring
[ INFO ]: Procedure state set to STARTED
[ INFO ]: State monitoring active - process can be controlled externally
[ INFO ]: Beginning controlled procedure execution...
[ INFO ]: Processing stage: Users
[ INFO ]: Processing action: Creating System User jsonuser
[ INFO ]: Executing Procedure Stage Action: Creating System User jsonuser
CMD> id jsonuser


[ NOK ]: id: ‘jsonuser’: no such user

CMD> # for group in 'jsongroup'; do groupadd -f $group; done && useradd -m -p 'json123' -G 'jsongroup' 'jsonuser'


CMD> echo 'User jsonuser exists or created successfully'
User jsonuser exists or created successfully

[ OK ]: Action completed: Creating System User jsonuser
[ OK ]: Stage completed: Users
[ INFO ]: Processing stage: Groups
[ INFO ]: Processing action: create_group_jsongroup
[ INFO ]: Executing Procedure Stage Action: create_group_jsongroup
CMD> groupadd jsongroup


[ NOK ]: /bin/sh: line 1: groupadd: command not found

CMD> # groupadd -f 'jsongroup' && for user in 'jsonuser'; do id $user &>/dev/null || useradd -m $user; usermod -a -G 'jsongroup' $user; done


CMD> echo 'Group jsongroup exists'
Group jsongroup exists

[ OK ]: Action completed: create_group_jsongroup
[ OK ]: Stage completed: Groups
[ OK ]: Procedure completed: SUCCESS
```

--------------------------------------------------------------------------------

# [ TC 5 ]: Error Handing of Invalid Pyro Files

- Test Environment: Docker container with Amazon Linux 2023.6.20241121 6.6.15-amd64
- Tester: D:Ta
- Date: 16/11/2025
- Pyroform Version: 1.0.0
- Validates: [TPS TC_5](./TPS/TC_5.md)
- Status:
[X] PASS
[ ] FAIL
[ ] BLOCKED

# Archive

## 1. Create Pyro file with invalid JSON syntax
```yaml
{
  "Label": "Test JSON Config",
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
## 2.Create Pyro file with invalid YAML syntax
```json
Label: "Test Configuration"
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
## 3. Create Pyro file with missing required fields
```text
Label: "Test Configuration"
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
## 4. Create Pyro file with invalid fied types
```text
Label: "Test Configuration"
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
## 5. Run validate command for each previously created files
```text
    bash-5.2# pyroform validate -i test_invalid.pyro.yaml

        ___________________________________________________________________________

        *                          *   Pyroform   *                           *
        ___________________________________________________________________________
                        Regards, the Alveare Solutions #!/Society -x


    [ INFO ]: Logging configured: /tmp/pyroflow/pyroflow.log
    [ INFO ]: State monitoring configured for inter-process control
    [ INFO ]: Parsing Pyro state file (test_invalid.pyro.yaml)...
    [ ERROR ]: Validate action failed! Details: while scanning a simple key
    in "dump/test_invalid.pyro.yaml", line 7, column 1
    could not find expected ':'
    in "dump/test_invalid.pyro.yaml", line 8, column 10


    bash-5.2# pyroform validate -i test_invalid.pyro.json

        ___________________________________________________________________________

        *                          *   Pyroform   *                           *
        ___________________________________________________________________________
                        Regards, the Alveare Solutions #!/Society -x


    [ INFO ]: Logging configured: /tmp/pyroflow/pyroflow.log
    [ INFO ]: State monitoring configured for inter-process control
    [ INFO ]: Parsing Pyro state file (test_invalid.pyro.json)...
    [ ERROR ]: Validate action failed! Details: Expecting property name enclosed in double quotes: line 9 column 5 (char 170)


    bash-5.2# pyroform validate -i test_invalid.pyro.yaml

        ___________________________________________________________________________

        *                          *   Pyroform   *                           *
        ___________________________________________________________________________
                        Regards, the Alveare Solutions #!/Society -x


    [ INFO ]: Logging configured: /tmp/pyroflow/pyroflow.log
    [ INFO ]: State monitoring configured for inter-process control
    [ INFO ]: Parsing Pyro state file (test_invalid.pyro.yaml)...
    [ ERROR ]: Validate action failed! Details: 'str' object has no attribute 'get'


    bash-5.2# pyroform validate -i test_invalid.pyro.yaml

        ___________________________________________________________________________

        *                          *   Pyroform   *                           *
        ___________________________________________________________________________
                        Regards, the Alveare Solutions #!/Society -x


    [ INFO ]: Logging configured: /tmp/pyroflow/pyroflow.log
    [ INFO ]: State monitoring configured for inter-process control
    [ INFO ]: Parsing Pyro state file (test_invalid.pyro.yaml)...
    [ INFO ]: State file data: {
        "Label": "Test Configuration",
        "Users": [
            {
                "label": "test_user",
                "Name": "testuser",
                "Password": true,
                "Groups": [
                    "testgroup"
                ]
            }
        ],
        "Groups": [
            {
                "label": "test_group",
                "Name": "testgroup",
                "Users": false
            }
        ],
        "Devices": [
            {
                "label": "test_device",
                "Path": "/tmp/test_mount",
                "Partition": 1,
                "Mountpoint": "/mnt/test",
                "State": 123
            }
        ]
    }
    [ ERROR ]: Validate action failed! Details: 'int' object is not iterable

```

--------------------------------------------------------------------------------

# [ TC 6 ]: User Creation (Dry Run)

- Test Environment: Docker container with Amazon Linux 2023.6.20241121 6.6.15-amd64
- Tester: D:Ta
- Date: 17/11/2025
- Pyroform Version: 1.0.0
- Validates: [TPS TC_6](./TPS/TC_6.md)
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

--------------------------------------------------------------------------------

# [ TC 7 ]: Test Environment:

Tester:
Date:
Pyroform Version:
Status: [ ] PASS [ ] FAIL [ ] BLOCKED

Archive

--------------------------------------------------------------------------------

# [ TC 8 ]: Test Environment:

Tester:
Date:
Pyroform Version:
Status: [ ] PASS [ ] FAIL [ ] BLOCKED

Archive

--------------------------------------------------------------------------------

# [ TC 9 ]: Test Environment:

Tester:
Date:
Pyroform Version:
Status: [ ] PASS [ ] FAIL [ ] BLOCKED

Archive

--------------------------------------------------------------------------------

# [ TC 10 ]: Test Environment:

Tester:
Date:
Pyroform Version:
Status: [ ] PASS [ ] FAIL [ ] BLOCKED

Archive

--------------------------------------------------------------------------------

# [ TC 11 ]: Test Environment:

Tester:
Date:
Pyroform Version:
Status: [ ] PASS [ ] FAIL [ ] BLOCKED

Archive

--------------------------------------------------------------------------------

# [ TC 12 ]: Test Environment:

Tester:
Date:
Pyroform Version:
Status: [ ] PASS [ ] FAIL [ ] BLOCKED

Archive

--------------------------------------------------------------------------------

# [ TC 13 ]: Test Environment:

Tester:
Date:
Pyroform Version:
Status: [ ] PASS [ ] FAIL [ ] BLOCKED

Archive

--------------------------------------------------------------------------------

# [ TC 14 ]: Test Environment:

Tester:
Date:
Pyroform Version:
Status: [ ] PASS [ ] FAIL [ ] BLOCKED

Archive

--------------------------------------------------------------------------------

# [ TC 15 ]: Test Environment:

Tester:
Date:
Pyroform Version:
Status: [ ] PASS [ ] FAIL [ ] BLOCKED

Archive

--------------------------------------------------------------------------------

# [ TC 16 ]: Test Environment:

Tester:
Date:
Pyroform Version:
Status: [ ] PASS [ ] FAIL [ ] BLOCKED

Archive

--------------------------------------------------------------------------------

# [ Conclusion ]: Overview

## Overall Status:
- [ ] READY FOR PRODUCTION
- [ ] NEEDS FIXES
- [ ] NOT READY

## Critical Issues Found
N/A

## Recommendations
N/A

