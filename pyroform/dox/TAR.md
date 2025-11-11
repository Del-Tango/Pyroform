# Test Archive

# [ Description ]: Pyroform Test Archive

- Objective: Archive of Pyroform manual testing functionalities as described in the TPS.
- Scope: CLI interface, configuration parsing, system operations, error handling, and safety features.
- Environment: Clean Docker container with Debian image.

--------------------------------------------------------------------------------

# [ TC 1 ]: CLI Help and Version

- Test Environment: Docker container with Amazon Linux 2023.6.20241121 6.6.15-amd64
- Tester: D:Ta
- Date: 11/11/2025
- Pyroform Version: 1.0.0
- Validates: [TPS TC_1](./TPS/TC_1.md)
- Status: [X] PASS [ ] FAIL [ ] BLOCKED

# Remarks

- Help messages on action sub-commands would be betters suited if they addressed only the action in question.

# Archive:

## 1. Display Version
```text
    bash-5.2# pyroform --version

        ___________________________________________________________________________

        *                          *   Pyroform   *                           *
        ___________________________________________________________________________
                        Regards, the Alveare Solutions #!/Society -x

    Pyroform version 1.0.0
```

## 2. Display Help
```text
    bash-5.2# pyroform --help

        ___________________________________________________________________________

        *                          *   Pyroform   *                           *
        ___________________________________________________________________________
                        Regards, the Alveare Solutions #!/Society -x

    Usage: pyroform [OPTIONS]

    Pyroform Linux Configurator

    Options:
    -S, --scorch            Trigger action scorch using input Pyro file(s)
    -M, --mount             Trigger action mount using input Pyro file(s)
    -C, --configure         Trigger action configure using input Pyro file(s)
    -V, --validate          Trigger action validate using input Pyro file(s)
    -i, --input PATH        Path to Pyro file (JSON|YAML) or directory
                            containing Pyro files
    -o, --output PATH       Path to FlowCTRL sketch file (JSON) or directory for
                            generated files
    -c, --config-file PATH  Path to Pyroform config file (JSON|YAML)
    -l, --log-file PATH     Path to Pyroform and FlowCTRL log file
    -r, --dump-report       Flag to generate report file with STDOUT, STDERR
                            plus summary
    -s, --silent            Flag to suppress STDOUT
    -d, --debug             Flag that makes logging and STDOUT messages more
                            verbose
    -v, --version           Action that displays Pyroform version
    -y, --yes               Flag to confirm all manual prompts such that manual
                            interaction from user is not required
    --help                  Show this message and exit.


    bash-5.2# pyroform configure --help

        ___________________________________________________________________________

        *                          *   Pyroform   *                           *
        ___________________________________________________________________________
                        Regards, the Alveare Solutions #!/Society -x

    Usage: pyroform [OPTIONS]

    Pyroform Linux Configurator

    Options:
    -S, --scorch            Trigger action scorch using input Pyro file(s)
    -M, --mount             Trigger action mount using input Pyro file(s)
    -C, --configure         Trigger action configure using input Pyro file(s)
    -V, --validate          Trigger action validate using input Pyro file(s)
    -i, --input PATH        Path to Pyro file (JSON|YAML) or directory
                            containing Pyro files
    -o, --output PATH       Path to FlowCTRL sketch file (JSON) or directory for
                            generated files
    -c, --config-file PATH  Path to Pyroform config file (JSON|YAML)
    -l, --log-file PATH     Path to Pyroform and FlowCTRL log file
    -r, --dump-report       Flag to generate report file with STDOUT, STDERR
                            plus summary
    -s, --silent            Flag to suppress STDOUT
    -d, --debug             Flag that makes logging and STDOUT messages more
                            verbose
    -v, --version           Action that displays Pyroform version
    -y, --yes               Flag to confirm all manual prompts such that manual
                            interaction from user is not required
    --help                  Show this message and exit.


    bash-5.2# pyroform scorch --help

        ___________________________________________________________________________

        *                          *   Pyroform   *                           *
        ___________________________________________________________________________
                        Regards, the Alveare Solutions #!/Society -x

    Usage: pyroform [OPTIONS]

    Pyroform Linux Configurator

    Options:
    -S, --scorch            Trigger action scorch using input Pyro file(s)
    -M, --mount             Trigger action mount using input Pyro file(s)
    -C, --configure         Trigger action configure using input Pyro file(s)
    -V, --validate          Trigger action validate using input Pyro file(s)
    -i, --input PATH        Path to Pyro file (JSON|YAML) or directory
                            containing Pyro files
    -o, --output PATH       Path to FlowCTRL sketch file (JSON) or directory for
                            generated files
    -c, --config-file PATH  Path to Pyroform config file (JSON|YAML)
    -l, --log-file PATH     Path to Pyroform and FlowCTRL log file
    -r, --dump-report       Flag to generate report file with STDOUT, STDERR
                            plus summary
    -s, --silent            Flag to suppress STDOUT
    -d, --debug             Flag that makes logging and STDOUT messages more
                            verbose
    -v, --version           Action that displays Pyroform version
    -y, --yes               Flag to confirm all manual prompts such that manual
                            interaction from user is not required
    --help                  Show this message and exit.


    bash-5.2# pyroform mount --help

        ___________________________________________________________________________

        *                          *   Pyroform   *                           *
        ___________________________________________________________________________
                        Regards, the Alveare Solutions #!/Society -x

    Usage: pyroform [OPTIONS]

    Pyroform Linux Configurator

    Options:
    -S, --scorch            Trigger action scorch using input Pyro file(s)
    -M, --mount             Trigger action mount using input Pyro file(s)
    -C, --configure         Trigger action configure using input Pyro file(s)
    -V, --validate          Trigger action validate using input Pyro file(s)
    -i, --input PATH        Path to Pyro file (JSON|YAML) or directory
                            containing Pyro files
    -o, --output PATH       Path to FlowCTRL sketch file (JSON) or directory for
                            generated files
    -c, --config-file PATH  Path to Pyroform config file (JSON|YAML)
    -l, --log-file PATH     Path to Pyroform and FlowCTRL log file
    -r, --dump-report       Flag to generate report file with STDOUT, STDERR
                            plus summary
    -s, --silent            Flag to suppress STDOUT
    -d, --debug             Flag that makes logging and STDOUT messages more
                            verbose
    -v, --version           Action that displays Pyroform version
    -y, --yes               Flag to confirm all manual prompts such that manual
                            interaction from user is not required
    --help                  Show this message and exit.


    bash-5.2# pyroform validate --help

        ___________________________________________________________________________

        *                          *   Pyroform   *                           *
        ___________________________________________________________________________
                        Regards, the Alveare Solutions #!/Society -x

    Usage: pyroform [OPTIONS]

    Pyroform Linux Configurator

    Options:
    -S, --scorch            Trigger action scorch using input Pyro file(s)
    -M, --mount             Trigger action mount using input Pyro file(s)
    -C, --configure         Trigger action configure using input Pyro file(s)
    -V, --validate          Trigger action validate using input Pyro file(s)
    -i, --input PATH        Path to Pyro file (JSON|YAML) or directory
                            containing Pyro files
    -o, --output PATH       Path to FlowCTRL sketch file (JSON) or directory for
                            generated files
    -c, --config-file PATH  Path to Pyroform config file (JSON|YAML)
    -l, --log-file PATH     Path to Pyroform and FlowCTRL log file
    -r, --dump-report       Flag to generate report file with STDOUT, STDERR
                            plus summary
    -s, --silent            Flag to suppress STDOUT
    -d, --debug             Flag that makes logging and STDOUT messages more
                            verbose
    -v, --version           Action that displays Pyroform version
    -y, --yes               Flag to confirm all manual prompts such that manual
                            interaction from user is not required
    --help                  Show this message and exit.



    bash-5.2# pyroform workflow --help

        ___________________________________________________________________________

        *                          *   Pyroform   *                           *
        ___________________________________________________________________________
                        Regards, the Alveare Solutions #!/Society -x

    Usage: pyroform [OPTIONS]

    Pyroform Linux Configurator

    Options:
    -S, --scorch            Trigger action scorch using input Pyro file(s)
    -M, --mount             Trigger action mount using input Pyro file(s)
    -C, --configure         Trigger action configure using input Pyro file(s)
    -V, --validate          Trigger action validate using input Pyro file(s)
    -i, --input PATH        Path to Pyro file (JSON|YAML) or directory
                            containing Pyro files
    -o, --output PATH       Path to FlowCTRL sketch file (JSON) or directory for
                            generated files
    -c, --config-file PATH  Path to Pyroform config file (JSON|YAML)
    -l, --log-file PATH     Path to Pyroform and FlowCTRL log file
    -r, --dump-report       Flag to generate report file with STDOUT, STDERR
                            plus summary
    -s, --silent            Flag to suppress STDOUT
    -d, --debug             Flag that makes logging and STDOUT messages more
                            verbose
    -v, --version           Action that displays Pyroform version
    -y, --yes               Flag to confirm all manual prompts such that manual
                            interaction from user is not required
    --help                  Show this message and exit.
```

--------------------------------------------------------------------------------

# [ TC 2 ]: Invalid CLI Usage

- Test Environment: Docker container with Amazon Linux 2023.6.20241121 6.6.15-amd64
- Tester: D:Ta
- Date: 11/11/2025
- Pyroform Version: 1.0.0
- Validates: [TPS TC_2](./TPS/TC_2.md)
- Status: [x] PASS [ ] FAIL [ ] BLOCKED

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

--------------------------------------------------------------------------------

# [ TC 3 ]: YAML Configuration Parsing

- Test Environment: Docker container with Amazon Linux 2023.6.20241121 6.6.15-amd64
- Tester: D:Ta
- Date: 11/11/2025
- Pyroform Version: 1.0.0
- Validates: [TPS TC_3](./TPS/TC_3.md)
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

--------------------------------------------------------------------------------

# [ TC 4 ]: Test Environment:

Tester:
Date:
Pyroform Version:
Status: [ ] PASS [ ] FAIL [ ] BLOCKED

Archive

--------------------------------------------------------------------------------

# [ TC 5 ]: Test Environment:

Tester:
Date:
Pyroform Version:
Status: [ ] PASS [ ] FAIL [ ] BLOCKED

Archive

--------------------------------------------------------------------------------

# [ TC 6 ]: Test Environment:

Tester:
Date:
Pyroform Version:
Status: [ ] PASS [ ] FAIL [ ] BLOCKED

Archive

--------------------------------------------------------------------------------

# [ TC 7 ]: Test Environment:

Tester:
Date:
Pyroform Version:
Status: [ ] PASS [ ] FAIL [ ] BLOCKED

Archive

--------------------------------------------------------------------------------

# [ TC 8 ]: Test Environment:

Tester:
Date:
Pyroform Version:
Status: [ ] PASS [ ] FAIL [ ] BLOCKED

Archive

--------------------------------------------------------------------------------

# [ TC 9 ]: Test Environment:

Tester:
Date:
Pyroform Version:
Status: [ ] PASS [ ] FAIL [ ] BLOCKED

Archive

--------------------------------------------------------------------------------

# [ TC 10 ]: Test Environment:

Tester:
Date:
Pyroform Version:
Status: [ ] PASS [ ] FAIL [ ] BLOCKED

Archive

--------------------------------------------------------------------------------

# [ TC 11 ]: Test Environment:

Tester:
Date:
Pyroform Version:
Status: [ ] PASS [ ] FAIL [ ] BLOCKED

Archive

--------------------------------------------------------------------------------

# [ TC 12 ]: Test Environment:

Tester:
Date:
Pyroform Version:
Status: [ ] PASS [ ] FAIL [ ] BLOCKED

Archive

--------------------------------------------------------------------------------

# [ TC 13 ]: Test Environment:

Tester:
Date:
Pyroform Version:
Status: [ ] PASS [ ] FAIL [ ] BLOCKED

Archive

--------------------------------------------------------------------------------

# [ TC 14 ]: Test Environment:

Tester:
Date:
Pyroform Version:
Status: [ ] PASS [ ] FAIL [ ] BLOCKED

Archive

--------------------------------------------------------------------------------

# [ TC 15 ]: Test Environment:

Tester:
Date:
Pyroform Version:
Status: [ ] PASS [ ] FAIL [ ] BLOCKED

Archive

--------------------------------------------------------------------------------

# [ TC 16 ]: Test Environment:

Tester:
Date:
Pyroform Version:
Status: [ ] PASS [ ] FAIL [ ] BLOCKED

Archive

--------------------------------------------------------------------------------

# [ Conclusion ]: Overview

## Overall Status:
- [ ] READY FOR PRODUCTION
- [ ] NEEDS FIXES
- [ ] NOT READY

## Critical Issues Found
N/A

## Recommendations
N/A

