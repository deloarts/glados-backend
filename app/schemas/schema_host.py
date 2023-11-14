"""
    Host-endpoint schema.
"""

from datetime import datetime
from typing import Dict
from typing import List

from pydantic import BaseModel
from utilities.config_editor.bought_items import ConfigBoughtItems
from utilities.config_editor.bought_items import ConfigBoughtItemsFilter
from utilities.disc_space import DiscSpace

from config import Config


class HostVersion(BaseModel):
    """Host version schema."""

    version: str


class HostTime(BaseModel):
    """Host time schema."""

    now: datetime
    timezone: str


class HostConfig(BaseModel):
    """Host configuration schema."""

    now: datetime
    config: Config


class HostInfo(BaseModel):
    """Host configuration schema."""

    now: datetime
    version: str
    os: str
    hostname: str
    disc_space: DiscSpace


class HostConfigItemsBoughtStatus(BaseModel):
    """Bought item status schema."""

    open: str
    requested: str
    ordered: str
    late: str
    partial: str
    delivered: str
    canceled: str
    lost: str


class HostConfigItemsBoughtUnits(BaseModel):
    """Bought item units schema."""

    default: str
    values: List[str]


class HostConfigItemsBought(ConfigBoughtItems):
    ...


class HostConfigItemsBoughtFilter(ConfigBoughtItemsFilter):
    ...


class HostConfigItemsBoughtFilterAdd(HostConfigItemsBoughtFilter):
    ...


class HostConfigItemsBoughtFilterUpdate(HostConfigItemsBoughtFilterAdd):
    ...
