# TC-3 / YAML Configuration Parsing

- Test Environment: Docker container with Amazon Linux 2023.6.20241121 6.6.15-amd64
- Tester: D:Ta
- Date: 11/11/2025
- Pyroform Version: 1.0.0
- Status: [ ] PASS [X] FAIL [ ] BLOCKED

# Remarks

- Pyro file (YAML) validation failed at step 2:
    - Action 'validate' cannot be given as sub-command, only option flag (e.g. --validate);
    - No explicit reason given for failure, at least not upfront;
    - Debug flag did apparently nothing. Expected verbosity level to increase;
- Pyro file (YAML) configuration failed at step 3:
    - Action 'configure' cannot be given as sub-command, only option flag (e.g. --configure)
    - Dry-run cannot be configured via CLI, only config file.

# Archive

## 1. Create dummy Pyro file
```text
    bash-5.2# cat test_config.pyro.yaml
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

## 2. Run validation command using previously created Pyro file
```text
    bash-5.2# pyroform validate -i dump/test_config.yaml
    Usage: pyroform [OPTIONS]
    Try 'pyroform --help' for help.

    Error: Got unexpected extra argument (validate)

    bash-5.2# echo $?
    2
```

### Miscellaneous
```text
    bash-5.2# pyroform --validate -i test_config.pyro.yaml

        ___________________________________________________________________________

        *                          *   Pyroform   *                           *
        ___________________________________________________________________________
                        Regards, the Alveare Solutions #!/Society -x

    Executing validate action with input: test_config.pyro.yaml
    Validate action failed
```

## 3. Dry-run of configuration
```text
    bash-5.2# pyroform --configure -i test_config.pyro.yaml --dry-run
    Usage: pyroform [OPTIONS]
    Try 'pyroform --help' for help.

    Error: No such option: --dry-run
```

### Miscellaneous
```text
    bash-5.2# pyroform configure -i test_config.yaml
    Usage: pyroform [OPTIONS]
    Try 'pyroform --help' for help.

    Error: Got unexpected extra argument (configure)


    bash-5.2# pyroform --configure -i test_config.pyro.yaml

        ___________________________________________________________________________

        *                          *   Pyroform   *                           *
        ___________________________________________________________________________
                        Regards, the Alveare Solutions #!/Society -x

    Executing configure action with input: test_config.pyro.yaml
    Configure action completed successfully
```
