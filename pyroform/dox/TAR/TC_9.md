# Scorch Dry Run
- Test Environment: Docker container with Debian GNU/Linux 13 (trixie) 6.6.15-amd64
- Tester: D:Ta
- Date: 23/11/2025
- Pyroform Version: 1.0.0
- Validates: [TPS TC_9](../TPS/TC_9.md)
- Preconditions: System has some test users/files not in config
- Status:
[X] PASS
[ ] FAIL
[ ] BLOCKED

# Archive

## 1. Create test Pyro file
```yaml
Label: "Full System Management Test"
Users:
  - label: "test_user_1"
    Name: "pyrotest1"
    Password: "testpass1"
    Groups: ["pyrogroup1"]
  - label: "test_user_2"
    Name: "pyrotest2"
    Password: "testpass2"
    Groups: ["pyrogroup1", "pyrogroup2"]
Groups:
  - label: "group_1"
    Name: "pyrogroup1"
    Users: ["pyrotest1", "pyrotest2"]
  - label: "group_2"
    Name: "pyrogroup2"
    Users: ["pyrotest2"]
Devices:
  - label: "Primary Storage"
    Path: "/dev/sda"
    Partition: 1
    Mountpoint: "/tmp/pyrotest"
    State:
      - "dir,/tmp/pyrotest,root,root,755"
      - "dir,/tmp/pyrotest/data,pyrotest1,pyrogroup1,750"
      - "dir,/tmp/pyrotest/logs,root,pyrogroup1,775"
      - "fl,/tmp/pyrotest/README,pyrotest1,pyrogroup1,644"
      - "ln,/tmp/pyrotest/readme_shortcut,pyrotest1,pyrogroup1,777,/tmp/pyrotest/README"
Excludes:
  Users: []
  Groups: []
  Devices:
    - "/dev/sda"
  Directories:
    - "/proc"
    - "/sys"
    - "/dev"
    - "/boot"
    - "/lib"
    - "/lib64"
    - "/sbin"
    - "/usr"
    - "/var"
    - "/app"
    - "/etc"
    - "/usr"
    - "/root"
  Files: []
  Links: []
```

## 2. Create extra user
```text
    root@1e1b62138bef:/app/Pyroform# useradd scorchtest; echo $?
    0
```

## 3. Create extra file
```text
    root@1e1b62138bef:/app/Pyroform# touch /tmp/shall_not_be_scorched.dummy; echo $?
    0
```

## 4. Dry-Run Scorch command
```text
    root@1e1b62138bef:/app/Pyroform# pyroform scorch -i dump/full_test.pyro.yaml --dry-run

        ___________________________________________________________________________

        *                          *   Pyroform   *                           *
        ___________________________________________________________________________
                        Regards, the Alveare Solutions #!/Society -x


    [ INFO ]: Logging configured: /usr/local/lib/python3.13/dist-packages/log/pyroflow/pyroflow.log
    [ INFO ]: State monitoring configured for inter-process control
    [ INFO ]: Parsing Pyro state file (dump/full_test.pyro.yaml)...
    [ INFO ]: State file data: {
        "Label": "User Management Test",
        "Users": [
            {
                "label": "test_user_1",
                "Name": "pyrotest1",
                "Password": "testpass1",
                "Groups": [
                    "pyrogroup1"
                ]
            },
            {
                "label": "test_user_2",
                "Name": "pyrotest2",
                "Password": "testpass2",
                "Groups": [
                    "pyrogroup1",
                    "pyrogroup2"
                ]
            }
        ],
        "Groups": [
            {
                "label": "group_1",
                "Name": "pyrogroup1",
                "Users": [
                    "pyrotest1",
                    "pyrotest2"
                ]
            },
            {
                "label": "group_2",
                "Name": "pyrogroup2",
                "Users": [
                    "pyrotest2"
                ]
            }
        ],
        "Devices": [
            {
                "label": "Primary Storage",
                "Path": "/dev/sda",
                "Partition": 1,
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
            "Users": [],
            "Groups": [],
            "Devices": [
                "/dev/sda"
            ],
            "Directories": [
                "/proc",
                "/sys",
                "/dev",
                "/boot",
                "/lib",
                "/lib64",
                "/sbin",
                "/usr",
                "/var",
                "/app",
                "/etc",
                "/usr",
                "/root"
            ],
            "Files": [],
            "Links": []
        }
    }
    [ INFO ]: Scanning current machine state (users, groups, filesystem)...
    [ INFO ]: Comparing current system state with Pyro file...
    [ INFO ]: FlowCTRL Sketch - {
        "name": "Pyroform Auto-Generated Sketch User Management Test",
        "Cleanup": [
            {
                "name": "Cleanup extra users",
                "cmd": "# for user in scorchtest sys www-data irc bin daemon proxy lp root list news sync man nobody mail uucp backup _apt games; do userdel -f -r $user; done",
                "setup-cmd": "",
                "on-ok-cmd": "echo 'Eliminated: scorchtest sys www-data irc bin daemon proxy lp root list news sync man nobody mail uucp backup _apt games'",
                "on-nok-cmd": "echo 'Could not scorch extra system users! Details: scorchtest sys www-data irc bin daemon proxy lp root list news sync man nobody mail uucp backup _apt games'",
                "fatal-nok": false
            },
            {
                "name": "Cleanup extra groups",
                "cmd": "# for group in scorchtest pyrotest1 nogroup pyrotest2; do groupdel $group; done",
                "setup-cmd": "",
                "on-ok-cmd": "echo 'Eliminated: scorchtest pyrotest1 nogroup pyrotest2'",
                "on-nok-cmd": "echo 'Could not scorch extra system groups! Details: scorchtest pyrotest1 nogroup pyrotest2'",
                "fatal-nok": false
            },
            {
                "name": "Cleanup extra directories",
                "cmd": "# rm -rf /tmp /tmp/flow_ctrl /mnt /home/pyrotest2 /home /opt /run/lock /home/pyrotest1 /run /srv /media",
                "setup-cmd": "",
                "on-ok-cmd": "echo 'Eliminated: /tmp /tmp/flow_ctrl /mnt /home/pyrotest2 /home /opt /run/lock /home/pyrotest1 /run /srv /media'",
                "on-nok-cmd": "echo 'Could not scorch extra directories! Details: /tmp /tmp/flow_ctrl /mnt /home/pyrotest2 /home /opt /run/lock /home/pyrotest1 /run /srv /media'",
                "fatal-nok": false
            },
            {
                "name": "Cleanup extra files and links",
                "cmd": "# rm -f /home/pyrotest2/.bash_logout /tmp/flow_ctrl/flow-ctrl.log /home/pyrotest2/.profile /home/pyrotest1/.bash_logout /tmp/shall_not_be_scorched.dummy /home/pyrotest1/.profile /.dockerenv /home/pyrotest2/.bashrc /home/pyrotest1/.bashrc /run/adduser /.pyroflow.state /var/run /var/lock /proc/1/task/1/root /proc/1306/task/1306/root /proc/1307/root /proc/1307/task/1307/root /proc/1/root /proc/1306/root",
                "setup-cmd": "",
                "on-ok-cmd": "echo 'Eliminated: /home/pyrotest2/.bash_logout /tmp/flow_ctrl/flow-ctrl.log /home/pyrotest2/.profile /home/pyrotest1/.bash_logout /tmp/shall_not_be_scorched.dummy /home/pyrotest1/.profile /.dockerenv /home/pyrotest2/.bashrc /home/pyrotest1/.bashrc /run/adduser /.pyroflow.state /var/run /var/lock /proc/1/task/1/root /proc/1306/task/1306/root /proc/1307/root /proc/1307/task/1307/root /proc/1/root /proc/1306/root'",
                "on-nok-cmd": "echo 'Could not scorch extra files and links! Details: /home/pyrotest2/.bash_logout /tmp/flow_ctrl/flow-ctrl.log /home/pyrotest2/.profile /home/pyrotest1/.bash_logout /tmp/shall_not_be_scorched.dummy /home/pyrotest1/.profile /.dockerenv /home/pyrotest2/.bashrc /home/pyrotest1/.bashrc /run/adduser /.pyroflow.state /var/run /var/lock /proc/1/task/1/root /proc/1306/task/1306/root /proc/1307/root /proc/1307/task/1307/root /proc/1/root /proc/1306/root'",
                "fatal-nok": false
            }
        ]
    }
    [ INFO ]: Purging all state and report data
    [ OK ]: All data purged
    [ INFO ]: Loading sketch file: pyroflow.sketch.json
    [ OK ]: Loaded procedure: Pyroform Auto-Generated Sketch User Management Test
    [ INFO ]: Starting procedure execution with state monitoring
    [ INFO ]: Procedure state set to STARTED
    [ INFO ]: State monitoring active - process can be controlled externally
    [ INFO ]: Beginning controlled procedure execution...
    [ INFO ]: Processing stage: Cleanup
    [ INFO ]: Processing action: Cleanup extra users
    [ INFO ]: Executing Procedure Stage Action: Cleanup extra users
    CMD> # for user in scorchtest sys www-data irc bin daemon proxy lp root list news sync man nobody mail uucp backup _apt games; do userdel -f -r $user; done


    CMD> echo 'Eliminated: scorchtest sys www-data irc bin daemon proxy lp root list news sync man nobody mail uucp backup _apt games'
    Eliminated: scorchtest sys www-data irc bin daemon proxy lp root list news sync man nobody mail uucp backup _apt games

    [ OK ]: Action completed: Cleanup extra users
    [ INFO ]: Processing action: Cleanup extra groups
    [ INFO ]: Executing Procedure Stage Action: Cleanup extra groups
    CMD> # for group in scorchtest pyrotest1 nogroup pyrotest2; do groupdel $group; done


    CMD> echo 'Eliminated: scorchtest pyrotest1 nogroup pyrotest2'
    Eliminated: scorchtest pyrotest1 nogroup pyrotest2

    [ OK ]: Action completed: Cleanup extra groups
    [ INFO ]: Processing action: Cleanup extra directories
    [ INFO ]: Executing Procedure Stage Action: Cleanup extra directories
    CMD> # rm -rf /tmp /tmp/flow_ctrl /mnt /home/pyrotest2 /home /opt /run/lock /home/pyrotest1 /run /srv /media


    CMD> echo 'Eliminated: /tmp /tmp/flow_ctrl /mnt /home/pyrotest2 /home /opt /run/lock /home/pyrotest1 /run /srv /media'
    Eliminated: /tmp /tmp/flow_ctrl /mnt /home/pyrotest2 /home /opt /run/lock /home/pyrotest1 /run /srv /media

    [ OK ]: Action completed: Cleanup extra directories
    [ INFO ]: Processing action: Cleanup extra files and links
    [ INFO ]: Executing Procedure Stage Action: Cleanup extra files and links
    CMD> # rm -f /home/pyrotest2/.bash_logout /tmp/flow_ctrl/flow-ctrl.log /home/pyrotest2/.profile /home/pyrotest1/.bash_logout /tmp/shall_not_be_scorched.dummy /home/pyrotest1/.profile /.dockerenv /home/pyrotest2/.bashrc /home/pyrotest1/.bashrc /run/adduser /.pyroflow.state /var/run /var/lock /proc/1/task/1/root /proc/1306/task/1306/root /proc/1307/root /proc/1307/task/1307/root /proc/1/root /proc/1306/root


    CMD> echo 'Eliminated: /home/pyrotest2/.bash_logout /tmp/flow_ctrl/flow-ctrl.log /home/pyrotest2/.profile /home/pyrotest1/.bash_logout /tmp/shall_not_be_scorched.dummy /home/pyrotest1/.profile /.dockerenv /home/pyrotest2/.bashrc /home/pyrotest1/.bashrc /run/adduser /.pyroflow.state /var/run /var/lock /proc/1/task/1/root /proc/1306/task/1306/root /proc/1307/root /proc/1307/task/1307/root /proc/1/root /proc/1306/root'
    Eliminated: /home/pyrotest2/.bash_logout /tmp/flow_ctrl/flow-ctrl.log /home/pyrotest2/.profile /home/pyrotest1/.bash_logout /tmp/shall_not_be_scorched.dummy /home/pyrotest1/.profile /.dockerenv /home/pyrotest2/.bashrc /home/pyrotest1/.bashrc /run/adduser /.pyroflow.state /var/run /var/lock /proc/1/task/1/root /proc/1306/task/1306/root /proc/1307/root /proc/1307/task/1307/root /proc/1/root /proc/1306/root

    [ OK ]: Action completed: Cleanup extra files and links
    [ OK ]: Stage completed: Cleanup
    [ OK ]: Procedure completed: SUCCESS
```

## 5. Analize output to ensure new user and file should have been scorched
```text
    ...
    [ INFO ]: FlowCTRL Sketch - {
        "name": "Pyroform Auto-Generated Sketch User Management Test",
        "Cleanup": [
            {
                "name": "Cleanup extra users",
                "cmd": "# for user in scorchtest sys www-data irc bin daemon proxy lp root list news sync man nobody mail uucp backup _apt games; do userdel -f -r $user; done",
                ...
            },
            ...
            {
                "name": "Cleanup extra files and links",
                "cmd": "# rm -f /home/pyrotest2/.bash_logout /tmp/flow_ctrl/flow-ctrl.log /home/pyrotest2/.profile /home/pyrotest1/.bash_logout /tmp/shall_not_be_scorched.dummy /home/pyrotest1/.profile /.dockerenv /home/pyrotest2/.bashrc /home/pyrotest1/.bashrc /run/adduser /.pyroflow.state /var/run /var/lock /proc/1/task/1/root /proc/1306/task/1306/root /proc/1307/root /proc/1307/task/1307/root /proc/1/root /proc/1306/root",
                ...
            }
        ]
    }
    ...
```

## 6. Verify user and file have not actually been removed
```text
    root@1e1b62138bef:/app/Pyroform# id scorchtest
    uid=1002(scorchtest) gid=1004(scorchtest) groups=1004(scorchtest)

    root@1e1b62138bef:/app/Pyroform# ls -allah /tmp/shall_not_be_scorched.dummy
    -rw-r--r-- 1 root root 0 Nov 22 22:09 /tmp/shall_not_be_scorched.dummy
```

