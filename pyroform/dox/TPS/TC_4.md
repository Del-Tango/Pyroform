ID: TC-4 / JSON Configuration Parsing
Priority: High
Description: Test JSON configuration file parsing
Preconditions:

Test Data (test_config.json):
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

Test Steps:

1. Create test_config.json with above content
2. Run commands
```bash
~$ pyroform validate -i test_config.json
~$ pyroform configure -i test_config.json --dry-run
```

Expected Results:

- JSON file parsed without errors
- Configuration object created correctly
- Dry-run completes successfully
