# CLI Help and Version
- Test Environment: Docker container with Amazon Linux 2023.6.20241121 6.6.15-amd64
- Tester: D:Ta
- Date: 11/11/2025
- Pyroform Version: 1.0.0
- Validates: [TPS TC_1](../TPS/TC_1.md)
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
