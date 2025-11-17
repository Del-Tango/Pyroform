# JSON Configuration Parsing
- Priority: High
- Description: Test JSON configuration file parsing
- Preconditions:
- Validated by: [TAR TC_4](../TAR/TC_4.md)

## Test Data (test_config.pyro.json):
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

## Test Steps:

1. Create test_config.pyro.json with above content
2. Run validation command
```bash
~$ pyroform validate -i test_config.pyro.json
```
3. Run configuration command with dry-run flag
```bash
~$ pyroform configure -i test_config.pyro.json --dry-run
```

## Expected Results:

- JSON file parsed without errors
- Configuration object created correctly
- Dry-run completes successfully
