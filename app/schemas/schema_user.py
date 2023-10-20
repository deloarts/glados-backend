"""
    DB user schema.
"""

from datetime import datetime
from typing import Optional

from config import cfg
from pydantic import BaseModel
from pydantic import Field


class UserBase(BaseModel):
    """Shared properties."""

    username: str = Field(..., min_length=1)
    full_name: str = Field(..., min_length=1)
    email: str = Field(...)
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False


class UserCreate(UserBase):
    """Properties to receive via API on creation."""

    is_systemuser: Optional[bool] = False
    password: str = Field(..., min_length=cfg.security.min_pw_len)


class UserUpdate(UserBase):
    """Properties to receive via API on update."""

    password: Optional[str] = Field(None, min_length=cfg.security.min_pw_len)


class UserInDBBase(UserBase):
    """Properties stored in DB."""

    id: int
    created: datetime

    class Config:
        orm_mode = True


class User(UserInDBBase):
    """Additional properties to return via API."""

    is_systemuser: bool


class UserInDB(UserInDBBase):
    """Additional properties stored in DB."""

    hashed_password: str
    personal_access_token: str
