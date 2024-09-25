"""
    DB user schema.
"""

from datetime import datetime
from typing import Optional

from config import cfg
from pydantic import BaseModel
from pydantic import Field


class ProjectBaseSchema(BaseModel):
    """Shared properties."""

    number: str = Field(..., min_length=1, pattern=cfg.items.bought.validation.project)
    product_number: Optional[str] = Field(pattern=cfg.items.bought.validation.product)
    customer: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    designated_user_id: int = Field(..., gt=0)
    is_active: Optional[bool] = True


class ProjectCreateSchema(ProjectBaseSchema):
    """Properties to receive via API on creation."""


class ProjectUpdateSchema(ProjectBaseSchema):
    """Properties to receive via API on update."""


class ProjectInDBBaseSchema(ProjectBaseSchema):
    """Properties stored in DB."""

    id: int
    created: datetime


class ProjectSchema(ProjectInDBBaseSchema):
    """Additional properties to return via API."""

    number: str
    product_number: Optional[str]
    customer: str
    description: str
    designated_user_id: int


class ProjectInDBSchema(ProjectInDBBaseSchema):
    """Additional properties stored in DB."""
