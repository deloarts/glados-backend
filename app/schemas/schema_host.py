"""
    Host-endpoint schema.
"""

from datetime import datetime
from typing import List

from config import Config
from pydantic import BaseModel


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
