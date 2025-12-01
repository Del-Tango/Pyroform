# Scorch Dry Run
- Test Environment: Docker container with Debian GNU/Linux 13 (trixie) 6.6.15-amd64
- Tester: D:Ta
- Date: 02/12/2025
- Pyroform Version: 1.0.0
- Validates: [TPS TC_9](../TPS/TC_9.md)
- Preconditions: System has some test users/files not in config
- Status:
[X] PASS
[ ] FAIL
[ ] BLOCKED

# Archive

## 1. Create test Pyro file (full_system.pyro.yaml)
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
root@1e1b62138bef:/app/Pyroform# pyroform scorch -i full_system.pyro.yaml --dry-run

    ___________________________________________________________________________

      *                          *   Pyroform   *                           *
    ___________________________________________________________________________
                    Regards, the Alveare Solutions #!/Society -x


[ INFO ]: Logging configured: /usr/local/lib/python3.13/dist-packages/log/pyroflow/pyroflow.log
[ INFO ]: State monitoring configured for inter-process control
[ INFO ]: Parsing Pyro state file (full_system.pyro.yaml)...
[ INFO ]: State file data: {
    "Label": "Full System Management Test",
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
[ INFO ]: DRY RUN: No changes will be made
[ INFO ]: Scanning current machine state (users, groups, filesystem)...
[ INFO ]: Excluding path: /opt
[ INFO ]: Excluding path: /run
[ INFO ]: Excluding path: /proc
[ INFO ]: Excluding path: /dev
[ INFO ]: Excluding path: /mnt
[ INFO ]: Excluding path: /boot
[ INFO ]: Excluding path: /root
[ INFO ]: Excluding path: /etc
[ INFO ]: Excluding path: /srv
[ INFO ]: Excluding path: /usr
[ INFO ]: Excluding path: /media
[ INFO ]: Excluding path: /sys
[ INFO ]: Excluding path: /var
[ INFO ]: Excluding path: /home
[ INFO ]: Excluding path: /protected
[ INFO ]: Excluding path: /app
[ INFO ]: Comparing current system state with Pyro file...
[ WARNING ]: Scorch will remove system resources not specified in 'Full System Management Test'
[ WARNING ]: This is a DESTRUCTIVE operation that cannot be undone!

Are you sure about this? [Y/N]> y

[ INFO ]: Purging all state and report data
[ OK ]: All data purged
[ INFO ]: Loading sketch file: pyroflow.sketch.json
[ OK ]: Loaded procedure: Pyroform Auto-Generated Sketch Full System Management Test
[ INFO ]: Starting procedure execution with state monitoring
[ INFO ]: Procedure state set to STARTED
[ INFO ]: State monitoring active - process can be controlled externally
[ INFO ]: Beginning controlled procedure execution...
[ INFO ]: Processing stage: Cleanup
[ INFO ]: Processing action: Cleanup extra users
[ INFO ]: Executing Procedure Stage Action: Cleanup extra users
CMD> # for user in news man www-data irc sys proxy backup intruder _apt daemon games scorchtest root nobody mail uucp lp sync bin list; do userdel -f -r $user; done


CMD> echo 'Eliminated: news man www-data irc sys proxy backup intruder _apt daemon games scorchtest root nobody mail uucp lp sync bin list'
Eliminated: news man www-data irc sys proxy backup intruder _apt daemon games scorchtest root nobody mail uucp lp sync bin list

[ OK ]: Action completed: Cleanup extra users
[ INFO ]: Processing action: Cleanup extra groups
[ INFO ]: Executing Procedure Stage Action: Cleanup extra groups
CMD> # for group in disk man floppy irc fax kmem dialout proxy cdrom daemon games scorchtest video operator mail tape lp tty sudo plugdev shadow list news www-data voice sasl sys dip src audio adm users backup intruder pyrotest2 nogroup r
oot staff utmp _ssh uucp bin pyrotest1; do groupdel $group; done


CMD> echo 'Eliminated: disk man floppy irc fax kmem dialout proxy cdrom daemon games scorchtest video operator mail tape lp tty sudo plugdev shadow list news www-data voice sasl sys dip src audio adm users backup intruder pyrotest2 nogrou
p root staff utmp _ssh uucp bin pyrotest1'
Eliminated: disk man floppy irc fax kmem dialout proxy cdrom daemon games scorchtest video operator mail tape lp tty sudo plugdev shadow list news www-data voice sasl sys dip src audio adm users backup intruder pyrotest2 nogroup root staf
f utmp _ssh uucp bin pyrotest1

[ OK ]: Action completed: Cleanup extra groups
[ INFO ]: Processing action: Cleanup extra directories
[ INFO ]: Executing Procedure Stage Action: Cleanup extra directories
CMD> # rm -rf /tmp


CMD> echo 'Eliminated: /tmp'
Eliminated: /tmp

[ OK ]: Action completed: Cleanup extra directories
[ INFO ]: Processing action: Cleanup extra files and links
[ INFO ]: Executing Procedure Stage Action: Cleanup extra files and links
CMD> # rm -f /.pyroflow.state /tmp/shall_not_be_scorched.dummy /snapshot.yaml /.dockerenv


CMD> echo 'Eliminated: /.pyroflow.state /tmp/shall_not_be_scorched.dummy /snapshot.yaml /.dockerenv'
Eliminated: /.pyroflow.state /tmp/shall_not_be_scorched.dummy /snapshot.yaml /.dockerenv

[ OK ]: Action completed: Cleanup extra files and links
[ OK ]: Stage completed: Cleanup
[ OK ]: Procedure completed: SUCCESS
```

## 5. Analize output to ensure new user and file should have been scorched
```text
...
CMD> # for user in news man www-data irc sys proxy backup intruder _apt daemon games scorchtest root nobody mail uucp lp sync bin list; do userdel -f -r $user; done
CMD> # rm -f /.pyroflow.state /tmp/shall_not_be_scorched.dummy /snapshot.yaml /.dockerenv
...
```

## 6. Verify user and file have not actually been removed
```text
root@1e1b62138bef:/app/Pyroform# id scorchtest
uid=1008(scorchtest) gid=1011(scorchtest) groups=1011(scorchtest)
```
```text
root@1e1b62138bef:/app/Pyroform# ls -allah /tmp/shall_not_be_scorched.dummy
-rw-r--r-- 1 root root 0 Dec  1 22:45 /tmp/shall_not_be_scorched.dummy
```

