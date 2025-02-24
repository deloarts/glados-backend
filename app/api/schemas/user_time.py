"""
    DB user time schema.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from pydantic import ConfigDict


class UserTimeBaseSchema(BaseModel):
    """Shared properties."""

    login: Optional[datetime]
    logout: Optional[datetime]
    note: Optional[str]


class UserTimeCreateSchema(UserTimeBaseSchema):
    """Properties to receive via API on creation."""

    login: datetime


class UserTimeUpdateSchema(UserTimeBaseSchema):
    """Properties to receive via API on update."""

    login: datetime


class UserTimeInDBBaseSchema(UserTimeBaseSchema):
    """Properties stored in DB."""

    id: int
    user_id: int

    # Required for pagination
    model_config = ConfigDict(from_attributes=True)


class UserTimeSchema(UserTimeInDBBaseSchema):
    """Additional properties to return via API."""

    duration_minutes: Optional[float]


class UserTimeNoLogoutSchema(UserTimeSchema):
    """Schema for user time entries where no logout time is logged"""

    logout: None
    duration_minutes: None


class UserTimeInDBSchema(UserTimeInDBBaseSchema):
    """Additional properties stored in DB."""
