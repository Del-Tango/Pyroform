# YAML Configuration Parsing
- Test Environment: Docker container with Debian GNU/Linux 13 (trixie) 6.6.15-amd64
- Tester: D:Ta
- Date: 01/12/2025
- Pyroform Version: 1.0.0
- Validates: [TPS TC_3](../TPS/TC_3.md)
- Status:
[X] PASS
[ ] FAIL
[ ] BLOCKED

# Remarks
N/A

# Archive

## 1. Create dummy Pyro file (test_simple_config.pyro.yaml)
```text
Label: "Test Simple Configuration"
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
Excludes:
  Users:
  - root
  - daemon
  - bin
  - sys
  - sync
  - games
  - man
  - lp
  - mail
  - news
  - uucp
  - proxy
  - www-data
  - backup
  - list
  - irc
  - _apt
  - nobody
  Groups:
  - root
  - daemon
  - bin
  - sys
  - adm
  - tty
  - disk
  - lp
  - mail
  - news
  - uucp
  - man
  - proxy
  - kmem
  - dialout
  - fax
  - voice
  - cdrom
  - floppy
  - tape
  - sudo
  - audio
  - dip
  - www-data
  - backup
  - operator
  - list
  - irc
  - src
  - shadow
  - utmp
  - video
  - sasl
  - plugdev
  - staff
  - games
  - users
  - nogroup
  - _ssh
  Directories:
  - /app
  - /bin
  - /boot
  - /dev
  - /etc
  - /home
  - /lib
  - /lib64
  - /media
  - /mnt
  - /opt
  - /proc
  - /protected
  - /root
  - /run
  - /sbin
  - /srv
  - /sys
  - /usr
  - /var
```

## 2. Run validation command using previously created Pyro file
```text
root@1e1b62138bef:/app/Pyroform# pyroform validate -i test_simple_config.pyro.yaml

    ___________________________________________________________________________

      *                          *   Pyroform   *                           *
    ___________________________________________________________________________
                    Regards, the Alveare Solutions #!/Society -x


[ INFO ]: Logging configured: /usr/local/lib/python3.13/dist-packages/log/pyroflow/pyroflow.log
[ INFO ]: State monitoring configured for inter-process control
[ INFO ]: Parsing Pyro state file (test_simple_config.pyro.yaml)...
[ INFO ]: State file data: {
    "Label": "Test Simple Configuration",
    "Users": [
        {
            "label": "test_user",
            "Name": "testuser",
            "Password": "test123",
            "Groups": [
                "testgroup"
            ]
        }
    ],
    "Groups": [
        {
            "label": "test_group",
            "Name": "testgroup",
            "Users": [
                "testuser"
            ]
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
[ INFO ]: Scanning current machine state (users, groups, filesystem)...
[ WARNING ]: Excluding user root
[ WARNING ]: Excluding user daemon
[ WARNING ]: Excluding user bin
[ WARNING ]: Excluding user sys
[ WARNING ]: Excluding user sync
[ WARNING ]: Excluding user games
[ WARNING ]: Excluding user man
[ WARNING ]: Excluding user lp
[ WARNING ]: Excluding user mail
[ WARNING ]: Excluding user news
[ WARNING ]: Excluding user uucp
[ WARNING ]: Excluding user proxy
[ WARNING ]: Excluding user www-data
[ WARNING ]: Excluding user backup
[ WARNING ]: Excluding user list
[ WARNING ]: Excluding user irc
[ WARNING ]: Excluding user _apt
[ WARNING ]: Excluding user nobody
[ WARNING ]: Excluding group root
[ WARNING ]: Excluding group daemon
[ WARNING ]: Excluding group bin
[ WARNING ]: Excluding group sys
[ WARNING ]: Excluding group adm
[ WARNING ]: Excluding group tty
[ WARNING ]: Excluding group disk
[ WARNING ]: Excluding group lp
[ WARNING ]: Excluding group mail
[ WARNING ]: Excluding group news
[ WARNING ]: Excluding group uucp
[ WARNING ]: Excluding group man
[ WARNING ]: Excluding group proxy
[ WARNING ]: Excluding group kmem
[ WARNING ]: Excluding group dialout
[ WARNING ]: Excluding group fax
[ WARNING ]: Excluding group voice
[ WARNING ]: Excluding group cdrom
[ WARNING ]: Excluding group floppy
[ WARNING ]: Excluding group tape
[ WARNING ]: Excluding group sudo
[ WARNING ]: Excluding group audio
[ WARNING ]: Excluding group dip
[ WARNING ]: Excluding group www-data
[ WARNING ]: Excluding group backup
[ WARNING ]: Excluding group operator
[ WARNING ]: Excluding group list
[ WARNING ]: Excluding group irc
[ WARNING ]: Excluding group src
[ WARNING ]: Excluding group shadow
[ WARNING ]: Excluding group utmp
[ WARNING ]: Excluding group video
[ WARNING ]: Excluding group sasl
[ WARNING ]: Excluding group plugdev
[ WARNING ]: Excluding group staff
[ WARNING ]: Excluding group games
[ WARNING ]: Excluding group users
[ WARNING ]: Excluding group nogroup
[ WARNING ]: Excluding group _ssh
[ INFO ]: Comparing current system state with Pyro file...
[ NOK ]: Validation discrepancies for Pyro config (Test Simple Configuration):
{
    "missing_users": [
        {
            "label": "test_user",
            "username": "testuser",
            "password": "test123",
            "groups": [
                "testgroup"
            ]
        }
    ],
    "extra_users": [
        {
            "username": "pyrotest1",
            "uid": 1003,
            "home_directory": "/home/pyrotest1"
        },
        {
            "username": "pyrotest2",
            "uid": 1004,
            "home_directory": "/home/pyrotest2"
        },
        {
            "username": "scorchtest",
            "uid": 1002,
            "home_directory": "/home/scorchtest"
        },
        {
            "username": "intruder",
            "uid": 1005,
            "home_directory": "/home/intruder"
        }
    ],
    "missing_groups": [
        {
            "label": "test_group",
            "groupname": "testgroup",
            "members": [
                "testuser"
            ]
        }
    ],
    "extra_groups": [
        {
            "groupname": "scorchtest",
            "gid": 1004,
            "members": []
        },
        {
            "groupname": "intruder",
            "gid": 1008,
            "members": []
        },
        {
            "groupname": "pyrotest2",
            "gid": 1007,
            "members": [
                "pyrotest2"
            ]
        },
        {
            "groupname": "pyrogroup2",
            "gid": 1006,
            "members": [
                "pyrotest2"
            ]
        },
        {
            "groupname": "pyrogroup1",
            "gid": 1005,
            "members": [
                "pyrotest1"
            ]
        },
        {
            "groupname": "pyrotest1",
            "gid": 1003,
            "members": [
                "pyrotest1"
            ]
        }
    ],
    "extra_directories": [
        {
            "path": "/tmp/pytest-of-root/pytest-13/test_setup_logging_log_file_di0",
            "owner": "root",
            "group": "root",
            "permissions": "0700"
        },
        ...
        {
            "path": "/tmp/pytest-of-root/pytest-12/test_parse_invalid_path_type0",
            "owner": "root",
            "group": "root",
            "permissions": "0700"
        }
    ],
    "extra_files": [
        {
            "path": "/tmp/pytest-of-root/pytest-13/test_load_config_json_decode_e0/invalid.json",
            "owner": "root",
            "group": "root",
            "permissions": "0644"
        },
        ...
        {
            "path": "/tmp/pytest-of-root/pytest-12/test_load_config_yml_extension0/config.yml",
            "owner": "root",
            "group": "root",
            "permissions": "0644"
        }
    ],
    "extra_symlinks": [
        {
            "path": "/tmp/pytest-of-root/pytest-12/test_parse_yaml_errorcurrent",
            "owner": "root",
            "group": "root",
            "permissions": "0777",
            "target": "/tmp/pytest-of-root/pytest-12/test_parse_yaml_error0"
        },
        ...
        {
            "path": "/tmp/pytest-of-root/pytest-13/test_parse_string_pathcurrent",
            "owner": "root",
            "group": "root",
            "permissions": "0777",
            "target": "/tmp/pytest-of-root/pytest-13/test_parse_string_path0"
        }
    ],
    "missing_mountpoints": [
        {
            "label": "test_device",
            "mountpoint": "/mnt/test"
        }
    ]
}
[ NOK ]: System state mismatch for (Test Simple Configuration) (352 critical, 352 total issues)
[ NOK ]: Found 352 critical issues, 352 total issues
[ NOK ]: System state validation failed - run "configure" to apply changes
```

## 3. Dry-run of configuration
```text
root@1e1b62138bef:/app/Pyroform# pyroform configure -i test_simple_config.pyro.yaml --dry-run

    ___________________________________________________________________________

      *                          *   Pyroform   *                           *
    ___________________________________________________________________________
                    Regards, the Alveare Solutions #!/Society -x


[ INFO ]: Logging configured: /usr/local/lib/python3.13/dist-packages/log/pyroflow/pyroflow.log
[ INFO ]: State monitoring configured for inter-process control
[ INFO ]: Parsing Pyro state file (test_simple_config.pyro.yaml)...
[ INFO ]: State file data: {
    "Label": "Test Simple Configuration",
    "Users": [
        {
            "label": "test_user",
            "Name": "testuser",
            "Password": "test123",
            "Groups": [
                "testgroup"
            ]
        }
    ],
    "Groups": [
        {
            "label": "test_group",
            "Name": "testgroup",
            "Users": [
                "testuser"
            ]
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
[ INFO ]: FlowCTRL Sketch: {
    "name": "Pyroform Auto-Generated Sketch Test Simple Configuration",
    "Users": [
        {
            "name": "Creating System User testuser",
            "cmd": "# for group in testgroup; do groupadd -f $group; done && useradd -m -p 'test123' -G 'testgroup' 'testuser' || exit 0",
            "setup-cmd": "id testuser && echo 'User testuser already exists' || exit 0",
            "teardown-cmd": "",
            "on-ok-cmd": "echo 'User testuser exists or created successfully'",
            "on-nok-cmd": "echo 'Failed to create user testuser'",
            "fatal-nok": false
        }
    ],
    "Groups": [
        {
            "name": "Creating System Group testgroup",
            "cmd": "# groupadd -f 'testgroup' && for user in testuser; do id $user || useradd -m $user; usermod -a -G 'testgroup' $user; done",
            "setup-cmd": "getent group testgroup && echo 'Group testgroup already exists' || exit 0",
            "teardown-cmd": "",
            "on-ok-cmd": "echo 'Group testgroup exists'",
            "on-nok-cmd": "echo 'Failed to create group testgroup'",
            "fatal-nok": false
        }
    ],
    "Devices": [
        {
            "name": "Creating System Mountpoint Directory /mnt/test",
            "cmd": "# mkdir -p '/mnt/test'",
            "setup-cmd": "test -d /mnt/test",
            "teardown-cmd": "",
            "on-ok-cmd": "echo 'Mountpoint /mnt/test exists'",
            "on-nok-cmd": "echo 'Creating mountpoint /mnt/test'",
            "fatal-nok": true
        },
        {
            "name": "Mounting Block Device test_device",
            "cmd": "# mount '/tmp/test_mount1' '/mnt/test'",
            "setup-cmd": "mount | grep -q '/tmp/test_mount on /mnt/test'",
            "teardown-cmd": "umount /mnt/test",
            "on-ok-cmd": "echo 'Device /tmp/test_mount already mounted to /mnt/test'",
            "on-nok-cmd": "echo 'Mounting /tmp/test_mount to /mnt/test'",
            "fatal-nok": true
        }
    ]
}
[ INFO ]: Purging all state and report data
[ OK ]: All data purged
[ INFO ]: Loading sketch file: pyroflow.sketch.json
[ OK ]: Loaded procedure: Pyroform Auto-Generated Sketch Test Simple Configuration
[ INFO ]: Starting procedure execution with state monitoring
[ INFO ]: Procedure state set to STARTED
[ INFO ]: State monitoring active - process can be controlled externally
[ INFO ]: Beginning controlled procedure execution...
[ INFO ]: Processing stage: Users
[ INFO ]: Processing action: Creating System User testuser
[ INFO ]: Executing Procedure Stage Action: Creating System User testuser
CMD> id testuser && echo 'User testuser already exists' || exit 0


CMD> # for group in testgroup; do groupadd -f $group; done && useradd -m -p 'test123' -G 'testgroup' 'testuser' || exit 0


CMD> echo 'User testuser exists or created successfully'
User testuser exists or created successfully

[ OK ]: Action completed: Creating System User testuser
[ OK ]: Stage completed: Users
[ INFO ]: Processing stage: Groups
[ INFO ]: Processing action: Creating System Group testgroup
[ INFO ]: Executing Procedure Stage Action: Creating System Group testgroup
CMD> getent group testgroup && echo 'Group testgroup already exists' || exit 0


CMD> # groupadd -f 'testgroup' && for user in testuser; do id $user || useradd -m $user; usermod -a -G 'testgroup' $user; done


CMD> echo 'Group testgroup exists'
Group testgroup exists

[ OK ]: Action completed: Creating System Group testgroup
[ OK ]: Stage completed: Groups
[ INFO ]: Processing stage: Devices
[ INFO ]: Processing action: Creating System Mountpoint Directory /mnt/test
[ INFO ]: Executing Procedure Stage Action: Creating System Mountpoint Directory /mnt/test
CMD> test -d /mnt/test


[ NOK ]:

CMD> # mkdir -p '/mnt/test'


CMD> echo 'Mountpoint /mnt/test exists'
Mountpoint /mnt/test exists

[ OK ]: Action completed: Creating System Mountpoint Directory /mnt/test
[ INFO ]: Processing action: Mounting Block Device test_device
[ INFO ]: Executing Procedure Stage Action: Mounting Block Device test_device
CMD> mount | grep -q '/tmp/test_mount on /mnt/test'


[ NOK ]:

CMD> # mount '/tmp/test_mount1' '/mnt/test'


CMD> echo 'Device /tmp/test_mount already mounted to /mnt/test'
Device /tmp/test_mount already mounted to /mnt/test

CMD> umount /mnt/test


[ NOK ]: umount: /mnt/test: must be superuser to unmount.

[ OK ]: Action completed: Mounting Block Device test_device
[ OK ]: Stage completed: Devices
[ OK ]: Procedure completed: SUCCESS
```

### Miscellaneous

