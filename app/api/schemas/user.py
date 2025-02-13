"""
    DB user schema.
"""

from datetime import datetime
from datetime import time
from typing import Optional

from config import cfg
from pydantic import BaseModel
from pydantic import Field


class UserBaseSchema(BaseModel):
    """Shared properties."""

    username: str = Field(..., min_length=1)
    full_name: str = Field(..., min_length=1)
    email: str = Field(..., min_length=1)

    work_hours_per_week: Optional[float] = Field(default=None)
    auto_break_from: Optional[time] = Field(default=None)
    auto_break_to: Optional[time] = Field(default=None)
    auto_logout: Optional[bool] = True

    is_active: Optional[bool] = True
    is_adminuser: Optional[bool] = False
    is_superuser: Optional[bool] = False
    is_guestuser: Optional[bool] = False


class UserCreateSchema(UserBaseSchema):
    """Properties to receive via API on creation."""

    is_systemuser: Optional[bool] = False

    password: str = Field(..., min_length=cfg.security.min_pw_len)
    rfid: Optional[str] = Field(None, min_length=8)


class UserUpdateSchema(UserBaseSchema):
    """Properties to receive via API on update."""

    full_name: Optional[str] = Field(None, min_length=1)
    language: Optional[str] = Field(None, min_length=1)
    theme: Optional[str] = Field(None, min_length=1)
    password: Optional[str] = Field(None, min_length=cfg.security.min_pw_len)
    rfid: Optional[str] = Field(None, min_length=8)


class UserInDBBaseSchema(UserBaseSchema):
    """Properties stored in DB."""

    id: int
    created: datetime


class UserSchema(UserInDBBaseSchema):
    """Additional properties to return via API."""

    is_systemuser: bool
    language: str
    theme: Optional[str]
    hashed_rfid: Optional[str]


class UserInDBSchema(UserInDBBaseSchema):
    """Additional properties stored in DB."""

    hashed_password: str
    personal_access_token: str
