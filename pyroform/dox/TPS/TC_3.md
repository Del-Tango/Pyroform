# YAML Configuration Parsing
- Priority: High
- Description: Test YAML configuration file parsing
- Preconditions:
- Validated by: [TAR TC_3](../TAR/TC_3.md)

## Test Data (test_config.pyro.yaml):
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

## Test Steps:

1. Create test_config.pyro.yaml with above content and run commands
2. Run validation command
```bash
~$ pyroform validate -i test_config.pyro.yaml
```
3. Run dry-run configuration command
```bash
~$ pyroform configure -i test_config.pyro.yaml --dry-run
```

## Expected Results:

- YAML file parsed without errors
- Configuration object created correctly
- Dry-run completes successfully
