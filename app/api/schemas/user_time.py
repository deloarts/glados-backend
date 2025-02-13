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


class UserTimeCreateSchema(UserTimeBaseSchema):
    """Properties to receive via API on creation."""

    login: datetime
    logout: datetime


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


class UserTimeInDBSchema(UserTimeInDBBaseSchema):
    """Additional properties stored in DB."""
