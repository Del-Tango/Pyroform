# Invalid CLI Usage
- Test Environment: Docker container with Amazon Linux 2023.6.20241121 6.6.15-amd64
- Tester: D:Ta
- Date: 11/11/2025
- Pyroform Version: 1.0.0
- Validates: [TPS TC_2](../TPS/TC_2.md)
- Status:
[x] PASS
[ ] FAIL
[ ] BLOCKED

# Remarks

- Case 4 should have better error messages. In it's current form can be missleading.

# Archive

## 1. No arguments
```text
    bash-5.2# pyroform

        ___________________________________________________________________________

        *                          *   Pyroform   *                           *
        ___________________________________________________________________________
                        Regards, the Alveare Solutions #!/Society -x

    Usage: pyroform [OPTIONS]
    Try 'pyroform --help' for help.

    Error: No action specified. Use --scorch, --mount, --configure, or --validate

    bash-5.2# echo $?
    2
```

## 2. Invalid action
```text
    bash-5.2# pyroform invalid-command
    Usage: pyroform [OPTIONS]
    Try 'pyroform --help' for help.

    Error: Got unexpected extra argument (invalid-command)

    bash-5.2# echo $?
    2
```

## 3. Invalid option flag
```text
    bash-5.2# pyroform configure --invalid-flag
    Usage: pyroform [OPTIONS]
    Try 'pyroform --help' for help.

    Error: No such option: --invalid-flag Did you mean --validate?

    bash-5.2# echo $?
    2
```

## 4. Incomplete command
```text
    bash-5.2# pyroform configure
    Usage: pyroform [OPTIONS]
    Try 'pyroform --help' for help.

    Error: Got unexpected extra argument (configure)

    bash-5.2# echo $?
    2
```

## 5. Multiple actions
```text
    bash-5.2# pyroform --configure --scorch

        ___________________________________________________________________________

        *                          *   Pyroform   *                           *
        ___________________________________________________________________________
                        Regards, the Alveare Solutions #!/Society -x

    Usage: pyroform [OPTIONS]
    Try 'pyroform --help' for help.

    Error: Exactly one action must be specified: --scorch, --mount, --configure, or --validate

    bash-5.2# echo $?
    2
```
