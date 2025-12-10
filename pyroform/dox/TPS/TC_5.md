# Invalid Configuration Files
- Priority: Medium
- Description: Test error handling for invalid configuration files
- Preconditions:
- Validated by: [TAR TC_5](../TAR/TC_5.md)

## Test Data:

### Pyro file with invalid JSON syntax (invalid_syntax.pyro.json)
```json
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

### Pyro file with invalid YAML syntax (invalid_syntax.pyro.yaml)
```yaml
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

### Pyro file with missing required fields (missing_fields.pyro.yaml)
```yaml
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

### Pyro file with invalid field types (invalid_fields.pyro.yaml)
```yaml
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

## Test Steps:

1. Create file with invalid YAML syntax (invalid_syntax.pyro.yaml)
2. Create file with invalid JSON syntax (invalid_syntax.pyro.json)
3. Create file missing required fields  (missing_fields.pyro.yaml)
4. Create file with invalid field types (invalid_fields.pyro.yaml)
5. Attempt to parse each with pyroform validate commands
```bash
~$ pyroform validate -i invalid_syntax.pyro.yaml
~$ pyroform validate -i invalid_syntax.pyro.json
~$ pyroform validate -i missing_fields.pyro.yaml
~$ pyroform validate -i invalid_fields.pyro.yaml
```

## Expected Results:

- Clear error messages for syntax errors
- Validation fails for missing required fields
- Type errors reported appropriately
