ID: TC-9 / Scorch Dry Run
Priority: High
Description: Test scorch operation in dry-run mode
Preconditions: System has some test users/files not in config

Test Steps:

1. Create orphaned user:
```bash
~$ useradd scorchtest
```
2. Create orphaned file:
```bash
~$ touch /tmp/orphaned.file
```
3. Run commands
```bash
~$ pyroform scorch -i minimal_config.yaml --dry-run -v
```
4. Review what would be removed
5. Verify nothing actually removed

Expected Results:

- Dry-run shows orphaned resources
- No actual removal occurs
- Clear indication of dry-run mode
