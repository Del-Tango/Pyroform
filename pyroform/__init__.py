"""
Pyroform - Linux Configuration Management Tool

A tool that receives input file(s) containing list of users, user groups,
block storage device mountpoints, files and directories with owners and permissions,
generates on the fly FlowCTRL sketch files based on input pyro file(s),
and runs them using the flow_ctrl library.
"""

__version__ = "0.1.0"
__author__ = "Pyroform Team"
__description__ = "Linux Configurator tool written in Python3"

# Import key classes for easy access
from .src.models import PyroConfig, User, Group, Device, ActionType
from .src.parser import PyroParser

__all__ = [
    'PyroConfig',
    'User',
    'Group',
    'Device',
    'ActionType',
    'PyroParser',
    '__version__',
    '__author__',
    '__description__'
]

# CODE DUMP

#   # pyroform/__init__.py
#   from .src.core import PyroformEngine
#   from .src.models import PyroConfig, ActionType

#   class Pyroform:
#       def __init__(self, config_file: str = None, auto_confirm: bool = False):
#           self.engine = PyroformEngine(config_file, auto_confirm)

#       def configure(self, input_path: str, **kwargs) -> bool:
#           """Library method for configure action"""
#           pass

#       def scorch(self, input_path: str, **kwargs) -> bool:
#           """Library method for scorch action"""
#           pass

#       # ... other actions
