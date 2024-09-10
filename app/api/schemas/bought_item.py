"""
    DB BoughtItem schema.
"""

from datetime import date
from typing import Annotated
from typing import List
from typing import Literal
from typing import Optional

from config import cfg
from pydantic import BaseModel
from pydantic import BeforeValidator
from pydantic import Field

# This type includes str, int, float, ...
# It includes anything that can be converted to a string,
# but it doesn't allow None
IncludingString = Annotated[str, BeforeValidator(lambda s: str(s) if s is not None else None)]


class BoughtItemBaseSchema(BaseModel):
    """Shared properties."""


class BoughtItemCreateSchema(BoughtItemBaseSchema):
    """Properties to receive via API on creation from "BoughtItem"."""

    high_priority: Optional[bool] = False
    notify_on_delivery: Optional[bool] = False
    group_1: Optional[str] = None
    project_id: int = Field(..., gt=0)
    quantity: float = Field(..., gt=0)
    unit: Literal[tuple(cfg.items.bought.units.values)] = Field(cfg.items.bought.units.default)  # type: ignore
    partnumber: str = Field(..., min_length=1)
    definition: IncludingString = Field(..., min_length=1)
    supplier: Optional[str] = None
    manufacturer: str = Field(..., min_length=1)
    weblink: Optional[str] = None
    note_general: Optional[str] = None
    note_supplier: Optional[str] = None
    desired_delivery_date: Optional[date] = None


class BoughtItemUpdateSchema(BoughtItemCreateSchema):
    """Properties to receive via API on update from "BoughtItem"."""


class BoughtItemInDBBaseSchema(BoughtItemBaseSchema):
    """Properties stored in DB."""

    id: int
    status: str
    created: date
    creator_id: int


class BoughtItemSchema(BoughtItemInDBBaseSchema):
    """Additional properties to return to api."""

    high_priority: bool
    notify_on_delivery: bool
    project_id: int
    project_number: str
    project_is_active: bool
    machine: Optional[str]
    quantity: float
    unit: str
    partnumber: str
    definition: str
    manufacturer: str
    supplier: Optional[str]
    weblink: Optional[str]
    group_1: Optional[str]
    note_general: Optional[str]
    note_supplier: Optional[str]
    desired_delivery_date: Optional[date]
    creator_full_name: str
    requester_id: Optional[int]
    requester_full_name: Optional[str]
    requested_date: Optional[date]
    orderer_id: Optional[int]
    orderer_full_name: Optional[str]
    ordered_date: Optional[date]
    expected_delivery_date: Optional[date]
    receiver_id: Optional[int]
    receiver_full_name: Optional[str]
    delivery_date: Optional[date]
    storage_place: Optional[str]


class BoughtItemInDBSchema(BoughtItemInDBBaseSchema):
    """Additional properties stored in DB."""

    changes: List[str]


class BoughtItemExcelExportSchema(BoughtItemBaseSchema):
    """Additional properties for creating the excel export."""

    id: int
    status: str
    # project_id: int
    project_number: str
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
