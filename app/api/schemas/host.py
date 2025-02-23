"""
    Host-endpoint schema.
"""

from datetime import datetime
from typing import List

from config import Config
from config import ConfigMailing
from pydantic import BaseModel
from utilities.config_editor.bought_items import ConfigBoughtItems
from utilities.config_editor.bought_items import ConfigBoughtItemsFilter
from utilities.disc_space import DiscSpace


class HostVersionSchema(BaseModel):
    """Host version schema."""

    version: str


class HostTimeSchema(BaseModel):
    """Host time schema."""

    now: datetime
    timezone: str


class HostConfigSchema(BaseModel):
    """Host configuration schema."""

    now: datetime
    config: Config


class HostConfigMailingSchema(BaseModel):
    """Host configuration schema for the mailing part."""

    enabled: bool
    config: ConfigMailing


class HostInfoSchema(BaseModel):
    """Host configuration schema."""

    now: datetime
    version: str
    os: str
    hostname: str
    disc_space: DiscSpace


class HostConfigItemsBoughtStatusSchema(BaseModel):
    """Bought item status schema."""

    open: str
    requested: str
    ordered: str
    late: str
    partial: str
    delivered: str
    canceled: str
    lost: str


class HostConfigItemsBoughtUnitsSchema(BaseModel):
    """Bought item units schema."""

    default: str
    values: List[str]


class HostConfigItemsBoughtSchema(ConfigBoughtItems):
    """Bought item config."""


class HostConfigItemsBoughtFilterSchema(ConfigBoughtItemsFilter):
    """Bought item db filter keys."""


class HostConfigItemsBoughtFilterAddSchema(HostConfigItemsBoughtFilterSchema):
    """Bought item db filter object on creation."""


class HostConfigItemsBoughtFilterUpdateSchema(HostConfigItemsBoughtFilterAddSchema):
    """Bought item db filter object on update."""
