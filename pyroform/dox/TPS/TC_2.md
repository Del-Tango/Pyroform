ID: TC-2 / Invalid CLI Usage
Priority: High
Description: Verify error handling for invalid CLI usage
Preconditions: Pyroform installed in test environment

Test Steps:

1. Run commands
```bash
~$ pyroform (no arguments)
~$ pyroform invalid-command
~$ pyroform configure --invalid-flag
~$ pyroform configure (no input file)
~$ pyroform --configure --scorch (multiple actions)
```

Expected Results:

- Appropriate error messages for invalid usage
- Clear guidance on correct usage
- Non-zero exit codes for errors
