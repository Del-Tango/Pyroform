# Error Handing of Invalid Pyro Files
- Test Environment: Docker container with Debian GNU/Linux 13 (trixie) 6.6.15-amd64
- Tester: D:Ta
- Date: 01/12/2025
- Pyroform Version: 1.0.0
- Validates: [TPS TC_5](../TPS/TC_5.md)
- Status:
[X] PASS
[ ] FAIL
[ ] BLOCKED

# Archive

## 1. Create Pyro file with invalid JSON syntax (invalid_syntax.pyro.json)
```yaml
{
  "Label": "Test Invalid JSON Syntax Configuration",
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

## 2.Create Pyro file with invalid YAML syntax (invalid_syntax.pyro.yaml)
```json
Label: "Test Invalid YAML Syntax Configuration"
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

## 3. Create Pyro file with missing required fields (missing_fields.pyro.yaml)
```text
Label: "Test Missing Fields YAML Configuration"
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

## 4. Create Pyro file with invalid fied types (invalid_fields.pyro.yaml)
```text
Label: "Test Invalid Fields YAML Configuration"
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
root@1e1b62138bef:/app/Pyroform# pyroform validate -i invalid_syntax.pyro.yaml

    ___________________________________________________________________________

      *                          *   Pyroform   *                           *
    ___________________________________________________________________________
                    Regards, the Alveare Solutions #!/Society -x


[ INFO ]: Logging configured: /usr/local/lib/python3.13/dist-packages/log/pyroflow/pyroflow.log
[ INFO ]: State monitoring configured for inter-process control
[ INFO ]: Parsing Pyro state file (invalid_syntax.pyro.yaml)...
[ ERROR ]: Validation failed: while scanning a simple key
  in "invalid_syntax.pyro.yaml", line 7, column 1
could not find expected ':'
  in "invalid_syntax.pyro.yaml", line 8, column 10
```

```text
root@1e1b62138bef:/app/Pyroform# pyroform validate -i invalid_syntax.pyro.json 2> /dev/null

    ___________________________________________________________________________

      *                          *   Pyroform   *                           *
    ___________________________________________________________________________
                    Regards, the Alveare Solutions #!/Society -x


[ INFO ]: Logging configured: /usr/local/lib/python3.13/dist-packages/log/pyroflow/pyroflow.log
[ INFO ]: State monitoring configured for inter-process control
[ INFO ]: Parsing Pyro state file (invalid_syntax.pyro.json)...
[ ERROR ]: Validation failed: Illegal trailing comma before end of object: line 8 column 30 (char 186)
```

```text
root@1e1b62138bef:/app/Pyroform# pyroform validate -i missing_fields.pyro.yaml 2> /dev/null

    ___________________________________________________________________________

      *                          *   Pyroform   *                           *
    ___________________________________________________________________________
                    Regards, the Alveare Solutions #!/Society -x


[ INFO ]: Logging configured: /usr/local/lib/python3.13/dist-packages/log/pyroflow/pyroflow.log
[ INFO ]: State monitoring configured for inter-process control
[ INFO ]: Parsing Pyro state file (missing_fields.pyro.yaml)...
[ ERROR ]: Validation failed: 'str' object has no attribute 'get'
```

```text
root@1e1b62138bef:/app/Pyroform# pyroform validate -i invalid_fields.pyro.yaml 2> /dev/null

    ___________________________________________________________________________

      *                          *   Pyroform   *                           *
    ___________________________________________________________________________
                    Regards, the Alveare Solutions #!/Society -x


[ INFO ]: Logging configured: /usr/local/lib/python3.13/dist-packages/log/pyroflow/pyroflow.log
[ INFO ]: State monitoring configured for inter-process control
[ INFO ]: Parsing Pyro state file (invalid_fields.pyro.yaml)...
[ INFO ]: State file data: {
    "Label": "Test Invalid Fields YAML Configuration",
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
[ INFO ]: Scanning current machine state (users, groups, filesystem)...
[ INFO ]: Comparing current system state with Pyro file...
[ ERROR ]: Validation failed: 'int' object is not iterable
```
