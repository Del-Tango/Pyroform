ID: TC-5 / Invalid Configuration Files
Priority: Medium
Description: Test error handling for invalid configuration files
Preconditions:

Test Steps:

1. Create file with invalid YAML syntax
2. Create file with invalid JSON syntax
3. Create file missing required fields
4. Create file with invalid field types
5. Attempt to parse each with pyroform validate
```bash
~$ pyroform validate -i test_invalid.pyro.yaml
```

Expected Results:

- Clear error messages for syntax errors
- Validation fails for missing required fields
- Type errors reported appropriately
