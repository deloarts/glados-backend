"""
    DB api key schema.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class APIKeyBaseSchema(BaseModel):
    """Shared properties."""

    name: str
    expiration_date: Optional[datetime]


class APIKeyCreateSchema(APIKeyBaseSchema):
    """Properties to receive via API on creation."""

    expiration_date: datetime


class APIKeyUpdateSchema(APIKeyBaseSchema):
    """Properties to receive via API on update."""


class APIKeyInDBBaseSchema(APIKeyBaseSchema):
    """Database properties."""

    id: int
    api_key: str
    created: datetime


class APIKeySchema(APIKeyInDBBaseSchema):
    """Additional properties to return via API."""


class APIKeyInDBSchema(APIKeyInDBBaseSchema):
    """Additional properties stored in DB."""

    deleted: bool