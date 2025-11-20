"""
Pyroform Data Models
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Set
from enum import Enum


class ActionType(Enum):
    CONFIGURE = "configure"
    SCORCH = "scorch"
    MOUNT = "mount"
    VALIDATE = "validate"


@dataclass
class User:
    label: str
    name: str
    password: str
    groups: List[str]


@dataclass
class Group:
    label: str
    name: str
    users: List[str]


@dataclass
class Device:
    label: str
    path: str
    partition: int
    mountpoint: str
    state: List[str]  # dir|fl,path,owner,group,permissions


@dataclass
class PyroConfig:
    label: str
    users: List[User]
    groups: List[Group]
    devices: List[Device]

    def __post_init__(self):
        """Validate required fields after initialization"""
        if not self.label:
            raise ValueError("PyroConfig must have a label")

        # Ensure lists are initialized even if None
        self.users = self.users or []
        self.groups = self.groups or []
        self.devices = self.devices or []


@dataclass
class FileInfo:
    path: str
    owner: str
    group: str
    permissions: str
    type: str


@dataclass
class ScorchResult:
    """Result of scorch operation"""

    resources_removed: List[str]
    resources_failed: List[Dict[str, Any]]
    dry_run: bool
    success: bool


# CODE DUMP

