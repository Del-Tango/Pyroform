# Error Handing of Invalid Pyro Files
- Test Environment: Docker container with Amazon Linux 2023.6.20241121 6.6.15-amd64
- Tester: D:Ta
- Date: 16/11/2025
- Pyroform Version: 1.0.0
- Validates: [TPS TC_5](../TPS/TC_5.md)
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
