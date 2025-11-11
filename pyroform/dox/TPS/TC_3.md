ID: TC-3 / YAML Configuration Parsing
Priority: High
Description: Test YAML configuration file parsing
Preconditions:

Test Data (test_config.yaml):
```yaml
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

Test Steps:

1. Create test_config.yaml with above content and run commands
2. Run commands
```bash
~$ pyroform validate -i test_config.yaml
~$ pyroform configure -i test_config.yaml --dry-run
```

Expected Results:

- YAML file parsed without errors
- Configuration object created correctly
- Dry-run completes successfully
