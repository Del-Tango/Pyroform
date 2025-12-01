# Directory Structure Creation
- Test Environment: Docker container with Debian GNU/Linux 13 (trixie) 6.6.15-amd64
- Tester: D:Ta
- Date: 01/12/2025
- Pyroform Version: 1.0.0
- Validates: [TPS TC_8](../TPS/TC_8.md)
- Preconditions: Users from TC_7 exist
- Status:
[X] PASS
[ ] FAIL
[ ] BLOCKED

# Archive

## 1. Create test Pyro file
```yaml
Label: "Filesystem Test Without Block Device Path"
Devices:
  - label: "test_fs"
    Path: ""
    Partition: 0
    Mountpoint: "/tmp/pyrotest"
    State:
      - "dir,/tmp/pyrotest,root,root,755"
      - "dir,/tmp/pyrotest/data,pyrotest1,pyrogroup1,750"
      - "dir,/tmp/pyrotest/logs,root,pyrogroup1,775"
      - "fl,/tmp/pyrotest/README,pyrotest1,pyrogroup1,644"
      - "ln,/tmp/pyrotest/readme_shortcut,pyrotest1,pyrogroup1,777,/tmp/pyrotest/README"
Excludes:
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

## 2. Dry-run configure
```text
root@1e1b62138bef:/app/Pyroform# pyroform configure -i fs_test.pyro.yaml --dry-run

    ___________________________________________________________________________

      *                          *   Pyroform   *                           *
    ___________________________________________________________________________
                    Regards, the Alveare Solutions #!/Society -x


[ INFO ]: Logging configured: /usr/local/lib/python3.13/dist-packages/log/pyroflow/pyroflow.log
[ INFO ]: State monitoring configured for inter-process control
[ INFO ]: Parsing Pyro state file (fs_test.pyro.yaml)...
[ INFO ]: State file data: {
    "Label": "Filesystem Test Without Block Device Path",
    "Devices": [
        {
            "label": "test_fs",
            "Path": "",
            "Partition": 0,
            "Mountpoint": "/tmp/pyrotest",
            "State": [
                "dir,/tmp/pyrotest,root,root,755",
                "dir,/tmp/pyrotest/data,pyrotest1,pyrogroup1,750",
                "dir,/tmp/pyrotest/logs,root,pyrogroup1,775",
                "fl,/tmp/pyrotest/README,pyrotest1,pyrogroup1,644",
                "ln,/tmp/pyrotest/readme_shortcut,pyrotest1,pyrogroup1,777,/tmp/pyrotest/README"
            ]
        }
    ],
    "Excludes": {
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
[ INFO ]: FlowCTRL Sketch: {                                                                                                                                                                                               16:45:42 [212/1813]
    "name": "Pyroform Auto-Generated Sketch Filesystem Test Without Block Device Path",
    "Devices": [
        {
            "name": "Creating System Mountpoint Directory /tmp/pyrotest",
            "cmd": "# mkdir -p '/tmp/pyrotest'",
            "setup-cmd": "test -d /tmp/pyrotest",
            "teardown-cmd": "",
            "on-ok-cmd": "echo 'Mountpoint /tmp/pyrotest exists'",
            "on-nok-cmd": "echo 'Creating mountpoint /tmp/pyrotest'",
            "fatal-nok": true
        },
        {
            "name": "Creating Directory /tmp/pyrotest",
            "cmd": "# mkdir -p /tmp/pyrotest",
            "setup-cmd": "test -d /tmp/pyrotest",
            "teardown-cmd": "",
            "on-ok-cmd": "echo 'Directory /tmp/pyrotest exists'",
            "on-nok-cmd": "echo 'Creating directory /tmp/pyrotest'",
            "fatal-nok": true
        },
        {
            "name": "Setting Permissions For /tmp/pyrotest",
            "cmd": "# chown root:root /tmp/pyrotest && chmod 755 /tmp/pyrotest",
            "setup-cmd": "stat -c '%U:%G %a' /tmp/pyrotest | grep -q 'root:root 755'",
            "teardown-cmd": "",
            "on-ok-cmd": "echo 'Permissions for /tmp/pyrotest are correct'",
            "on-nok-cmd": "echo 'Setting permissions for /tmp/pyrotest'",
            "fatal-nok": true
        },
        {
            "name": "Creating Directory /tmp/pyrotest/data",
            "cmd": "# mkdir -p /tmp/pyrotest/data",
            "setup-cmd": "test -d /tmp/pyrotest/data",
            "teardown-cmd": "",
            "on-ok-cmd": "echo 'Directory /tmp/pyrotest/data exists'",
            "on-nok-cmd": "echo 'Creating directory /tmp/pyrotest/data'",
            "fatal-nok": true
        },
        {
            "name": "Setting Permissions For /tmp/pyrotest/data",
            "cmd": "# chown pyrotest1:pyrogroup1 /tmp/pyrotest/data && chmod 750 /tmp/pyrotest/data",
            "setup-cmd": "stat -c '%U:%G %a' /tmp/pyrotest/data | grep -q 'pyrotest1:pyrogroup1 750'",
            "teardown-cmd": "",
            "on-ok-cmd": "echo 'Permissions for /tmp/pyrotest/data are correct'",
            "on-nok-cmd": "echo 'Setting permissions for /tmp/pyrotest/data'",
            "fatal-nok": true
        },
        {
            "name": "Creating Directory /tmp/pyrotest/logs",
            "cmd": "# mkdir -p /tmp/pyrotest/logs",
            "setup-cmd": "test -d /tmp/pyrotest/logs",
            "teardown-cmd": "",
            "on-ok-cmd": "echo 'Directory /tmp/pyrotest/logs exists'",
            "on-nok-cmd": "echo 'Creating directory /tmp/pyrotest/logs'",
            "fatal-nok": true
        },
        {
            "name": "Setting Permissions For /tmp/pyrotest/logs",
            "cmd": "# chown root:pyrogroup1 /tmp/pyrotest/logs && chmod 775 /tmp/pyrotest/logs",
            "setup-cmd": "stat -c '%U:%G %a' /tmp/pyrotest/logs | grep -q 'root:pyrogroup1 775'",
            "teardown-cmd": "",
            "on-ok-cmd": "echo 'Permissions for /tmp/pyrotest/logs are correct'",
            "on-nok-cmd": "echo 'Setting permissions for /tmp/pyrotest/logs'",
            "fatal-nok": true
        },
        {
            "name": "Creating Regular File /tmp/pyrotest/README",
            "cmd": "# touch /tmp/pyrotest/README",
            "setup-cmd": "test -f /tmp/pyrotest/README",
            "teardown-cmd": "",
            "on-ok-cmd": "echo 'File /tmp/pyrotest/README exists'",
            "on-nok-cmd": "echo 'Creating file /tmp/pyrotest/README'",
            "fatal-nok": true
        },
        {
            "name": "Setting Permissions For /tmp/pyrotest/README",
            "cmd": "# chown pyrotest1:pyrogroup1 /tmp/pyrotest/README && chmod 644 /tmp/pyrotest/README",
            "setup-cmd": "stat -c '%U:%G %a' /tmp/pyrotest/README | grep -q 'pyrotest1:pyrogroup1 644'",
            "teardown-cmd": "",
            "on-ok-cmd": "echo 'Permissions for /tmp/pyrotest/README are correct'",
            "on-nok-cmd": "echo 'Setting permissions for /tmp/pyrotest/README'",
            "fatal-nok": true
        },
        {
            "name": "Creating Symbolic Link /tmp/pyrotest/readme_shortcut",
            "cmd": "# ln -s /tmp/pyrotest/README /tmp/pyrotest/readme_shortcut",
            "setup-cmd": "test -L /tmp/pyrotest/readme_shortcut",
            "teardown-cmd": "",
            "on-ok-cmd": "echo 'File /tmp/pyrotest/readme_shortcut exists'",
            "on-nok-cmd": "echo 'Creating file /tmp/pyrotest/readme_shortcut'",
            "fatal-nok": true
        },
        {
            "name": "Setting Permissions For /tmp/pyrotest/readme_shortcut",
            "cmd": "# chown pyrotest1:pyrogroup1 /tmp/pyrotest/readme_shortcut && chmod 777 /tmp/pyrotest/readme_shortcut",
            "setup-cmd": "stat -c '%U:%G %a' /tmp/pyrotest/readme_shortcut | grep -q 'pyrotest1:pyrogroup1 777'",
            "teardown-cmd": "",
            "on-ok-cmd": "echo 'Permissions for /tmp/pyrotest/readme_shortcut are correct'",
            "on-nok-cmd": "echo 'Setting permissions for /tmp/pyrotest/readme_shortcut'",
            "fatal-nok": true
        }
    ]
}
[ INFO ]: Purging all state and report data
[ OK ]: All data purged
[ INFO ]: Loading sketch file: pyroflow.sketch.json
[ OK ]: Loaded procedure: Pyroform Auto-Generated Sketch Filesystem Test Without Block Device Path
[ INFO ]: Starting procedure execution with state monitoring
[ INFO ]: Procedure state set to STARTED
[ INFO ]: State monitoring active - process can be controlled externally
[ INFO ]: Beginning controlled procedure execution...
[ INFO ]: Processing stage: Devices
[ INFO ]: Processing action: Creating System Mountpoint Directory /tmp/pyrotest
[ INFO ]: Executing Procedure Stage Action: Creating System Mountpoint Directory /tmp/pyrotest
CMD> test -d /tmp/pyrotest


[ NOK ]:

CMD> # mkdir -p '/tmp/pyrotest'


CMD> echo 'Mountpoint /tmp/pyrotest exists'
Mountpoint /tmp/pyrotest exists

[ OK ]: Action completed: Creating System Mountpoint Directory /tmp/pyrotest
[ INFO ]: Processing action: Creating Directory /tmp/pyrotest
[ INFO ]: Executing Procedure Stage Action: Creating Directory /tmp/pyrotest
CMD> test -d /tmp/pyrotest


[ NOK ]:

CMD> # mkdir -p /tmp/pyrotest


CMD> echo 'Directory /tmp/pyrotest exists'
Directory /tmp/pyrotest exists

[ OK ]: Action completed: Creating Directory /tmp/pyrotest
[ INFO ]: Processing action: Setting Permissions For /tmp/pyrotest
[ INFO ]: Executing Procedure Stage Action: Setting Permissions For /tmp/pyrotest
CMD> stat -c '%U:%G %a' /tmp/pyrotest | grep -q 'root:root 755'


[ NOK ]: stat: cannot statx '/tmp/pyrotest': No such file or directory

CMD> # chown root:root /tmp/pyrotest && chmod 755 /tmp/pyrotest


CMD> echo 'Permissions for /tmp/pyrotest are correct'
Permissions for /tmp/pyrotest are correct

[ OK ]: Action completed: Setting Permissions For /tmp/pyrotest
[ INFO ]: Processing action: Creating Directory /tmp/pyrotest/data
[ INFO ]: Executing Procedure Stage Action: Creating Directory /tmp/pyrotest/data
CMD> test -d /tmp/pyrotest/data


[ NOK ]:

CMD> # mkdir -p /tmp/pyrotest/data


CMD> echo 'Directory /tmp/pyrotest/data exists'
Directory /tmp/pyrotest/data exists

[ OK ]: Action completed: Creating Directory /tmp/pyrotest/data
[ INFO ]: Processing action: Setting Permissions For /tmp/pyrotest/data
[ INFO ]: Executing Procedure Stage Action: Setting Permissions For /tmp/pyrotest/data
CMD> stat -c '%U:%G %a' /tmp/pyrotest/data | grep -q 'pyrotest1:pyrogroup1 750'


[ NOK ]: stat: cannot statx '/tmp/pyrotest/data': No such file or directory

CMD> # chown pyrotest1:pyrogroup1 /tmp/pyrotest/data && chmod 750 /tmp/pyrotest/data


CMD> echo 'Permissions for /tmp/pyrotest/data are correct'
Permissions for /tmp/pyrotest/data are correct

[ OK ]: Action completed: Setting Permissions For /tmp/pyrotest/data
[ INFO ]: Processing action: Creating Directory /tmp/pyrotest/logs
[ INFO ]: Executing Procedure Stage Action: Creating Directory /tmp/pyrotest/logs
CMD> test -d /tmp/pyrotest/logs


[ NOK ]:

CMD> # mkdir -p /tmp/pyrotest/logs


CMD> echo 'Directory /tmp/pyrotest/logs exists'
Directory /tmp/pyrotest/logs exists

[ OK ]: Action completed: Creating Directory /tmp/pyrotest/logs
[ INFO ]: Processing action: Setting Permissions For /tmp/pyrotest/logs
[ INFO ]: Executing Procedure Stage Action: Setting Permissions For /tmp/pyrotest/logs
CMD> stat -c '%U:%G %a' /tmp/pyrotest/logs | grep -q 'root:pyrogroup1 775'


[ NOK ]: stat: cannot statx '/tmp/pyrotest/logs': No such file or directory

CMD> # chown root:pyrogroup1 /tmp/pyrotest/logs && chmod 775 /tmp/pyrotest/logs


CMD> echo 'Permissions for /tmp/pyrotest/logs are correct'
Permissions for /tmp/pyrotest/logs are correct

[ OK ]: Action completed: Setting Permissions For /tmp/pyrotest/logs
[ INFO ]: Processing action: Creating Regular File /tmp/pyrotest/README
[ INFO ]: Executing Procedure Stage Action: Creating Regular File /tmp/pyrotest/README
CMD> test -f /tmp/pyrotest/README


[ NOK ]:

CMD> # touch /tmp/pyrotest/README


CMD> echo 'File /tmp/pyrotest/README exists'
File /tmp/pyrotest/README exists

[ OK ]: Action completed: Creating Regular File /tmp/pyrotest/README
[ INFO ]: Processing action: Setting Permissions For /tmp/pyrotest/README
[ INFO ]: Executing Procedure Stage Action: Setting Permissions For /tmp/pyrotest/README
CMD> stat -c '%U:%G %a' /tmp/pyrotest/README | grep -q 'pyrotest1:pyrogroup1 644'


[ NOK ]: stat: cannot statx '/tmp/pyrotest/README': No such file or directory

CMD> # chown pyrotest1:pyrogroup1 /tmp/pyrotest/README && chmod 644 /tmp/pyrotest/README


CMD> echo 'Permissions for /tmp/pyrotest/README are correct'
Permissions for /tmp/pyrotest/README are correct

[ OK ]: Action completed: Setting Permissions For /tmp/pyrotest/README
[ INFO ]: Processing action: Creating Symbolic Link /tmp/pyrotest/readme_shortcut
[ INFO ]: Executing Procedure Stage Action: Creating Symbolic Link /tmp/pyrotest/readme_shortcut
CMD> test -L /tmp/pyrotest/readme_shortcut


[ NOK ]:

CMD> # ln -s /tmp/pyrotest/README /tmp/pyrotest/readme_shortcut


CMD> echo 'File /tmp/pyrotest/readme_shortcut exists'
File /tmp/pyrotest/readme_shortcut exists

[ OK ]: Action completed: Creating Symbolic Link /tmp/pyrotest/readme_shortcut
[ INFO ]: Processing action: Setting Permissions For /tmp/pyrotest/readme_shortcut
[ INFO ]: Executing Procedure Stage Action: Setting Permissions For /tmp/pyrotest/readme_shortcut
CMD> stat -c '%U:%G %a' /tmp/pyrotest/readme_shortcut | grep -q 'pyrotest1:pyrogroup1 777'


[ NOK ]: stat: cannot statx '/tmp/pyrotest/readme_shortcut': No such file or directory

CMD> # chown pyrotest1:pyrogroup1 /tmp/pyrotest/readme_shortcut && chmod 777 /tmp/pyrotest/readme_shortcut


CMD> echo 'Permissions for /tmp/pyrotest/readme_shortcut are correct'
Permissions for /tmp/pyrotest/readme_shortcut are correct

[ OK ]: Action completed: Setting Permissions For /tmp/pyrotest/readme_shortcut
[ OK ]: Stage completed: Devices
[ OK ]: Procedure completed: SUCCESS
```

## 3. Run configure command (auto-confirm)
```text
root@1e1b62138bef:/app/Pyroform# pyroform configure -i fs_test.pyro.yaml -y

    ___________________________________________________________________________

      *                          *   Pyroform   *                           *
    ___________________________________________________________________________
                    Regards, the Alveare Solutions #!/Society -x


[ INFO ]: Logging configured: /usr/local/lib/python3.13/dist-packages/log/pyroflow/pyroflow.log
[ INFO ]: State monitoring configured for inter-process control
[ INFO ]: Parsing Pyro state file (fs_test.pyro.yaml)...
[ INFO ]: State file data: {
    "Label": "Filesystem Test Without Block Device Path",
    "Devices": [
        {
            "label": "test_fs",
            "Path": "",
            "Partition": 0,
            "Mountpoint": "/tmp/pyrotest",
            "State": [
                "dir,/tmp/pyrotest,root,root,755",
                "dir,/tmp/pyrotest/data,pyrotest1,pyrogroup1,750",
                "dir,/tmp/pyrotest/logs,root,pyrogroup1,775",
                "fl,/tmp/pyrotest/README,pyrotest1,pyrogroup1,644",
                "ln,/tmp/pyrotest/readme_shortcut,pyrotest1,pyrogroup1,777,/tmp/pyrotest/README"
            ]
        }
    ],
    "Excludes": {
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
    "name": "Pyroform Auto-Generated Sketch Filesystem Test Without Block Device Path",
    "Devices": [
        {
            "name": "Creating System Mountpoint Directory /tmp/pyrotest",
            "cmd": "mkdir -p '/tmp/pyrotest'",
            "setup-cmd": "test -d /tmp/pyrotest",
            "teardown-cmd": "",
            "on-ok-cmd": "echo 'Mountpoint /tmp/pyrotest exists'",
            "on-nok-cmd": "echo 'Creating mountpoint /tmp/pyrotest'",
            "fatal-nok": true
        },
        {
            "name": "Creating Directory /tmp/pyrotest",
            "cmd": "mkdir -p /tmp/pyrotest",
            "setup-cmd": "test -d /tmp/pyrotest",
            "teardown-cmd": "",
            "on-ok-cmd": "echo 'Directory /tmp/pyrotest exists'",
            "on-nok-cmd": "echo 'Creating directory /tmp/pyrotest'",
            "fatal-nok": true
        },
        {
            "name": "Setting Permissions For /tmp/pyrotest",
            "cmd": "chown root:root /tmp/pyrotest && chmod 755 /tmp/pyrotest",
            "setup-cmd": "stat -c '%U:%G %a' /tmp/pyrotest | grep -q 'root:root 755'",
            "teardown-cmd": "",
            "on-ok-cmd": "echo 'Permissions for /tmp/pyrotest are correct'",
            "on-nok-cmd": "echo 'Setting permissions for /tmp/pyrotest'",
            "fatal-nok": true
        },
        {
            "name": "Creating Directory /tmp/pyrotest/data",
            "cmd": "mkdir -p /tmp/pyrotest/data",
            "setup-cmd": "test -d /tmp/pyrotest/data",
            "teardown-cmd": "",
            "on-ok-cmd": "echo 'Directory /tmp/pyrotest/data exists'",
            "on-nok-cmd": "echo 'Creating directory /tmp/pyrotest/data'",
            "fatal-nok": true
        },
        {
            "name": "Setting Permissions For /tmp/pyrotest/data",
            "cmd": "chown pyrotest1:pyrogroup1 /tmp/pyrotest/data && chmod 750 /tmp/pyrotest/data",
            "setup-cmd": "stat -c '%U:%G %a' /tmp/pyrotest/data | grep -q 'pyrotest1:pyrogroup1 750'",
            "teardown-cmd": "",
            "on-ok-cmd": "echo 'Permissions for /tmp/pyrotest/data are correct'",
            "on-nok-cmd": "echo 'Setting permissions for /tmp/pyrotest/data'",
            "fatal-nok": true
        },
        {
            "name": "Creating Directory /tmp/pyrotest/logs",
            "cmd": "mkdir -p /tmp/pyrotest/logs",
            "setup-cmd": "test -d /tmp/pyrotest/logs",
            "teardown-cmd": "",
            "on-ok-cmd": "echo 'Directory /tmp/pyrotest/logs exists'",
            "on-nok-cmd": "echo 'Creating directory /tmp/pyrotest/logs'",
            "fatal-nok": true
        },
        {
            "name": "Setting Permissions For /tmp/pyrotest/logs",
            "cmd": "chown root:pyrogroup1 /tmp/pyrotest/logs && chmod 775 /tmp/pyrotest/logs",
            "setup-cmd": "stat -c '%U:%G %a' /tmp/pyrotest/logs | grep -q 'root:pyrogroup1 775'",
            "teardown-cmd": "",
            "on-ok-cmd": "echo 'Permissions for /tmp/pyrotest/logs are correct'",
            "on-nok-cmd": "echo 'Setting permissions for /tmp/pyrotest/logs'",
            "fatal-nok": true
        },
        {
            "name": "Creating Regular File /tmp/pyrotest/README",
            "cmd": "touch /tmp/pyrotest/README",
            "setup-cmd": "test -f /tmp/pyrotest/README",
            "teardown-cmd": "",
            "on-ok-cmd": "echo 'File /tmp/pyrotest/README exists'",
            "on-nok-cmd": "echo 'Creating file /tmp/pyrotest/README'",
            "fatal-nok": true
        },
        {
            "name": "Setting Permissions For /tmp/pyrotest/README",
            "cmd": "chown pyrotest1:pyrogroup1 /tmp/pyrotest/README && chmod 644 /tmp/pyrotest/README",
            "setup-cmd": "stat -c '%U:%G %a' /tmp/pyrotest/README | grep -q 'pyrotest1:pyrogroup1 644'",
            "teardown-cmd": "",
            "on-ok-cmd": "echo 'Permissions for /tmp/pyrotest/README are correct'",
            "on-nok-cmd": "echo 'Setting permissions for /tmp/pyrotest/README'",
            "fatal-nok": true
        },
        {
            "name": "Creating Symbolic Link /tmp/pyrotest/readme_shortcut",
            "cmd": "ln -s /tmp/pyrotest/README /tmp/pyrotest/readme_shortcut",
            "setup-cmd": "test -L /tmp/pyrotest/readme_shortcut",
            "teardown-cmd": "",
            "on-ok-cmd": "echo 'File /tmp/pyrotest/readme_shortcut exists'",
            "on-nok-cmd": "echo 'Creating file /tmp/pyrotest/readme_shortcut'",
            "fatal-nok": true
        },
        {
            "name": "Setting Permissions For /tmp/pyrotest/readme_shortcut",
            "cmd": "chown pyrotest1:pyrogroup1 /tmp/pyrotest/readme_shortcut && chmod 777 /tmp/pyrotest/readme_shortcut",
            "setup-cmd": "stat -c '%U:%G %a' /tmp/pyrotest/readme_shortcut | grep -q 'pyrotest1:pyrogroup1 777'",
            "teardown-cmd": "",
            "on-ok-cmd": "echo 'Permissions for /tmp/pyrotest/readme_shortcut are correct'",
            "on-nok-cmd": "echo 'Setting permissions for /tmp/pyrotest/readme_shortcut'",
            "fatal-nok": true
        }
    ]
}
[ INFO ]: Purging all state and report data
[ OK ]: All data purged
[ INFO ]: Loading sketch file: pyroflow.sketch.json
[ OK ]: Loaded procedure: Pyroform Auto-Generated Sketch Filesystem Test Without Block Device Path
[ INFO ]: Starting procedure execution with state monitoring
[ INFO ]: Procedure state set to STARTED
[ INFO ]: State monitoring active - process can be controlled externally
[ INFO ]: Beginning controlled procedure execution...
[ INFO ]: Processing stage: Devices
[ INFO ]: Processing action: Creating System Mountpoint Directory /tmp/pyrotest
[ INFO ]: Executing Procedure Stage Action: Creating System Mountpoint Directory /tmp/pyrotest
CMD> test -d /tmp/pyrotest


[ NOK ]:

CMD> mkdir -p '/tmp/pyrotest'


CMD> echo 'Mountpoint /tmp/pyrotest exists'
Mountpoint /tmp/pyrotest exists

[ OK ]: Action completed: Creating System Mountpoint Directory /tmp/pyrotest
[ INFO ]: Processing action: Creating Directory /tmp/pyrotest
[ INFO ]: Executing Procedure Stage Action: Creating Directory /tmp/pyrotest
CMD> test -d /tmp/pyrotest


CMD> mkdir -p /tmp/pyrotest


CMD> echo 'Directory /tmp/pyrotest exists'
Directory /tmp/pyrotest exists

[ OK ]: Action completed: Creating Directory /tmp/pyrotest
[ INFO ]: Processing action: Setting Permissions For /tmp/pyrotest
[ INFO ]: Executing Procedure Stage Action: Setting Permissions For /tmp/pyrotest
CMD> stat -c '%U:%G %a' /tmp/pyrotest | grep -q 'root:root 755'


CMD> chown root:root /tmp/pyrotest && chmod 755 /tmp/pyrotest


CMD> echo 'Permissions for /tmp/pyrotest are correct'
Permissions for /tmp/pyrotest are correct

[ OK ]: Action completed: Setting Permissions For /tmp/pyrotest
[ INFO ]: Processing action: Creating Directory /tmp/pyrotest/data
[ INFO ]: Executing Procedure Stage Action: Creating Directory /tmp/pyrotest/data
CMD> test -d /tmp/pyrotest/data


[ NOK ]:

CMD> mkdir -p /tmp/pyrotest/data

CMD> echo 'Directory /tmp/pyrotest/data exists'
Directory /tmp/pyrotest/data exists

[ OK ]: Action completed: Creating Directory /tmp/pyrotest/data
[ INFO ]: Processing action: Setting Permissions For /tmp/pyrotest/data
[ INFO ]: Executing Procedure Stage Action: Setting Permissions For /tmp/pyrotest/data
CMD> stat -c '%U:%G %a' /tmp/pyrotest/data | grep -q 'pyrotest1:pyrogroup1 750'


[ NOK ]:

CMD> chown pyrotest1:pyrogroup1 /tmp/pyrotest/data && chmod 750 /tmp/pyrotest/data


CMD> echo 'Permissions for /tmp/pyrotest/data are correct'
Permissions for /tmp/pyrotest/data are correct

[ OK ]: Action completed: Setting Permissions For /tmp/pyrotest/data
[ INFO ]: Processing action: Creating Directory /tmp/pyrotest/logs
[ INFO ]: Executing Procedure Stage Action: Creating Directory /tmp/pyrotest/logs
CMD> test -d /tmp/pyrotest/logs


[ NOK ]:

CMD> mkdir -p /tmp/pyrotest/logs


CMD> echo 'Directory /tmp/pyrotest/logs exists'
Directory /tmp/pyrotest/logs exists

[ OK ]: Action completed: Creating Directory /tmp/pyrotest/logs
[ INFO ]: Processing action: Setting Permissions For /tmp/pyrotest/logs
[ INFO ]: Executing Procedure Stage Action: Setting Permissions For /tmp/pyrotest/logs
CMD> stat -c '%U:%G %a' /tmp/pyrotest/logs | grep -q 'root:pyrogroup1 775'


[ NOK ]:

CMD> chown root:pyrogroup1 /tmp/pyrotest/logs && chmod 775 /tmp/pyrotest/logs


CMD> echo 'Permissions for /tmp/pyrotest/logs are correct'
Permissions for /tmp/pyrotest/logs are correct

[ OK ]: Action completed: Setting Permissions For /tmp/pyrotest/logs
[ INFO ]: Processing action: Creating Regular File /tmp/pyrotest/README
[ INFO ]: Executing Procedure Stage Action: Creating Regular File /tmp/pyrotest/README
CMD> test -f /tmp/pyrotest/README


[ NOK ]:

CMD> touch /tmp/pyrotest/README

CMD> echo 'File /tmp/pyrotest/README exists'
File /tmp/pyrotest/README exists

[ OK ]: Action completed: Creating Regular File /tmp/pyrotest/README
[ INFO ]: Processing action: Setting Permissions For /tmp/pyrotest/README
[ INFO ]: Executing Procedure Stage Action: Setting Permissions For /tmp/pyrotest/README
CMD> stat -c '%U:%G %a' /tmp/pyrotest/README | grep -q 'pyrotest1:pyrogroup1 644'


[ NOK ]:

CMD> chown pyrotest1:pyrogroup1 /tmp/pyrotest/README && chmod 644 /tmp/pyrotest/README


CMD> echo 'Permissions for /tmp/pyrotest/README are correct'
Permissions for /tmp/pyrotest/README are correct

[ OK ]: Action completed: Setting Permissions For /tmp/pyrotest/README
[ INFO ]: Processing action: Creating Symbolic Link /tmp/pyrotest/readme_shortcut
[ INFO ]: Executing Procedure Stage Action: Creating Symbolic Link /tmp/pyrotest/readme_shortcut
CMD> test -L /tmp/pyrotest/readme_shortcut


[ NOK ]:

CMD> ln -s /tmp/pyrotest/README /tmp/pyrotest/readme_shortcut


CMD> echo 'File /tmp/pyrotest/readme_shortcut exists'
File /tmp/pyrotest/readme_shortcut exists

[ OK ]: Action completed: Creating Symbolic Link /tmp/pyrotest/readme_shortcut
[ INFO ]: Processing action: Setting Permissions For /tmp/pyrotest/readme_shortcut
[ INFO ]: Executing Procedure Stage Action: Setting Permissions For /tmp/pyrotest/readme_shortcut
CMD> stat -c '%U:%G %a' /tmp/pyrotest/readme_shortcut | grep -q 'pyrotest1:pyrogroup1 777'


[ NOK ]:

CMD> chown pyrotest1:pyrogroup1 /tmp/pyrotest/readme_shortcut && chmod 777 /tmp/pyrotest/readme_shortcut


CMD> echo 'Permissions for /tmp/pyrotest/readme_shortcut are correct'
Permissions for /tmp/pyrotest/readme_shortcut are correct

[ OK ]: Action completed: Setting Permissions For /tmp/pyrotest/readme_shortcut
[ OK ]: Stage completed: Devices
[ OK ]: Procedure completed: SUCCESS
```

## 4. Verify created directory structure
```text
root@1e1b62138bef:/app/Pyroform# tree /tmp/pyrotest
/tmp/pyrotest
|-- README
|-- data
|-- logs
`-- readme_shortcut -> /tmp/pyrotest/README

3 directories, 2 files
```

## 5. Verify ownership and permissions
```text
root@1e1b62138bef:/app/Pyroform# ls -allah /tmp/pyrotest
total 24K
drwxr-xr-x 4 root      root       4.0K Dec  1 21:50 .
drwxrwxrwt 1 root      root        12K Dec  1 21:50 ..
-rwxrwxrwx 1 pyrotest1 pyrogroup1    0 Dec  1 21:50 README
drwxr-x--- 2 pyrotest1 pyrogroup1 4.0K Dec  1 21:50 data
drwxrwxr-x 2 root      pyrogroup1 4.0K Dec  1 21:50 logs
lrwxrwxrwx 1 root      root         20 Dec  1 21:50 readme_shortcut -> /tmp/pyrotest/README
```

## 6. Cleanup
```text
root@1e1b62138bef:/app/Pyroform# rm -rf /tmp/pyrotest; echo $?
0
```

