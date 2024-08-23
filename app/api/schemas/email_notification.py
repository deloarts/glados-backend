"""
    DB api key schema.
"""

from typing import Literal

from pydantic import BaseModel
from pydantic import Field


class EmailNotificationBaseSchema(BaseModel):
    """Shared properties."""

    reason: Literal["delivered", "late"] = Field(...)
    receiver_id: int = Field(..., gt=0)
    bought_item_id: int = Field(..., gt=0)


class EmailNotificationCreateSchema(EmailNotificationBaseSchema):
    """Properties to receive via API on creation."""


class EmailNotificationUpdateSchema(EmailNotificationBaseSchema):
    """Properties to receive via API on update."""


class EmailNotificationInDBBaseSchema(EmailNotificationBaseSchema):
    """Database properties."""

    id: int


class EmailNotificationSchema(EmailNotificationBaseSchema):
    """Additional properties to return via API."""


class EmailNotificationInDBSchema(EmailNotificationBaseSchema):
    """Additional properties stored in DB."""
