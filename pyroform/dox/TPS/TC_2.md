ID: TC-2 / Invalid CLI Usage
Priority: High
Description: Verify error handling for invalid CLI usage
Preconditions: Pyroform installed in test environment

Test Steps:

1. Run command with no arguments
```bash
~$ pyroform
~$ echo $?
```
2. Run command with invalid action
```bash
~$ pyroform invalid-command
~$ echo $?
```
3. Run command with invalid option flag
```bash
~$ pyroform configure --invalid-flag
~$ echo $?
```
4. Run incomplete command with no Pyro file
```bash
~$ pyroform configure
~$ echo $?
```
5. Run command with multiple actions
```
~$ pyroform --configure --scorch
~$ echo $?
```

Expected Results:

- Appropriate error messages for invalid usage
- Clear guidance on correct usage
- Non-zero exit codes for errors
