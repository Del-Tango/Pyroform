# CLI Help and Version

- Priority: High
- Description: Verify CLI help system and version information
- Preconditions: Pyroform installed in test environment
- Validated by: [TAR TC_1](../TAR/TC_1.md)

## Test Steps:

1. Run version command
```bash
~$ pyroform --version
```
2. Run help commands
```bash
~$ pyroform --help
~$ pyroform configure --help
~$ pyroform scorch --help
~$ pyroform mount --help
~$ pyroform validate --help
~$ pyroform workflow --help
```

## Expected Results:

- Version displays correctly (e.g., "Pyroform version 1.0.0")
- Main help shows banner and available commands
- Each subcommand shows appropriate help text
- Banner displays correctly for all commands
