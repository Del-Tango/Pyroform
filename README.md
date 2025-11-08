# Pyroform

Linux Configurator tool written in Python3. Receives input file(s) containing list of
users, user groups, block storage device mountpoints, files and directories with owners and permissions,
generates on the fly FlowCTRL sketch files based in input pyro file(s), and runs them using the flow_ctrl library.

## Features

- **Configure**: creates users, groups, files and directories with appropriate ownership and permissions
- **Scorch**: Cleanup everything on the system not specified in the input Pyro file(s)
- **Mount**: mounts block storage device partitions to designated mountpoints
- **Validate**: No action, just reports if the system corresponds to input Pyro file(s)

## Installation

```bash
pip install -e .
```

Usage
```bash
pyroform --configure --input config.yaml --yes
pyroform --validate --input configs/
pyroform --scorch --input pyro_config.json --dump-report
```
Configuration Format

See the project documentation for Pyro file format specifications.

[Include appropriate MIT license text here]

Key Implementation Details:

    Data Models: Used dataclass for clean data structures with type hints

    Parser: Supports both JSON and YAML formats, handles file and directory inputs

    CLI: Comprehensive Click-based interface matching the specification

    Error Handling: Proper exception handling for file operations and parsing

    Flexible Input: Supports single files and directories with pattern matching

    Type Safety: Full type hints for better code quality and IDE support

This implementation satisfies all the Phase 1 integration tests:

    File parsing for JSON and YAML

    Directory scanning with pattern matching

    Data model validation and creation

    CLI argument parsing with all specified options

    Proper error handling for invalid files

    Multiple config file merging

The code is structured to be easily extensible for the remaining phases while maintaining clean separation of concerns.
