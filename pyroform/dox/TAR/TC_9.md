# Directory Structure Creation
- Test Environment: Docker container with Debian GNU/Linux 13 (trixie) 6.6.15-amd64
- Tester: D:Ta
- Date: 18/11/2025
- Pyroform Version: 1.0.0
- Validates: [TPS TC_9](../TPS/TC_9.md)
- Preconditions: System has some test users/files not in config
- Status:
[ ] PASS
[ ] FAIL
[ ] BLOCKED

# Archive

## 1.
```text

```

## 2.
```text

```

## 3.
```text

```

## 4.
```text

```

## 5.
```text

```

## 6.
```text

```

## 7.
```text

```


Miscellaneous


[ DEBUG ]: compared - {'missing_users': [], 'extra_users': [{'username': 'sys', 'uid': 3, 'home_directory': '/dev'}, {'username': 'nobody', 'uid': 65534, 'home_directory': '/nonexistent'}, {'username': 'list', 'uid': 38, 'home_directory':
 '/var/list'}, {'username': 'backup', 'uid': 34, 'home_directory': '/var/backups'}, {'username': 'bin', 'uid': 2, 'home_directory': '/bin'}, {'username': 'root', 'uid': 0, 'home_directory': '/root'}, {'username': '_apt', 'uid': 42, 'home_
directory': '/nonexistent'}, {'username': 'games', 'uid': 5, 'home_directory': '/usr/games'}, {'username': 'irc', 'uid': 39, 'home_directory': '/run/ircd'}, {'username': 'www-data', 'uid': 33, 'home_directory': '/var/www'}, {'username': '
lp', 'uid': 7, 'home_directory': '/var/spool/lpd'}, {'username': 'sync', 'uid': 4, 'home_directory': '/bin'}, {'username': 'daemon', 'uid': 1, 'home_directory': '/usr/sbin'}, {'username': 'man', 'uid': 6, 'home_directory': '/var/cache/man
'}, {'username': 'proxy', 'uid': 13, 'home_directory': '/bin'}, {'username': 'news', 'uid': 9, 'home_directory': '/var/spool/news'}, {'username': 'mail', 'uid': 8, 'home_directory': '/var/mail'}, {'username': 'uucp', 'uid': 10, 'home_dire
ctory': '/var/spool/uucp'}], 'user_mismatches': [{'label': 'test_user_1', 'username': 'pyrotest1', 'mismatches': [{'property': 'groups', 'expected': ['pyrogroup1'], 'actual': ['pyrotest1', 'pyrogroup1'], 'missing': [], 'extra': ['pyrotest
1']}]}, {'label': 'test_user_2', 'username': 'pyrotest2', 'mismatches': [{'property': 'groups', 'expected': ['pyrogroup2', 'pyrogroup1'], 'actual': ['pyrogroup2', 'pyrotest2', 'pyrogroup1'], 'missing': [], 'extra': ['pyrotest2']}]}], 'mis
sing_groups': [], 'extra_groups': [{'groupname': 'nogroup', 'gid': 65534, 'members': []}, {'groupname': 'pyrotest2', 'gid': 1003, 'members': []}, {'groupname': 'pyrotest1', 'gid': 1001, 'members': []}], 'group_mismatches': [], 'missing_di
rectories': [], 'extra_directories': [], 'directory_mismatches': [], 'missing_files': [], 'extra_files': [], 'file_mismatches': [], 'missing_symlinks': [], 'extra_symlinks': [], 'symlink_mismatches': [], 'missing_mountpoints': [], 'mountp
oint_mismatches': []}

    "extra_users": [
        {
            "username": "daemon",
            "uid": 1,
            "home_directory": "/usr/sbin"
        },
        {
            "username": "games",
            "uid": 5,
            "home_directory": "/usr/games"
        },
    "user_mismatches": [
        {
            "label": "test_user_1",
            "username": "pyrotest1",
            "mismatches": [
                {
                    "property": "groups",
                    "expected": [
                        "pyrogroup1"
                    ],
                    "actual": [
                        "pyrotest1",
                        "pyrogroup1"
                    ],
                    "missing": [],
                    "extra": [
                        "pyrotest1"
                    ]
                }
            ]
        },
    "extra_groups": [
        {
            "groupname": "pyrotest2",
            "gid": 1003,
            "members": []
        },
        {
            "groupname": "pyrotest1",
            "gid": 1001,
            "members": []
        },
        {
            "groupname": "nogroup",
            "gid": 65534,
            "members": []
        }
    ],
    "extra_directories": [
        {
            'path': '/root/.cache/pip/http-v2/7/5/0',
            'owner': 'root',
            'group': 'root',
            'permissions': '0755'
        },
    ]
    "extra_files": [
    "extra_symlinks": [
        {
            "path": "/sys/module/soundwire_intel/drivers/auxiliary:soundwire_intel",
            "owner": "root",
            "group": "root",
            "permissions": "0777",
            "target": "../../../bus/auxiliary/drivers/soundwire_intel"
        }
    ],
    "missing_mountpoints": [
        {
            "label": "test_fs",
            "mountpoint": "/tmp/pyrotest"
        }
    ],
