"""
    DB api key schema.
"""

from typing import Literal

from pydantic import BaseModel, Field


class EmailNotificationBase(BaseModel):
    """Shared properties."""

    reason: Literal["delivered", "late"] = Field(...)
    receiver_id: int = Field(..., gt=0)
    bought_item_id: int = Field(..., gt=0)


class EmailNotificationCreate(EmailNotificationBase):
    """Properties to receive via API on creation."""


class EmailNotificationUpdate(EmailNotificationBase):
    """Properties to receive via API on update."""


class EmailNotificationInDBBase(EmailNotificationBase):
    """Database properties."""

    id: int


class EmailNotification(EmailNotificationBase):
    """Additional properties to return via API."""


class EmailNotificationInDB(EmailNotificationBase):
    """Additional properties stored in DB."""
