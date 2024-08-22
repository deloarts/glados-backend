"""
    DB user schema.
"""

from datetime import datetime
from typing import Optional

from config import cfg
from pydantic import BaseModel
from pydantic import Field


class UserBaseSchema(BaseModel):
    """Shared properties."""

    username: str = Field(..., min_length=1)
    full_name: str = Field(..., min_length=1)
    email: str = Field(..., min_length=1)
    is_active: Optional[bool] = True
    is_adminuser: Optional[bool] = False
    is_superuser: Optional[bool] = False
    is_guestuser: Optional[bool] = False


class UserCreateSchema(UserBaseSchema):
    """Properties to receive via API on creation."""

    is_systemuser: Optional[bool] = False
    password: str = Field(..., min_length=cfg.security.min_pw_len)


class UserUpdateSchema(UserBaseSchema):
    """Properties to receive via API on update."""

    password: Optional[str] = Field(None, min_length=cfg.security.min_pw_len)


class UserInDBBaseSchema(UserBaseSchema):
    """Properties stored in DB."""

    id: int
    created: datetime


class UserSchema(UserInDBBaseSchema):
    """Additional properties to return via API."""

    is_systemuser: bool


class UserInDBSchema(UserInDBBaseSchema):
    """Additional properties stored in DB."""

    hashed_password: str
    personal_access_token: str