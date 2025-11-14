# YAML Configuration Parsing
- Test Environment: Docker container with Amazon Linux 2023.6.20241121 6.6.15-amd64
- Tester: D:Ta
- Date: 14/11/2025, 11/11/2025
- Pyroform Version: 1.0.0
- Validates: [TPS TC_3](../TPS/TC_3.md)
- Status:
[ ] PASS
[X] FAIL
[ ] BLOCKED

# Remarks

- Pyro file (YAML) validation failed at step 2:
    - Action 'validate' cannot be given as sub-command, only option flag (e.g. --validate);
    - No explicit reason given for failure, at least not upfront;
    - Debug flag did apparently nothing. Expected verbosity level to increase;

- Pyro file (YAML) configuration failed at step 3:
    - Action 'configure' cannot be given as sub-command, only option flag (e.g. --configure)
    - Dry-run cannot be configured via CLI, only config file.

# Archive

## 1. Create dummy Pyro file
```text
    bash-5.2# cat test_config.pyro.yaml
    Label: "Test Configuration"
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
```

## 2. Run validation command using previously created Pyro file
```text
    bash-5.2# pyroform validate -i test_config.pyro.yaml

        ___________________________________________________________________________

        *                          *   Pyroform   *                           *
        ___________________________________________________________________________
                        Regards, the Alveare Solutions #!/Society -x


    [ INFO ]: Parsing Pyro state file (test_config.pyro.yaml)...
    [ INFO ]: State file data: {
        "Label": "Test Configuration",
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
        ]
    }
    [ NOK ]: Discrepancies [
        {
            "type": "user",
            "name": "testuser",
            "issue": "User does not exist",
            "critical": true
        },
        {
            "type": "group",
            "name": "testgroup",
            "issue": "Group does not exist",
            "critical": true
        },
        {
            "type": "mount",
            "device": "/tmp/test_mount",
            "mountpoint": "/mnt/test",
            "issue": "Device not mounted",
            "critical": false
        }
    ]
    [ NOK ]: Machine state does not correspond with Pyro config Test Configuration
    [ NOK ]: (2) critical issues identified
    [ NOK ]: (3) total issues identified
    [ NOK ]: Machine state does not correspond!

```

## 3. Dry-run of configuration
```text
    bash-5.2# pyroform --configure -i test_config.pyro.yaml --dry-run

```

### Miscellaneous
```text
    bash-5.2# python3.12 -m pip uninstall pyroform -y && python3.12 -m pip install dist/pyroform-1.0.0-py3-none-any.whl && pyroform configure -i dump/test_config.pyro.yaml -o . --debug --dry-run #2> /dev/null
    bash-5.2# pyroform --configure -i test_config.pyro.yaml --dry-run --debug

    ___________________________________________________________________________

    *                          *   Pyroform   *                           *
    ___________________________________________________________________________
                    Regards, the Alveare Solutions #!/Society -x


Source path:... /usr/local/lib/python3.12/site-packages/pyroform/cli.py
Starting var:.. action_type = <ActionType.CONFIGURE: 'configure'>
Starting var:.. input_path = PosixPath('dump/test_config.pyro.yaml')
Starting var:.. output_path = PosixPath('.')
Starting var:.. config_file = None
Starting var:.. log_file = None
Starting var:.. dump_report = False
Starting var:.. silent = False
Starting var:.. debug = True
Starting var:.. auto_confirm = False
Starting var:.. dry_run = True
23:01:22.425473 call       468 def _execute_action(
23:01:22.426185 line       494     start_time = datetime.now().isoformat()
New var:....... start_time = '2025-11-13T23:01:22.426271'
23:01:22.426282 line       499     try:
23:01:22.426367 line       501         pyroform_kwargs = {"auto_confirm": auto_confirm}
New var:....... pyroform_kwargs = {'auto_confirm': False}
23:01:22.426430 line       502         if config_file and config_file.exists():
23:01:22.426510 line       505         pf = Pyroform(**pyroform_kwargs)
    Source path:... /usr/local/lib/python3.12/site-packages/pyroform/src/flow_engine.py
    Starting var:.. self = <pyroform.src.flow_engine.PyroflowEngine object at 0x7f3683c8a390>
    Starting var:.. config_path = None
    23:01:22.426659 call        94     def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
    23:01:22.426859 line       104         if config_path and Path(config_path).exists():
    23:01:22.426905 line       117         return self._default_config()
        Source path:... /usr/local/lib/python3.12/site-packages/pyroform/src/flow_engine.py
        Starting var:.. self = <pyroform.src.flow_engine.PyroflowEngine object at 0x7f3683c8a390>
        23:01:22.426959 call       232     def _default_config(self) -> Dict[str, Any]:
        23:01:22.427030 line       240             "state_file": "/tmp/pyroform_state.json",
        23:01:22.427069 line       241             "logging": {"level": "INFO", "file": "/var/log/pyroform_flowctrl.log"},
        23:01:22.427097 line       243                 "max_retries": 3,
        23:01:22.427154 line       244                 "timeout": 300,
        23:01:22.427190 line       245                 "continue_on_failure": False,
        23:01:22.427215 line       242             "execution": {
        23:01:22.427249 line       248                 "generate_reports": True,
        23:01:22.427284 line       249                 "report_dir": "/var/log/pyroform/reports",
        23:01:22.427323 line       247             "reporting": {
        23:01:22.427362 line       239         return {
        23:01:22.427402 return     239         return {
        Return value:.. {'state_file': '/tmp/pyroform_state.json', 'logg...True, 'report_dir': '/var/log/pyroform/reports'}}
        Elapsed time: 00:00:00.000551
    23:01:22.427536 return     117         return self._default_config()
    Return value:.. {'state_file': '/tmp/pyroform_state.json', 'logg...True, 'report_dir': '/var/log/pyroform/reports'}}
    Elapsed time: 00:00:00.000984
    Source path:... /usr/local/lib/python3.12/site-packages/pyroform/src/flow_engine.py
    Starting var:.. self = <pyroform.src.flow_engine.PyroflowEngine object at 0x7f3683c8a390>
    23:01:22.427677 call        49     def _create_flow_config(self):
    23:01:22.427755 line        58         class FlowConfig:
    New var:....... FlowConfig = <class 'pyroform.src.flow_engine.PyroflowEngine._create_flow_config.<locals>.FlowConfig'>
    23:01:22.427813 line        71         return FlowConfig(self.config)
    23:01:22.427915 return      71         return FlowConfig(self.config)
    Return value:.. <pyroform.src.flow_engine.PyroflowEngine._create...fig.<locals>.FlowConfig object at 0x7f3683c8a870>
    Elapsed time: 00:00:00.000313
23:01:22.428183 exception  505         pf = Pyroform(**pyroform_kwargs)
Exception:..... AttributeError: 'FlowConfig' object has no attribute 'project_dir'
23:01:22.430138 line       568     except Exception as e:
New var:....... e = AttributeError("'FlowConfig' object has no attribute 'project_dir'")
23:01:22.430550 line       571         if debug:
23:01:22.431142 line       572             import traceback
New var:....... traceback = <module 'traceback' from '/usr/lib64/python3.12/traceback.py'>
23:01:22.431370 line       574             click.echo(traceback.format_exc())
Traceback (most recent call last):
  File "/usr/local/lib/python3.12/site-packages/pyroform/cli.py", line 505, in _execute_action
    pf = Pyroform(**pyroform_kwargs)
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/pyroform/pyroform.py", line 41, in __init__
    self.engine = PyroformEngine(self.config)
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/pyroform/src/pyroform_engine.py", line 47, in __init__
    self.flow_engine = PyroflowEngine(stdout=self.stdout)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/pyroform/src/flow_engine.py", line 37, in __init__
    self.flow_engine = FlowEngine(flow_config)
                       ^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/flow_ctrl/src/core/engine.py", line 46, in __init__
    self._setup_logging()
  File "/usr/local/lib/python3.12/site-packages/flow_ctrl/src/core/engine.py", line 52, in _setup_logging
    log_dir = Path(self.config.project_dir) / self.config.log_dir
                   ^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'FlowConfig' object has no attribute 'project_dir'

23:01:22.439909 return     574             click.echo(traceback.format_exc())
Return value:.. None
Elapsed time: 00:00:00.015156



    bash-5.2# pyroform --configure -i test_config.pyro.yaml --dry-run
    Usage: pyroform [OPTIONS]
    Try 'pyroform --help' for help.

    Error: No such option: --dry-run


    bash-5.2# pyroform configure -i test_config.yaml
    Usage: pyroform [OPTIONS]
    Try 'pyroform --help' for help.

    Error: Got unexpected extra argument (configure)


    bash-5.2# pyroform --configure -i test_config.pyro.yaml

        ___________________________________________________________________________

        *                          *   Pyroform   *                           *
        ___________________________________________________________________________
                        Regards, the Alveare Solutions #!/Society -x

    Executing configure action with input: test_config.pyro.yaml
    Configure action completed successfully
```
