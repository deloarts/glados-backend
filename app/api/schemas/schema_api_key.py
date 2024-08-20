"""
    DB api key schema.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class APIKeyBase(BaseModel):
    """Shared properties."""

    name: str
    expiration_date: Optional[datetime]


class APIKeyCreate(APIKeyBase):
    """Properties to receive via API on creation."""

    expiration_date: datetime


class APIKeyUpdate(APIKeyBase):
    """Properties to receive via API on update."""


class APIKeyInDBBase(APIKeyBase):
    """Database properties."""

    id: int
    api_key: str
    created: datetime


class APIKey(APIKeyInDBBase):
    """Additional properties to return via API."""


class APIKeyInDB(APIKeyInDBBase):
    """Additional properties stored in DB."""

    deleted: bool
