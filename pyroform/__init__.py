"""
Pyroform - Linux Configuration Management Tool

A tool that receives input file(s) containing list of users, user groups,
block storage device mountpoints, files and directories with owners and permissions,
generates on the fly FlowCTRL sketch files based on input pyro file(s),
and runs them using the flow_ctrl library.
"""

__version__ = "1.0.0"
__author__ = "Alveare Solutions"
__description__ = "Linux Configurator tool"

from .cli import cli, execute_workflow

# Import the main Pyroform class and CLI functions
from .pyroform import Pyroform, PyroformEngine
from .src.flow_engine import PyroflowEngine

# Import key classes for easy access
from .src.models import ActionType, Device, Group, PyroConfig, User
from .src.parser import PyroParser
from .src.reporter import ReportGenerator
from .src.sketch_generator import SketchGenerator
from .src.validator import SystemValidator, ValidationResult

__all__ = [
    "Pyroform",
    "cli",
    "execute_workflow",
    "PyroConfig",
    "User",
    "Group",
    "Device",
    "ActionType",
    "PyroParser",
    "SketchGenerator",
    "PyroflowEngine",
    "SystemValidator",
    "ValidationResult",
    "ReportGenerator",
    "__version__",
    "__author__",
    "__description__",
]

# CODE DUMP
# from .src.scorch_engine import ScorchEngine, ScorchResult
#   "ScorchEngine",
#   "ScorchResult",
