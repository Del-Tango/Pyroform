# CLI Help and Version
- Test Environment: Docker container with Debian GNU/Linux 13 (trixie) 6.6.15-amd64
- Tester: D:Ta
- Date: 01/12/2025
- Pyroform Version: 1.0.0
- Validates: [TPS TC_1](../TPS/TC_1.md)
- Status:
[X] PASS
[ ] FAIL
[ ] BLOCKED

# Archive:

## 1. Display Version
```text
    root@1e1b62138bef:/app/Pyroform# pyroform --version

        ___________________________________________________________________________

        *                          *   Pyroform   *                           *
        ___________________________________________________________________________
                        Regards, the Alveare Solutions #!/Society -x


    Pyroform version 1.0.0
```

## 2. Display Help
```text
    root@1e1b62138bef:/app/Pyroform# pyroform --help

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


    root@1e1b62138bef:/app/Pyroform# pyroform snapshot --help

        ___________________________________________________________________________

        *                          *   Pyroform   *                           *
        ___________________________________________________________________________
                        Regards, the Alveare Solutions #!/Society -x

    Usage: pyroform snapshot [OPTIONS]

    Validate system against Pyro file(s)

    Options:
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
    -y, --yes               Flag to confirm all manual prompts such that manual
                            interaction from user is not required
    --dry-run               Perform a trial run without making any changes
    --help                  Show this message and exit.


    root@1e1b62138bef:/app/Pyroform# pyroform configure --help

        ___________________________________________________________________________

        *                          *   Pyroform   *                           *
        ___________________________________________________________________________
                        Regards, the Alveare Solutions #!/Society -x

    Usage: pyroform configure [OPTIONS]

    Configure system according to Pyro file(s)

    Options:
    -i, --input PATH        Path to Pyro file (JSON|YAML) or directory
                            containing Pyro files  [required]
    -o, --output PATH       Path to FlowCTRL sketch file (JSON) or directory for
                            generated files
    -c, --config-file PATH  Path to Pyroform config file (JSON|YAML)
    -l, --log-file PATH     Path to Pyroform and FlowCTRL log file
    -r, --dump-report       Flag to generate report file with STDOUT, STDERR
                            plus summary
    -s, --silent            Flag to suppress STDOUT
    -d, --debug             Flag that makes logging and STDOUT messages more
                            verbose
    -y, --yes               Flag to confirm all manual prompts such that manual
                            interaction from user is not required
    --dry-run               Perform a trial run without making any changes
    --help                  Show this message and exit.


    root@1e1b62138bef:/app/Pyroform# pyroform scorch --help

        ___________________________________________________________________________

        *                          *   Pyroform   *                           *
        ___________________________________________________________________________
                        Regards, the Alveare Solutions #!/Society -x

    Usage: pyroform scorch [OPTIONS]

    Remove system resources not specified in Pyro file(s)

    Options:
    -i, --input PATH        Path to Pyro file (JSON|YAML) or directory
                            containing Pyro files  [required]
    -o, --output PATH       Path to FlowCTRL sketch file (JSON) or directory for
                            generated files
    -c, --config-file PATH  Path to Pyroform config file (JSON|YAML)
    -l, --log-file PATH     Path to Pyroform and FlowCTRL log file
    -r, --dump-report       Flag to generate report file with STDOUT, STDERR
                            plus summary
    -s, --silent            Flag to suppress STDOUT
    -d, --debug             Flag that makes logging and STDOUT messages more
                            verbose
    -y, --yes               Flag to confirm all manual prompts such that manual
                            interaction from user is not required
    --dry-run               Perform a trial run without making any changes
    --help                  Show this message and exit.


    root@1e1b62138bef:/app/Pyroform# pyroform mount --help

        ___________________________________________________________________________

        *                          *   Pyroform   *                           *
        ___________________________________________________________________________
                        Regards, the Alveare Solutions #!/Society -x

    Usage: pyroform mount [OPTIONS]

    Mount devices according to Pyro file(s)

    Options:
    -i, --input PATH        Path to Pyro file (JSON|YAML) or directory
                            containing Pyro files  [required]
    -o, --output PATH       Path to FlowCTRL sketch file (JSON) or directory for
                            generated files
    -c, --config-file PATH  Path to Pyroform config file (JSON|YAML)
    -l, --log-file PATH     Path to Pyroform and FlowCTRL log file
    -r, --dump-report       Flag to generate report file with STDOUT, STDERR
                            plus summary
    -s, --silent            Flag to suppress STDOUT
    -d, --debug             Flag that makes logging and STDOUT messages more
                            verbose
    -y, --yes               Flag to confirm all manual prompts such that manual
                            interaction from user is not required
    --dry-run               Perform a trial run without making any changes
    --help                  Show this message and exit.


    root@1e1b62138bef:/app/Pyroform# pyroform validate --help

        ___________________________________________________________________________

        *                          *   Pyroform   *                           *
        ___________________________________________________________________________
                        Regards, the Alveare Solutions #!/Society -x

    Usage: pyroform validate [OPTIONS]

    Validate system against Pyro file(s)

    Options:
    -i, --input PATH        Path to Pyro file (JSON|YAML) or directory
                            containing Pyro files  [required]
    -o, --output PATH       Path to FlowCTRL sketch file (JSON) or directory for
                            generated files
    -c, --config-file PATH  Path to Pyroform config file (JSON|YAML)
    -l, --log-file PATH     Path to Pyroform and FlowCTRL log file
    -r, --dump-report       Flag to generate report file with STDOUT, STDERR
                            plus summary
    -s, --silent            Flag to suppress STDOUT
    -d, --debug             Flag that makes logging and STDOUT messages more
                            verbose
    -y, --yes               Flag to confirm all manual prompts such that manual
                            interaction from user is not required
    --dry-run               Perform a trial run without making any changes
    --help                  Show this message and exit.


    root@1e1b62138bef:/app/Pyroform# pyroform workflow --help

        ___________________________________________________________________________

        *                          *   Pyroform   *                           *
        ___________________________________________________________________________
                        Regards, the Alveare Solutions #!/Society -x

    Usage: pyroform workflow [OPTIONS]

    Execute a complete Pyroform workflow from configuration file

    Options:
    -w, --workflow-file PATH  Path to workflow configuration file (JSON/YAML)
                                [required]
    --help                    Show this message and exit.
```
