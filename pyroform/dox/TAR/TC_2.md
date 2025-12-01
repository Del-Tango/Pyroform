# Invalid CLI Usage
- Test Environment: Docker container with Debian GNU/Linux 13 (trixie) 6.6.15-amd64
- Tester: D:Ta
- Date: 01/12/2025
- Pyroform Version: 1.0.0
- Validates: [TPS TC_2](../TPS/TC_2.md)
- Status:
[X] PASS
[ ] FAIL
[ ] BLOCKED

# Remarks
N/A

# Archive

## 1. No arguments
```text
    root@1e1b62138bef:/app/Pyroform# pyroform

        ___________________________________________________________________________

        *                          *   Pyroform   *                           *
        ___________________________________________________________________________
                        Regards, the Alveare Solutions #!/Society -x

    Usage: pyroform [OPTIONS] COMMAND [ARGS]...

    Pyroform Linux Configurator

    A tool that receives input file(s) containing list of users, user groups,
    block storage device mountpoints, files and directories with owners and
    permissions, generates on the fly FlowCTRL sketch files based on input pyro
    file(s), and runs them using the flow_ctrl library.

    Options:
    --version  Display PyrDisplay Pyroform  version
    --help     Show this message and exit.

    Commands:
    configure  Configure system according to Pyro file(s)
    mount      Mount devices according to Pyro file(s)
    scorch     Remove system resources not specified in Pyro file(s)
    snapshot   Validate system against Pyro file(s)
    validate   Validate system against Pyro file(s)
    workflow   Execute a complete Pyroform workflow from configuration file

    root@1e1b62138bef:/app/Pyroform# echo $?
    2
```

## 2. Invalid action
```text
    root@1e1b62138bef:/app/Pyroform# pyroform invalid-command

        ___________________________________________________________________________

        *                          *   Pyroform   *                           *
        ___________________________________________________________________________
                        Regards, the Alveare Solutions #!/Society -x

    Usage: pyroform [OPTIONS] COMMAND [ARGS]...
    Try 'pyroform --help' for help.

    Error: No such command 'invalid-command'.

    root@1e1b62138bef:/app/Pyroform# echo $?
    2
```

## 3. Invalid option flag
```text
    root@1e1b62138bef:/app/Pyroform# pyroform configure --invalid-flag
    Usage: pyroform configure [OPTIONS]
    Try 'pyroform configure --help' for help.

    Error: No such option: --invalid-flag

    root@1e1b62138bef:/app/Pyroform# echo $?
    2
```

## 4. Incomplete command
```text
    root@1e1b62138bef:/app/Pyroform# pyroform configure
    Usage: pyroform configure [OPTIONS]
    Try 'pyroform configure --help' for help.

    Error: Missing option '-i' / '--input'.

    root@1e1b62138bef:/app/Pyroform# echo $?
    2
```

## 5. Multiple actions
```text
    root@1e1b62138bef:/app/Pyroform# pyroform configure scorch
    Usage: pyroform configure [OPTIONS]
    Try 'pyroform configure --help' for help.

    Error: Missing option '-i' / '--input'.

    root@1e1b62138bef:/app/Pyroform# echo $?
    2
```
