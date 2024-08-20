"""
    Stock cut schema.
"""

from typing import List

from pydantic import BaseModel
from pydantic import Field
from tools.stock_cut_1d.models.model_job import TargetSize
from tools.stock_cut_1d.models.model_result import SolverType


class Job(BaseModel):
    """Job schema for the stock cutting problem."""

    max_length: int = Field(..., gt=0)
    cut_width: int = Field(default=0, ge=0)
    target_sizes: List[TargetSize] = Field(default_factory=list)


class Result(BaseModel):
    """Result schema for the stock cutting problem."""

    job: Job
    solver_type: SolverType
    time_us: int
    lengths: List[List[int]]
