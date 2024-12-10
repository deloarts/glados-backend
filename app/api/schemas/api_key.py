"""
    DB api key schema.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from pydantic import Field
from pydantic import computed_field


class APIKeyBaseSchema(BaseModel):
    """Shared properties."""

    name: str
    expiration_date: Optional[datetime]


class APIKeyCreateSchema(APIKeyBaseSchema):
    """Properties to receive via API on creation."""

    name: str = Field(..., min_length=1)
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

    @computed_field
    def expired(self) -> bool:
        if not self.expiration_date:
            return True
        return datetime.now() > self.expiration_date


class APIKeyInDBSchema(APIKeyInDBBaseSchema):
    """Additional properties stored in DB."""

    deleted: bool
