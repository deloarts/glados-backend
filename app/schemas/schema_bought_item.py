"""
    DB BoughtItem schema.
"""

from datetime import date
from typing import List
from typing import Literal
from typing import Optional

from config import cfg
from pydantic import BaseModel
from pydantic import Field


class BoughtItemBase(BaseModel):
    """Shared properties."""


class BoughtItemCreate(BoughtItemBase):
    """Properties to receive via API on creation from "BoughtItem"."""

    high_priority: Optional[bool] = False
    notify_on_delivery: Optional[bool] = False
    group_1: Optional[str] = None
    project: str = Field(..., min_length=1)
    machine: Optional[str] = None
    quantity: float = Field(..., gt=0)
    unit: Literal[tuple(cfg.items.bought.units.values)] = Field(cfg.items.bought.units.default)  # type: ignore
    partnumber: str = Field(..., min_length=1)
    definition: str = Field(..., min_length=1)
    supplier: Optional[str] = None
    manufacturer: str = Field(..., min_length=1)
    note_general: Optional[str] = None
    note_supplier: Optional[str] = None
    desired_delivery_date: Optional[date] = None


class BoughtItemUpdate(BoughtItemCreate):
    """Properties to receive via API on update from "BoughtItem"."""


class BoughtItemInDBBase(BoughtItemBase):
    """Properties stored in DB."""

    id: int
    status: str
    created: date
    creator_id: int

    class Config:
        orm_mode = True


class BoughtItem(BoughtItemInDBBase):
    """Additional properties to return to api."""

    high_priority: bool
    notify_on_delivery: bool
    project: str
    machine: Optional[str]
    quantity: float
    unit: str
    partnumber: str
    definition: str
    manufacturer: str
    supplier: Optional[str]
    group_1: Optional[str]
    note_general: Optional[str]
    note_supplier: Optional[str]
    desired_delivery_date: Optional[date]
    requester_id: Optional[int]
    requested_date: Optional[date]
    orderer_id: Optional[int]
    ordered_date: Optional[date]
    expected_delivery_date: Optional[date]
    taken_over_id: Optional[int]
    delivery_date: Optional[date]
    storage_place: Optional[str]


class BoughtItemInDB(BoughtItemInDBBase):
    """Additional properties stored in DB."""

    changes: List[str]


class BoughtItemExcelExport(BoughtItemBase):
    """Additional properties for creating the excel export."""

    id: int
    status: str
    project: str
    machine: Optional[str]
    quantity: float
    unit: str
    partnumber: str
    definition: str
    manufacturer: str
    supplier: Optional[str]
    group_1: Optional[str]
    note_general: Optional[str]
    note_supplier: Optional[str]
    created: date
    desired_delivery_date: Optional[date]
    requested_date: Optional[date]
    ordered_date: Optional[date]
    expected_delivery_date: Optional[date]
    delivery_date: Optional[date]
    storage_place: Optional[str]
