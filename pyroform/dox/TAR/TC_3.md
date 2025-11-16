# YAML Configuration Parsing
- Test Environment: Docker container with Amazon Linux 2023.6.20241121 6.6.15-amd64
- Tester: D:Ta
- Date: 16/11/2025, 14/11/2025, 11/11/2025
- Pyroform Version: 1.0.0
- Validates: [TPS TC_3](../TPS/TC_3.md)
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

