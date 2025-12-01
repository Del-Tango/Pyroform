# JSON Configuration Parsing
- Priority: High
- Description: Test JSON configuration file parsing
- Preconditions:
- Validated by: [TAR TC_4](../TAR/TC_4.md)

## Test Data (test_simple_config.pyro.json):
```json
{
  "Label": "Test Simple Configuration",
  "Users": [
    {
      "label": "test_user",
      "Name": "testuser",
      "Password": "test123",
      "Groups": ["testgroup"]
    }
  ],
  "Groups": [
    {
      "label": "test_group",
      "Name": "testgroup",
      "Users": ["testuser"]
    }
  ],
  "Devices": [
    {
      "label": "test_device",
      "Path": "/tmp/test_mount",
      "Partition": 1,
      "Mountpoint": "/mnt/test",
      "State": []
    }
  ],
  "Excludes": {
    "Users": [
      "root",
      "daemon",
      "bin",
      "sys",
      "sync",
      "games",
      "man",
      "lp",
      "mail",
      "news",
      "uucp",
      "proxy",
      "www-data",
      "backup",
      "list",
      "irc",
      "_apt",
      "nobody"
    ],
    "Groups": [
      "root",
      "daemon",
      "bin",
      "sys",
      "adm",
      "tty",
      "disk",
      "lp",
      "mail",
      "news",
      "uucp",
      "man",
      "proxy",
      "kmem",
      "dialout",
      "fax",
      "voice",
      "cdrom",
      "floppy",
      "tape",
      "sudo",
      "audio",
      "dip",
      "www-data",
      "backup",
      "operator",
      "list",
      "irc",
      "src",
      "shadow",
      "utmp",
      "video",
      "sasl",
      "plugdev",
      "staff",
      "games",
      "users",
      "nogroup",
      "_ssh"
    ],
    "Directories": [
      "/app",
      "/bin",
      "/boot",
      "/dev",
      "/etc",
      "/home",
      "/lib",
      "/lib64",
      "/media",
      "/mnt",
      "/opt",
      "/proc",
      "/protected",
      "/root",
      "/run",
      "/sbin",
      "/srv",
      "/sys",
      "/usr",
      "/var"
    ]
  }
}
```

## Test Steps:

1. Create test_config.pyro.json with above content
2. Run validation command
```bash
~$ pyroform validate -i test_config.pyro.json
```
3. Run configuration command with dry-run flag
```bash
~$ pyroform configure -i test_config.pyro.json --dry-run
```

## Expected Results:

- JSON file parsed without errors
- Configuration object created correctly
- Dry-run completes successfully
