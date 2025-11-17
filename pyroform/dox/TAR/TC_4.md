# JSON Configuration Parsing
- Test Environment: Docker container with Amazon Linux 2023.6.20241121 6.6.15-amd64
- Tester: D:Ta
- Date: 16/11/2025
- Pyroform Version: 1.0.0
- Validates: [TPS TC_4](../TPS/TC_4.md)
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
