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

# [ TC 7 ]: Actual User Creation

- Test Environment: Docker container with Debian GNU/Linux 13 (trixie) 6.6.15-amd64
- Tester: D:Ta
- Date: 17/11/2025
- Pyroform Version: 1.0.0
- Validates: [TPS TC_7](./TPS/TC_7.md)
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

--------------------------------------------------------------------------------

# [ TC 8 ]: Directory Structure Creation

- Test Environment: Docker container with Debian GNU/Linux 13 (trixie) 6.6.15-amd64
- Tester: D:Ta
- Date: 18/11/2025
- Pyroform Version: 1.0.0
- Validates: [TPS TC_8](./TPS/TC_8.md)
- Preconditions: Users from TC_7 exist
- Status:
[X] PASS
[ ] FAIL
[ ] BLOCKED

# Archive

## 1. Create test Pyro file
```text
Label: "Filesystem Test"
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
```

## 2. Dry-run configure
```text
    root@1e1b62138bef:/app/Pyroform# pyroform configure -i fs_test.pyro.yaml --dry-run

        ___________________________________________________________________________

        *                          *   Pyroform   *                           *
        ___________________________________________________________________________
                        Regards, the Alveare Solutions #!/Society -x


    [ INFO ]: Logging configured: /usr/local/lib/python3.13/dist-packages/log/pyroflow/pyroflow.log
    [ INFO ]: State monitoring configured for inter-process control
    [ INFO ]: Parsing Pyro state file (fs_test.pyro.yaml)...
    [ INFO ]: State file data: {
        "Label": "Filesystem Test",
        "Devices": [
            {
                "label": "test_fs",
                "Path": "",
                "Partition": 0,
                "Mountpoint": "/tmp/pyrotest",
                "State": [
                    "dir,/tmp/pyrotest,root,root,755",
                    "dir,/tmp/pyrotest/data,pyrotest1,pyrogroup1,750",
                    "dir,/tmp/pyrotest/logs,root,pyrogroup1,775",
                    "fl,/tmp/pyrotest/README,pyrotest1,pyrogroup1,644",
                    "ln,/tmp/pyrotest/readme_shortcut,pyrotest1,pyrogroup1,777,/tmp/pyrotest/README"
                ]
            }
        ]
    }
    [ INFO ]: FlowCTRL Sketch {
        "name": "Pyroform Auto-Generated Sketch Filesystem Test",
        "Devices": [
            {
                "name": "Creating System Mountpoint Directory _tmp_pyrotest",
                "cmd": "# mkdir -p /tmp/pyrotest",
                "setup-cmd": "test -d /tmp/pyrotest",
                "teardown-cmd": "",
                "on-ok-cmd": "echo 'Mountpoint /tmp/pyrotest exists'",
                "on-nok-cmd": "echo 'Creating mountpoint /tmp/pyrotest'",
                "fatal-nok": true
            },
            {
                "name": "Mounting Block Device test_fs",
                "cmd": "# mount  /tmp/pyrotest",
                "setup-cmd": "mount | grep -q ' on /tmp/pyrotest'",
                "teardown-cmd": "",
                "on-ok-cmd": "echo 'Device  already mounted to /tmp/pyrotest'",
                "on-nok-cmd": "echo 'Mounting  to /tmp/pyrotest'",
                "fatal-nok": true
            },
            {
                "name": "Creating Directory /tmp/pyrotest",
                "cmd": "# mkdir -p /tmp/pyrotest",
                "setup-cmd": "test -d /tmp/pyrotest",
                "teardown-cmd": "",
                "on-ok-cmd": "echo 'Directory /tmp/pyrotest exists'",
                "on-nok-cmd": "echo 'Creating directory /tmp/pyrotest'",
                "fatal-nok": true
            },
            {
                "name": "Setting Permissions For /tmp/pyrotest",
                "cmd": "# chown root:root /tmp/pyrotest && chmod 755 /tmp/pyrotest",
                "setup-cmd": "stat -c '%U:%G %a' /tmp/pyrotest | grep -q 'root:root 755'",
                "teardown-cmd": "",
                "on-ok-cmd": "echo 'Permissions for /tmp/pyrotest are correct'",
                "on-nok-cmd": "echo 'Setting permissions for /tmp/pyrotest'",
                "fatal-nok": true
            },
            {
                "name": "Creating Directory /tmp/pyrotest/data",
                "cmd": "# mkdir -p /tmp/pyrotest/data",
                "setup-cmd": "test -d /tmp/pyrotest/data",
                "teardown-cmd": "",
                "on-ok-cmd": "echo 'Directory /tmp/pyrotest/data exists'",
                "on-nok-cmd": "echo 'Creating directory /tmp/pyrotest/data'",
                "fatal-nok": true
            },
            {                                                                                                                                                                                                                  17:15:06 [187/1819]
                "name": "Setting Permissions For /tmp/pyrotest/data",
                "cmd": "# chown pyrotest1:pyrogroup1 /tmp/pyrotest/data && chmod 750 /tmp/pyrotest/data",
                "setup-cmd": "stat -c '%U:%G %a' /tmp/pyrotest/data | grep -q 'pyrotest1:pyrogroup1 750'",
                "teardown-cmd": "",
                "on-ok-cmd": "echo 'Permissions for /tmp/pyrotest/data are correct'",
                "on-nok-cmd": "echo 'Setting permissions for /tmp/pyrotest/data'",
                "fatal-nok": true
            },
            {
                "name": "Creating Directory /tmp/pyrotest/logs",
                "cmd": "# mkdir -p /tmp/pyrotest/logs",
                "setup-cmd": "test -d /tmp/pyrotest/logs",
                "teardown-cmd": "",
                "on-ok-cmd": "echo 'Directory /tmp/pyrotest/logs exists'",
                "on-nok-cmd": "echo 'Creating directory /tmp/pyrotest/logs'",
                "fatal-nok": true
            },
            {
                "name": "Setting Permissions For /tmp/pyrotest/logs",
                "cmd": "# chown root:pyrogroup1 /tmp/pyrotest/logs && chmod 775 /tmp/pyrotest/logs",
                "setup-cmd": "stat -c '%U:%G %a' /tmp/pyrotest/logs | grep -q 'root:pyrogroup1 775'",
                "teardown-cmd": "",
                "on-ok-cmd": "echo 'Permissions for /tmp/pyrotest/logs are correct'",
                "on-nok-cmd": "echo 'Setting permissions for /tmp/pyrotest/logs'",
                "fatal-nok": true
            },
            {
                "name": "Creating Regular File /tmp/pyrotest/README",
                "cmd": "# touch /tmp/pyrotest/README",
                "setup-cmd": "test -f /tmp/pyrotest/README",
                "teardown-cmd": "",
                "on-ok-cmd": "echo 'File /tmp/pyrotest/README exists'",
                "on-nok-cmd": "echo 'Creating file /tmp/pyrotest/README'",
                "fatal-nok": true
            },
            {
                "name": "Setting Permissions For /tmp/pyrotest/README",
                "cmd": "# chown pyrotest1:pyrogroup1 /tmp/pyrotest/README && chmod 644 /tmp/pyrotest/README",
                "setup-cmd": "stat -c '%U:%G %a' /tmp/pyrotest/README | grep -q 'pyrotest1:pyrogroup1 644'",
                "teardown-cmd": "",
                "on-ok-cmd": "echo 'Permissions for /tmp/pyrotest/README are correct'",
                "on-nok-cmd": "echo 'Setting permissions for /tmp/pyrotest/README'",
                "fatal-nok": true
            },
            {
                "name": "Creating Symbolic Link /tmp/pyrotest/readme_shortcut",
                "cmd": "# ln -s /tmp/pyrotest/README /tmp/pyrotest/readme_shortcut",
                "setup-cmd": "test -l /tmp/pyrotest/readme_shortcut",
                "teardown-cmd": "",
                "on-ok-cmd": "echo 'File /tmp/pyrotest/readme_shortcut exists'",
                "on-nok-cmd": "echo 'Creating file /tmp/pyrotest/readme_shortcut'",
                "fatal-nok": true
            },
            {
                "name": "Setting Permissions For /tmp/pyrotest/readme_shortcut",
                "cmd": "# chown pyrotest1:pyrogroup1 /tmp/pyrotest/readme_shortcut && chmod 777 /tmp/pyrotest/readme_shortcut",
                "setup-cmd": "stat -c '%U:%G %a' /tmp/pyrotest/readme_shortcut | grep -q 'pyrotest1:pyrogroup1 777'",
                "teardown-cmd": "",
                "on-ok-cmd": "echo 'Permissions for /tmp/pyrotest/readme_shortcut are correct'",
                "on-nok-cmd": "echo 'Setting permissions for /tmp/pyrotest/readme_shortcut'",
                "fatal-nok": true
            }
        ]
    }
    [ INFO ]: Purging all state and report data
    [ OK ]: All data purged
    [ INFO ]: Loading sketch file: pyroflow.sketch.json
    [ OK ]: Loaded procedure: Pyroform Auto-Generated Sketch Filesystem Test
    [ INFO ]: Starting procedure execution with state monitoring
    [ INFO ]: Procedure state set to STARTED
    [ INFO ]: State monitoring active - process can be controlled externally
    [ INFO ]: Beginning controlled procedure execution...
    [ INFO ]: Processing stage: Devices
    [ INFO ]: Processing action: Creating System Mountpoint Directory _tmp_pyrotest
    [ INFO ]: Executing Procedure Stage Action: Creating System Mountpoint Directory _tmp_pyrotest
    CMD> test -d /tmp/pyrotest


    [ NOK ]:

    CMD> # mkdir -p /tmp/pyrotest


    CMD> echo 'Mountpoint /tmp/pyrotest exists'
    Mountpoint /tmp/pyrotest exists

    [ OK ]: Action completed: Creating System Mountpoint Directory _tmp_pyrotest
    [ INFO ]: Processing action: Mounting Block Device test_fs
    [ INFO ]: Executing Procedure Stage Action: Mounting Block Device test_fs
    CMD> mount | grep -q ' on /tmp/pyrotest'


    [ NOK ]:

    CMD> # mount  /tmp/pyrotest


    CMD> echo 'Device  already mounted to /tmp/pyrotest'
    Device  already mounted to /tmp/pyrotest

    [ OK ]: Action completed: Mounting Block Device test_fs
    [ INFO ]: Processing action: Creating Directory /tmp/pyrotest
    [ INFO ]: Executing Procedure Stage Action: Creating Directory /tmp/pyrotest
    CMD> test -d /tmp/pyrotest


    [ NOK ]:

    CMD> # mkdir -p /tmp/pyrotest


    CMD> echo 'Directory /tmp/pyrotest exists'
    Directory /tmp/pyrotest exists

    [ OK ]: Action completed: Creating Directory /tmp/pyrotest
    [ INFO ]: Processing action: Setting Permissions For /tmp/pyrotest
    [ INFO ]: Executing Procedure Stage Action: Setting Permissions For /tmp/pyrotest
    CMD> stat -c '%U:%G %a' /tmp/pyrotest | grep -q 'root:root 755'


    [ NOK ]: stat: cannot statx '/tmp/pyrotest': No such file or directory

    CMD> # chown root:root /tmp/pyrotest && chmod 755 /tmp/pyrotest


    CMD> echo 'Permissions for /tmp/pyrotest are correct'
    Permissions for /tmp/pyrotest are correct

    [ OK ]: Action completed: Setting Permissions For /tmp/pyrotest
    [ INFO ]: Processing action: Creating Directory /tmp/pyrotest/data
    [ INFO ]: Executing Procedure Stage Action: Creating Directory /tmp/pyrotest/data
    CMD> test -d /tmp/pyrotest/data


    [ NOK ]:

    CMD> # mkdir -p /tmp/pyrotest/data


    CMD> echo 'Directory /tmp/pyrotest/data exists'
    Directory /tmp/pyrotest/data exists

    [ OK ]: Action completed: Creating Directory /tmp/pyrotest/data
    [ INFO ]: Processing action: Setting Permissions For /tmp/pyrotest/data
    [ INFO ]: Executing Procedure Stage Action: Setting Permissions For /tmp/pyrotest/data
    CMD> stat -c '%U:%G %a' /tmp/pyrotest/data | grep -q 'pyrotest1:pyrogroup1 750'


    [ NOK ]: stat: cannot statx '/tmp/pyrotest/data': No such file or directory

    CMD> # chown pyrotest1:pyrogroup1 /tmp/pyrotest/data && chmod 750 /tmp/pyrotest/data


    CMD> echo 'Permissions for /tmp/pyrotest/data are correct'
    Permissions for /tmp/pyrotest/data are correct

    [ OK ]: Action completed: Setting Permissions For /tmp/pyrotest/data
    [ INFO ]: Processing action: Creating Directory /tmp/pyrotest/logs
    [ INFO ]: Executing Procedure Stage Action: Creating Directory /tmp/pyrotest/logs
    CMD> test -d /tmp/pyrotest/logs


    [ NOK ]:

    CMD> # mkdir -p /tmp/pyrotest/logs


    CMD> echo 'Directory /tmp/pyrotest/logs exists'
    Directory /tmp/pyrotest/logs exists

    [ OK ]: Action completed: Creating Directory /tmp/pyrotest/logs
    [ INFO ]: Processing action: Setting Permissions For /tmp/pyrotest/logs
    [ INFO ]: Executing Procedure Stage Action: Setting Permissions For /tmp/pyrotest/logs
    CMD> stat -c '%U:%G %a' /tmp/pyrotest/logs | grep -q 'root:pyrogroup1 775'


    [ NOK ]: stat: cannot statx '/tmp/pyrotest/logs': No such file or directory

    CMD> # chown root:pyrogroup1 /tmp/pyrotest/logs && chmod 775 /tmp/pyrotest/logs


    CMD> echo 'Permissions for /tmp/pyrotest/logs are correct'
    Permissions for /tmp/pyrotest/logs are correct

    [ OK ]: Action completed: Setting Permissions For /tmp/pyrotest/logs
    [ INFO ]: Processing action: Creating Regular File /tmp/pyrotest/README
    [ INFO ]: Executing Procedure Stage Action: Creating Regular File /tmp/pyrotest/README
    CMD> test -f /tmp/pyrotest/README


    [ NOK ]:

    CMD> # touch /tmp/pyrotest/README


    CMD> echo 'File /tmp/pyrotest/README exists'
    File /tmp/pyrotest/README exists

    [ OK ]: Action completed: Creating Regular File /tmp/pyrotest/README
    [ INFO ]: Processing action: Setting Permissions For /tmp/pyrotest/README
    [ INFO ]: Executing Procedure Stage Action: Setting Permissions For /tmp/pyrotest/README
    CMD> stat -c '%U:%G %a' /tmp/pyrotest/README | grep -q 'pyrotest1:pyrogroup1 644'


    [ NOK ]: stat: cannot statx '/tmp/pyrotest/README': No such file or directory

    CMD> # chown pyrotest1:pyrogroup1 /tmp/pyrotest/README && chmod 644 /tmp/pyrotest/README


    CMD> echo 'Permissions for /tmp/pyrotest/README are correct'
    Permissions for /tmp/pyrotest/README are correct

    [ OK ]: Action completed: Setting Permissions For /tmp/pyrotest/README
    [ INFO ]: Processing action: Creating Symbolic Link /tmp/pyrotest/readme_shortcut
    [ INFO ]: Executing Procedure Stage Action: Creating Symbolic Link /tmp/pyrotest/readme_shortcut
    CMD> test -l /tmp/pyrotest/readme_shortcut


    [ NOK ]: /bin/sh: 1: test: -l: unexpected operator

    CMD> # ln -s /tmp/pyrotest/README /tmp/pyrotest/readme_shortcut


    CMD> echo 'File /tmp/pyrotest/readme_shortcut exists'
    File /tmp/pyrotest/readme_shortcut exists

    [ OK ]: Action completed: Creating Symbolic Link /tmp/pyrotest/readme_shortcut
    [ INFO ]: Processing action: Setting Permissions For /tmp/pyrotest/readme_shortcut
    [ INFO ]: Executing Procedure Stage Action: Setting Permissions For /tmp/pyrotest/readme_shortcut
    CMD> stat -c '%U:%G %a' /tmp/pyrotest/readme_shortcut | grep -q 'pyrotest1:pyrogroup1 777'


    [ NOK ]: stat: cannot statx '/tmp/pyrotest/readme_shortcut': No such file or directory

    CMD> # chown pyrotest1:pyrogroup1 /tmp/pyrotest/readme_shortcut && chmod 777 /tmp/pyrotest/readme_shortcut


    CMD> echo 'Permissions for /tmp/pyrotest/readme_shortcut are correct'
    Permissions for /tmp/pyrotest/readme_shortcut are correct

    [ OK ]: Action completed: Setting Permissions For /tmp/pyrotest/readme_shortcut
    [ OK ]: Stage completed: Devices
    [ OK ]: Procedure completed: SUCCESS
```

## 3. Run configure command (auto-confirm)
```text
    root@1e1b62138bef:/app/Pyroform# pyroform configure -i dump/fs_test.pyro.yaml -y

        ___________________________________________________________________________

          *                          *   Pyroform   *                           *
        ___________________________________________________________________________
                        Regards, the Alveare Solutions #!/Society -x


    [ INFO ]: Logging configured: /usr/local/lib/python3.13/dist-packages/log/pyroflow/pyroflow.log
    [ INFO ]: State monitoring configured for inter-process control
    [ INFO ]: Parsing Pyro state file (fs_test.pyro.yaml)...
    [ INFO ]: State file data: {
        "Label": "Filesystem Test",
        "Devices": [
            {
                "label": "test_fs",
                "Path": "",
                "Partition": 0,
                "Mountpoint": "/tmp/pyrotest",
                "State": [
                    "dir,/tmp/pyrotest,root,root,755",
                    "dir,/tmp/pyrotest/data,pyrotest1,pyrogroup1,750",
                    "dir,/tmp/pyrotest/logs,root,pyrogroup1,775",
                    "fl,/tmp/pyrotest/README,pyrotest1,pyrogroup1,644",
                    "ln,/tmp/pyrotest/readme_shortcut,pyrotest1,pyrogroup1,777,/tmp/pyrotest/README"
                ]
            }
        ]
    }
    [ INFO ]: FlowCTRL Sketch {
        "name": "Pyroform Auto-Generated Sketch Filesystem Test",
        "Devices": [
            {
                "name": "Creating System Mountpoint Directory /tmp/pyrotest",
                "cmd": "mkdir -p /tmp/pyrotest",
                "setup-cmd": "test -d /tmp/pyrotest",
                "teardown-cmd": "",
                "on-ok-cmd": "echo 'Mountpoint /tmp/pyrotest exists'",
                "on-nok-cmd": "echo 'Creating mountpoint /tmp/pyrotest'",
                "fatal-nok": true
            },
            {
                "name": "Creating Directory /tmp/pyrotest",
                "cmd": "mkdir -p /tmp/pyrotest",
                "setup-cmd": "test -d /tmp/pyrotest",
                "teardown-cmd": "",
                "on-ok-cmd": "echo 'Directory /tmp/pyrotest exists'",
                "on-nok-cmd": "echo 'Creating directory /tmp/pyrotest'",
                "fatal-nok": true
            },
            {
                "name": "Setting Permissions For /tmp/pyrotest",
                "cmd": "chown root:root /tmp/pyrotest && chmod 755 /tmp/pyrotest",
                "setup-cmd": "stat -c '%U:%G %a' /tmp/pyrotest | grep -q 'root:root 755'",
                "teardown-cmd": "",
                "on-ok-cmd": "echo 'Permissions for /tmp/pyrotest are correct'",
                "on-nok-cmd": "echo 'Setting permissions for /tmp/pyrotest'",
                "fatal-nok": true
            },
            {
                "name": "Creating Directory /tmp/pyrotest/data",
                "cmd": "mkdir -p /tmp/pyrotest/data",
                "setup-cmd": "test -d /tmp/pyrotest/data",
                "teardown-cmd": "",
                "on-ok-cmd": "echo 'Directory /tmp/pyrotest/data exists'",
                "on-nok-cmd": "echo 'Creating directory /tmp/pyrotest/data'",
                "fatal-nok": true
            },
            {
                "name": "Setting Permissions For /tmp/pyrotest/data",
                "cmd": "chown pyrotest1:pyrogroup1 /tmp/pyrotest/data && chmod 750 /tmp/pyrotest/data",
                "setup-cmd": "stat -c '%U:%G %a' /tmp/pyrotest/data | grep -q 'pyrotest1:pyrogroup1 750'",
                "teardown-cmd": "",
                "on-ok-cmd": "echo 'Permissions for /tmp/pyrotest/data are correct'",
                "on-nok-cmd": "echo 'Setting permissions for /tmp/pyrotest/data'",
                "fatal-nok": true
            },
            {
                "name": "Creating Directory /tmp/pyrotest/logs",
                "cmd": "mkdir -p /tmp/pyrotest/logs",
                "setup-cmd": "test -d /tmp/pyrotest/logs",
                "teardown-cmd": "",
                "on-ok-cmd": "echo 'Directory /tmp/pyrotest/logs exists'",
                "on-nok-cmd": "echo 'Creating directory /tmp/pyrotest/logs'",
                "fatal-nok": true
            },
            {
                "name": "Setting Permissions For /tmp/pyrotest/logs",
                "cmd": "chown root:pyrogroup1 /tmp/pyrotest/logs && chmod 775 /tmp/pyrotest/logs",
                "setup-cmd": "stat -c '%U:%G %a' /tmp/pyrotest/logs | grep -q 'root:pyrogroup1 775'",
                "teardown-cmd": "",
                "on-ok-cmd": "echo 'Permissions for /tmp/pyrotest/logs are correct'",
                "on-nok-cmd": "echo 'Setting permissions for /tmp/pyrotest/logs'",
                "fatal-nok": true
            },
            {
                "name": "Creating Regular File /tmp/pyrotest/README",
                "cmd": "touch /tmp/pyrotest/README",
                "setup-cmd": "test -f /tmp/pyrotest/README",
                "teardown-cmd": "",
                "on-ok-cmd": "echo 'File /tmp/pyrotest/README exists'",
                "on-nok-cmd": "echo 'Creating file /tmp/pyrotest/README'",
                "fatal-nok": true
            },
            {
                "name": "Setting Permissions For /tmp/pyrotest/README",
                "cmd": "chown pyrotest1:pyrogroup1 /tmp/pyrotest/README && chmod 644 /tmp/pyrotest/README",
                "setup-cmd": "stat -c '%U:%G %a' /tmp/pyrotest/README | grep -q 'pyrotest1:pyrogroup1 644'",
                "teardown-cmd": "",
                "on-ok-cmd": "echo 'Permissions for /tmp/pyrotest/README are correct'",
                "on-nok-cmd": "echo 'Setting permissions for /tmp/pyrotest/README'",
                "fatal-nok": true
            },
            {
                "name": "Creating Symbolic Link /tmp/pyrotest/readme_shortcut",
                "cmd": "ln -s /tmp/pyrotest/README /tmp/pyrotest/readme_shortcut",
                "setup-cmd": "test -L /tmp/pyrotest/readme_shortcut",
                "teardown-cmd": "",
                "on-ok-cmd": "echo 'File /tmp/pyrotest/readme_shortcut exists'",
                "on-nok-cmd": "echo 'Creating file /tmp/pyrotest/readme_shortcut'",
                "fatal-nok": true
            },
            {
                "name": "Setting Permissions For /tmp/pyrotest/readme_shortcut",
                "cmd": "chown pyrotest1:pyrogroup1 /tmp/pyrotest/readme_shortcut && chmod 777 /tmp/pyrotest/readme_shortcut",
                "setup-cmd": "stat -c '%U:%G %a' /tmp/pyrotest/readme_shortcut | grep -q 'pyrotest1:pyrogroup1 777'",
                "teardown-cmd": "",
                "on-ok-cmd": "echo 'Permissions for /tmp/pyrotest/readme_shortcut are correct'",
                "on-nok-cmd": "echo 'Setting permissions for /tmp/pyrotest/readme_shortcut'",
                "fatal-nok": true
            }
        ]
    }
    [ INFO ]: Purging all state and report data
    [ OK ]: All data purged
    [ INFO ]: Loading sketch file: pyroflow.sketch.json
    [ OK ]: Loaded procedure: Pyroform Auto-Generated Sketch Filesystem Test
    [ INFO ]: Starting procedure execution with state monitoring
    [ INFO ]: Procedure state set to STARTED
    [ INFO ]: State monitoring active - process can be controlled externally
    [ INFO ]: Beginning controlled procedure execution...
    [ INFO ]: Processing stage: Devices
    [ INFO ]: Processing action: Creating System Mountpoint Directory /tmp/pyrotest
    [ INFO ]: Executing Procedure Stage Action: Creating System Mountpoint Directory /tmp/pyrotest
    CMD> test -d /tmp/pyrotest


    [ NOK ]:

    CMD> mkdir -p /tmp/pyrotest


    CMD> echo 'Mountpoint /tmp/pyrotest exists'
    Mountpoint /tmp/pyrotest exists

    [ OK ]: Action completed: Creating System Mountpoint Directory /tmp/pyrotest
    [ INFO ]: Processing action: Creating Directory /tmp/pyrotest
    [ INFO ]: Executing Procedure Stage Action: Creating Directory /tmp/pyrotest
    CMD> test -d /tmp/pyrotest


    CMD> mkdir -p /tmp/pyrotest


    CMD> echo 'Directory /tmp/pyrotest exists'
    Directory /tmp/pyrotest exists

    [ OK ]: Action completed: Creating Directory /tmp/pyrotest
    [ INFO ]: Processing action: Setting Permissions For /tmp/pyrotest
    [ INFO ]: Executing Procedure Stage Action: Setting Permissions For /tmp/pyrotest
    CMD> stat -c '%U:%G %a' /tmp/pyrotest | grep -q 'root:root 755'


    CMD> chown root:root /tmp/pyrotest && chmod 755 /tmp/pyrotest


    CMD> echo 'Permissions for /tmp/pyrotest are correct'
    Permissions for /tmp/pyrotest are correct

    [ OK ]: Action completed: Setting Permissions For /tmp/pyrotest
    [ INFO ]: Processing action: Creating Directory /tmp/pyrotest/data
    [ INFO ]: Executing Procedure Stage Action: Creating Directory /tmp/pyrotest/data
    CMD> test -d /tmp/pyrotest/data


    [ NOK ]:

    CMD> mkdir -p /tmp/pyrotest/data


    CMD> echo 'Directory /tmp/pyrotest/data exists'
    Directory /tmp/pyrotest/data exists

    [ OK ]: Action completed: Creating Directory /tmp/pyrotest/data
    [ INFO ]: Processing action: Setting Permissions For /tmp/pyrotest/data
    [ INFO ]: Executing Procedure Stage Action: Setting Permissions For /tmp/pyrotest/data
    CMD> stat -c '%U:%G %a' /tmp/pyrotest/data | grep -q 'pyrotest1:pyrogroup1 750'


    [ NOK ]:

    CMD> chown pyrotest1:pyrogroup1 /tmp/pyrotest/data && chmod 750 /tmp/pyrotest/data


    CMD> echo 'Permissions for /tmp/pyrotest/data are correct'
    Permissions for /tmp/pyrotest/data are correct

    [ OK ]: Action completed: Setting Permissions For /tmp/pyrotest/data
    [ INFO ]: Processing action: Creating Directory /tmp/pyrotest/logs
    [ INFO ]: Executing Procedure Stage Action: Creating Directory /tmp/pyrotest/logs
    CMD> test -d /tmp/pyrotest/logs


    [ NOK ]:

    CMD> mkdir -p /tmp/pyrotest/logs


    CMD> echo 'Directory /tmp/pyrotest/logs exists'
    Directory /tmp/pyrotest/logs exists

    [ OK ]: Action completed: Creating Directory /tmp/pyrotest/logs
    [ INFO ]: Processing action: Setting Permissions For /tmp/pyrotest/logs
    [ INFO ]: Executing Procedure Stage Action: Setting Permissions For /tmp/pyrotest/logs
    CMD> stat -c '%U:%G %a' /tmp/pyrotest/logs | grep -q 'root:pyrogroup1 775'


    [ NOK ]:

    CMD> chown root:pyrogroup1 /tmp/pyrotest/logs && chmod 775 /tmp/pyrotest/logs


    CMD> echo 'Permissions for /tmp/pyrotest/logs are correct'
    Permissions for /tmp/pyrotest/logs are correct

    [ OK ]: Action completed: Setting Permissions For /tmp/pyrotest/logs
    [ INFO ]: Processing action: Creating Regular File /tmp/pyrotest/README
    [ INFO ]: Executing Procedure Stage Action: Creating Regular File /tmp/pyrotest/README
    CMD> test -f /tmp/pyrotest/README


    [ NOK ]:

    CMD> touch /tmp/pyrotest/README


    CMD> echo 'File /tmp/pyrotest/README exists'
    File /tmp/pyrotest/README exists

    [ OK ]: Action completed: Creating Regular File /tmp/pyrotest/README
    [ INFO ]: Processing action: Setting Permissions For /tmp/pyrotest/README
    [ INFO ]: Executing Procedure Stage Action: Setting Permissions For /tmp/pyrotest/README
    CMD> stat -c '%U:%G %a' /tmp/pyrotest/README | grep -q 'pyrotest1:pyrogroup1 644'


    [ NOK ]:

    CMD> chown pyrotest1:pyrogroup1 /tmp/pyrotest/README && chmod 644 /tmp/pyrotest/README


    CMD> echo 'Permissions for /tmp/pyrotest/README are correct'
    Permissions for /tmp/pyrotest/README are correct

    [ OK ]: Action completed: Setting Permissions For /tmp/pyrotest/README
    [ INFO ]: Processing action: Creating Symbolic Link /tmp/pyrotest/readme_shortcut
    [ INFO ]: Executing Procedure Stage Action: Creating Symbolic Link /tmp/pyrotest/readme_shortcut
    CMD> test -L /tmp/pyrotest/readme_shortcut


    [ NOK ]:

    CMD> ln -s /tmp/pyrotest/README /tmp/pyrotest/readme_shortcut


    CMD> echo 'File /tmp/pyrotest/readme_shortcut exists'
    File /tmp/pyrotest/readme_shortcut exists

    [ OK ]: Action completed: Creating Symbolic Link /tmp/pyrotest/readme_shortcut
    [ INFO ]: Processing action: Setting Permissions For /tmp/pyrotest/readme_shortcut
    [ INFO ]: Executing Procedure Stage Action: Setting Permissions For /tmp/pyrotest/readme_shortcut
    CMD> stat -c '%U:%G %a' /tmp/pyrotest/readme_shortcut | grep -q 'pyrotest1:pyrogroup1 777'


    [ NOK ]:

    CMD> chown pyrotest1:pyrogroup1 /tmp/pyrotest/readme_shortcut && chmod 777 /tmp/pyrotest/readme_shortcut


    CMD> echo 'Permissions for /tmp/pyrotest/readme_shortcut are correct'
    Permissions for /tmp/pyrotest/readme_shortcut are correct

    [ OK ]: Action completed: Setting Permissions For /tmp/pyrotest/readme_shortcut
    [ OK ]: Stage completed: Devices
    [ OK ]: Procedure completed: SUCCESS
```

## 4. Verify created directory structure
```text
    root@1e1b62138bef:/app/Pyroform# tree /tmp/pyrotest/
    /tmp/pyrotest/
    |-- README
    |-- data
    |-- logs
    `-- readme_shortcut -> /tmp/pyrotest/README

    3 directories, 2 files
```

## 5. Verify ownership and permissions
```text
    root@1e1b62138bef:/app/Pyroform# ls -allah /tmp/pyrotest/
    total 24K
    drwxr-xr-x 4 root      root       4.0K Nov 17 22:27 .
    drwxrwxrwt 1 root      root        12K Nov 17 22:27 ..
    -rwxrwxrwx 1 pyrotest1 pyrogroup1    0 Nov 17 22:27 README
    drwxr-x--- 2 pyrotest1 pyrogroup1 4.0K Nov 17 22:27 data
    drwxrwxr-x 2 root      pyrogroup1 4.0K Nov 17 22:27 logs
    lrwxrwxrwx 1 root      root         20 Nov 17 22:27 readme_shortcut -> /tmp/pyrotest/README


    root@1e1b62138bef:/app/Pyroform# echo 'Hell Yes!' > /tmp/pyrotest/readme_shortcut
    root@1e1b62138bef:/app/Pyroform# cat /tmp/pyrotest/README
    Hell Yes!
```

## 6. Cleanup
```text
    root@1e1b62138bef:/app/Pyroform# rm -rf /tmp/pyrotest; echo $?
    0
```


--------------------------------------------------------------------------------

# [ TC 9 ]: Scorch Dry Run

- Test Environment: Docker container with Debian GNU/Linux 13 (trixie) 6.6.15-amd64
- Tester: D:Ta
- Date: 23/11/2025
- Pyroform Version: 1.0.0
- Validates: [TPS TC_9](./TPS/TC_9.md)
- Preconditions: System has some test users/files not in config
- Status:
[X] PASS
[ ] FAIL
[ ] BLOCKED

# Archive

## 1. Create test Pyro file
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
  Users: []
  Groups: []
  Devices:
    - "/dev/sda"
  Directories:
    - "/proc"
    - "/sys"
    - "/dev"
    - "/boot"
    - "/lib"
    - "/lib64"
    - "/sbin"
    - "/usr"
    - "/var"
    - "/app"
    - "/etc"
    - "/usr"
    - "/root"
  Files: []
  Links: []
```

## 2. Create extra user
```text
    root@1e1b62138bef:/app/Pyroform# useradd scorchtest; echo $?
    0
```

## 3. Create extra file
```text
    root@1e1b62138bef:/app/Pyroform# touch /tmp/shall_not_be_scorched.dummy; echo $?
    0
```

## 4. Dry-Run Scorch command
```text
    root@1e1b62138bef:/app/Pyroform# pyroform scorch -i dump/full_test.pyro.yaml --dry-run

        ___________________________________________________________________________

        *                          *   Pyroform   *                           *
        ___________________________________________________________________________
                        Regards, the Alveare Solutions #!/Society -x


    [ INFO ]: Logging configured: /usr/local/lib/python3.13/dist-packages/log/pyroflow/pyroflow.log
    [ INFO ]: State monitoring configured for inter-process control
    [ INFO ]: Parsing Pyro state file (dump/full_test.pyro.yaml)...
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
        ],
        "Devices": [
            {
                "label": "Primary Storage",
                "Path": "/dev/sda",
                "Partition": 1,
                "Mountpoint": "/tmp/pyrotest",
                "State": [
                    "dir,/tmp/pyrotest,root,root,755",
                    "dir,/tmp/pyrotest/data,pyrotest1,pyrogroup1,750",
                    "dir,/tmp/pyrotest/logs,root,pyrogroup1,775",
                    "fl,/tmp/pyrotest/README,pyrotest1,pyrogroup1,644",
                    "ln,/tmp/pyrotest/readme_shortcut,pyrotest1,pyrogroup1,777,/tmp/pyrotest/README"
                ]
            }
        ],
        "Excludes": {
            "Users": [],
            "Groups": [],
            "Devices": [
                "/dev/sda"
            ],
            "Directories": [
                "/proc",
                "/sys",
                "/dev",
                "/boot",
                "/lib",
                "/lib64",
                "/sbin",
                "/usr",
                "/var",
                "/app",
                "/etc",
                "/usr",
                "/root"
            ],
            "Files": [],
            "Links": []
        }
    }
    [ INFO ]: Scanning current machine state (users, groups, filesystem)...
    [ INFO ]: Comparing current system state with Pyro file...
    [ INFO ]: FlowCTRL Sketch - {
        "name": "Pyroform Auto-Generated Sketch User Management Test",
        "Cleanup": [
            {
                "name": "Cleanup extra users",
                "cmd": "# for user in scorchtest sys www-data irc bin daemon proxy lp root list news sync man nobody mail uucp backup _apt games; do userdel -f -r $user; done",
                "setup-cmd": "",
                "on-ok-cmd": "echo 'Eliminated: scorchtest sys www-data irc bin daemon proxy lp root list news sync man nobody mail uucp backup _apt games'",
                "on-nok-cmd": "echo 'Could not scorch extra system users! Details: scorchtest sys www-data irc bin daemon proxy lp root list news sync man nobody mail uucp backup _apt games'",
                "fatal-nok": false
            },
            {
                "name": "Cleanup extra groups",
                "cmd": "# for group in scorchtest pyrotest1 nogroup pyrotest2; do groupdel $group; done",
                "setup-cmd": "",
                "on-ok-cmd": "echo 'Eliminated: scorchtest pyrotest1 nogroup pyrotest2'",
                "on-nok-cmd": "echo 'Could not scorch extra system groups! Details: scorchtest pyrotest1 nogroup pyrotest2'",
                "fatal-nok": false
            },
            {
                "name": "Cleanup extra directories",
                "cmd": "# rm -rf /tmp /tmp/flow_ctrl /mnt /home/pyrotest2 /home /opt /run/lock /home/pyrotest1 /run /srv /media",
                "setup-cmd": "",
                "on-ok-cmd": "echo 'Eliminated: /tmp /tmp/flow_ctrl /mnt /home/pyrotest2 /home /opt /run/lock /home/pyrotest1 /run /srv /media'",
                "on-nok-cmd": "echo 'Could not scorch extra directories! Details: /tmp /tmp/flow_ctrl /mnt /home/pyrotest2 /home /opt /run/lock /home/pyrotest1 /run /srv /media'",
                "fatal-nok": false
            },
            {
                "name": "Cleanup extra files and links",
                "cmd": "# rm -f /home/pyrotest2/.bash_logout /tmp/flow_ctrl/flow-ctrl.log /home/pyrotest2/.profile /home/pyrotest1/.bash_logout /tmp/shall_not_be_scorched.dummy /home/pyrotest1/.profile /.dockerenv /home/pyrotest2/.bashrc /home/pyrotest1/.bashrc /run/adduser /.pyroflow.state /var/run /var/lock /proc/1/task/1/root /proc/1306/task/1306/root /proc/1307/root /proc/1307/task/1307/root /proc/1/root /proc/1306/root",
                "setup-cmd": "",
                "on-ok-cmd": "echo 'Eliminated: /home/pyrotest2/.bash_logout /tmp/flow_ctrl/flow-ctrl.log /home/pyrotest2/.profile /home/pyrotest1/.bash_logout /tmp/shall_not_be_scorched.dummy /home/pyrotest1/.profile /.dockerenv /home/pyrotest2/.bashrc /home/pyrotest1/.bashrc /run/adduser /.pyroflow.state /var/run /var/lock /proc/1/task/1/root /proc/1306/task/1306/root /proc/1307/root /proc/1307/task/1307/root /proc/1/root /proc/1306/root'",
                "on-nok-cmd": "echo 'Could not scorch extra files and links! Details: /home/pyrotest2/.bash_logout /tmp/flow_ctrl/flow-ctrl.log /home/pyrotest2/.profile /home/pyrotest1/.bash_logout /tmp/shall_not_be_scorched.dummy /home/pyrotest1/.profile /.dockerenv /home/pyrotest2/.bashrc /home/pyrotest1/.bashrc /run/adduser /.pyroflow.state /var/run /var/lock /proc/1/task/1/root /proc/1306/task/1306/root /proc/1307/root /proc/1307/task/1307/root /proc/1/root /proc/1306/root'",
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
    [ INFO ]: Processing stage: Cleanup
    [ INFO ]: Processing action: Cleanup extra users
    [ INFO ]: Executing Procedure Stage Action: Cleanup extra users
    CMD> # for user in scorchtest sys www-data irc bin daemon proxy lp root list news sync man nobody mail uucp backup _apt games; do userdel -f -r $user; done


    CMD> echo 'Eliminated: scorchtest sys www-data irc bin daemon proxy lp root list news sync man nobody mail uucp backup _apt games'
    Eliminated: scorchtest sys www-data irc bin daemon proxy lp root list news sync man nobody mail uucp backup _apt games

    [ OK ]: Action completed: Cleanup extra users
    [ INFO ]: Processing action: Cleanup extra groups
    [ INFO ]: Executing Procedure Stage Action: Cleanup extra groups
    CMD> # for group in scorchtest pyrotest1 nogroup pyrotest2; do groupdel $group; done


    CMD> echo 'Eliminated: scorchtest pyrotest1 nogroup pyrotest2'
    Eliminated: scorchtest pyrotest1 nogroup pyrotest2

    [ OK ]: Action completed: Cleanup extra groups
    [ INFO ]: Processing action: Cleanup extra directories
    [ INFO ]: Executing Procedure Stage Action: Cleanup extra directories
    CMD> # rm -rf /tmp /tmp/flow_ctrl /mnt /home/pyrotest2 /home /opt /run/lock /home/pyrotest1 /run /srv /media


    CMD> echo 'Eliminated: /tmp /tmp/flow_ctrl /mnt /home/pyrotest2 /home /opt /run/lock /home/pyrotest1 /run /srv /media'
    Eliminated: /tmp /tmp/flow_ctrl /mnt /home/pyrotest2 /home /opt /run/lock /home/pyrotest1 /run /srv /media

    [ OK ]: Action completed: Cleanup extra directories
    [ INFO ]: Processing action: Cleanup extra files and links
    [ INFO ]: Executing Procedure Stage Action: Cleanup extra files and links
    CMD> # rm -f /home/pyrotest2/.bash_logout /tmp/flow_ctrl/flow-ctrl.log /home/pyrotest2/.profile /home/pyrotest1/.bash_logout /tmp/shall_not_be_scorched.dummy /home/pyrotest1/.profile /.dockerenv /home/pyrotest2/.bashrc /home/pyrotest1/.bashrc /run/adduser /.pyroflow.state /var/run /var/lock /proc/1/task/1/root /proc/1306/task/1306/root /proc/1307/root /proc/1307/task/1307/root /proc/1/root /proc/1306/root


    CMD> echo 'Eliminated: /home/pyrotest2/.bash_logout /tmp/flow_ctrl/flow-ctrl.log /home/pyrotest2/.profile /home/pyrotest1/.bash_logout /tmp/shall_not_be_scorched.dummy /home/pyrotest1/.profile /.dockerenv /home/pyrotest2/.bashrc /home/pyrotest1/.bashrc /run/adduser /.pyroflow.state /var/run /var/lock /proc/1/task/1/root /proc/1306/task/1306/root /proc/1307/root /proc/1307/task/1307/root /proc/1/root /proc/1306/root'
    Eliminated: /home/pyrotest2/.bash_logout /tmp/flow_ctrl/flow-ctrl.log /home/pyrotest2/.profile /home/pyrotest1/.bash_logout /tmp/shall_not_be_scorched.dummy /home/pyrotest1/.profile /.dockerenv /home/pyrotest2/.bashrc /home/pyrotest1/.bashrc /run/adduser /.pyroflow.state /var/run /var/lock /proc/1/task/1/root /proc/1306/task/1306/root /proc/1307/root /proc/1307/task/1307/root /proc/1/root /proc/1306/root

    [ OK ]: Action completed: Cleanup extra files and links
    [ OK ]: Stage completed: Cleanup
    [ OK ]: Procedure completed: SUCCESS
```

## 5. Analize output to ensure new user and file should have been scorched
```text
    ...
    [ INFO ]: FlowCTRL Sketch - {
        "name": "Pyroform Auto-Generated Sketch User Management Test",
        "Cleanup": [
            {
                "name": "Cleanup extra users",
                "cmd": "# for user in scorchtest sys www-data irc bin daemon proxy lp root list news sync man nobody mail uucp backup _apt games; do userdel -f -r $user; done",
                ...
            },
            ...
            {
                "name": "Cleanup extra files and links",
                "cmd": "# rm -f /home/pyrotest2/.bash_logout /tmp/flow_ctrl/flow-ctrl.log /home/pyrotest2/.profile /home/pyrotest1/.bash_logout /tmp/shall_not_be_scorched.dummy /home/pyrotest1/.profile /.dockerenv /home/pyrotest2/.bashrc /home/pyrotest1/.bashrc /run/adduser /.pyroflow.state /var/run /var/lock /proc/1/task/1/root /proc/1306/task/1306/root /proc/1307/root /proc/1307/task/1307/root /proc/1/root /proc/1306/root",
                ...
            }
        ]
    }
    ...
```

## 6. Verify user and file have not actually been removed
```text
    root@1e1b62138bef:/app/Pyroform# id scorchtest
    uid=1002(scorchtest) gid=1004(scorchtest) groups=1004(scorchtest)

    root@1e1b62138bef:/app/Pyroform# ls -allah /tmp/shall_not_be_scorched.dummy
    -rw-r--r-- 1 root root 0 Nov 22 22:09 /tmp/shall_not_be_scorched.dummy
```


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

