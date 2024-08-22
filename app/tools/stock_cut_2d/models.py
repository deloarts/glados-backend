"""
    Stock Cut 2D: Models
"""

from typing import List
from typing import Optional

from opcut.common import Cut
from opcut.common import Method
from pydantic import BaseModel
from pydantic import Field


class PanelModel(BaseModel):
    id: str = Field(...)
    width: float = Field(..., gt=0)
    height: float = Field(..., gt=0)


class ItemModel(BaseModel):
    id: str = Field(...)
    width: float = Field(..., gt=0)
    height: float = Field(..., gt=0)
    can_rotate: bool = Field(default=True)


class UsedModel(BaseModel):
    panel: PanelModel = Field(...)
    item: ItemModel = Field(...)
    x: float = Field(..., ge=0)
    y: float = Field(..., ge=0)
    rotate: bool = Field(default=True)


class UnusedModel(BaseModel):
    panel: PanelModel = Field(...)
    x: float = Field(..., ge=0)
    y: float = Field(..., ge=0)
    width: float = Field(..., gt=0)
    height: float = Field(..., gt=0)


class ParameterModel(BaseModel):
    items: List[ItemModel] = Field(
        ..., min_length=1, description="The rectangular areas that are cut out from a panel."
    )
    panels: List[PanelModel] = Field(..., min_length=1, description="The rectangular base from which to cut items.")
    cut_width: int = Field(default=0, ge=0)
    min_initial_usage: bool = Field(default=True)


class JobModel(BaseModel):
    params: ParameterModel = Field(...)
    method: Method = Field(...)


class ResultModel(BaseModel):
    params: ParameterModel = Field(...)
    used: List[UsedModel] = Field(default_factory=list)
    unused: List[UnusedModel] = Field(default_factory=list)
    cuts: Optional[List[Cut]]
