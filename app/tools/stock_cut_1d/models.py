"""
    Stock Cutting 1D: Model
"""

from typing import Iterator
from typing import List

from pydantic import BaseModel
from pydantic import Field
from tools.stock_cut_1d.common import SolverType


class TargetSizeModel(BaseModel):
    length: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)

    def __lt__(self, other):
        """
        compares lengths
        """
        return self.length < other.length

    def __str__(self):
        return f"l:{self.length}, n:{self.quantity}"


class JobModel(BaseModel):
    max_length: int = Field(..., gt=0)
    cut_width: int = Field(..., ge=0)
    target_sizes: List[TargetSizeModel] = Field(default_factory=list)

    def iterate_sizes(self) -> Iterator[int]:
        """
        yields all lengths, sorted descending
        """
        for item in self.target_sizes:
            for _ in range(item.quantity):
                yield item.length

    def assert_valid(self):
        if self.max_length <= 0:
            raise ValueError(f"Max length {self.max_length!r} is not valid")
        if self.cut_width < 0:
            raise ValueError(f"Cut width {self.cut_width!r} is not valid")
        if len(self.target_sizes) <= 0:
            raise ValueError(f"Target sizes are not set")
        if any(item.length > (self.max_length - self.cut_width) for item in self.target_sizes):
            raise ValueError(f"Some target sizes are longer than the stock")

    def __len__(self) -> int:
        """
        Number of target sizes in job
        """
        return sum(item.quantity for item in self.target_sizes)

    def __eq__(self, other):
        return (
            self.max_length == other.max_length
            and self.cut_width == other.cut_width
            and self.target_sizes == other.target_sizes
        )

    def __hash__(self) -> int:
        return hash((self.max_length, self.cut_width, str(sorted(self.target_sizes))))


class ResultModel(BaseModel):
    job: JobModel = Field(...)
    solver_type: SolverType = Field(...)
    time_us: int = Field(..., gt=0)
    lengths: List[List[int]] = Field(default_factory=list, min_length=1)

    def __eq__(self, other):
        return self.job == other.job and self.solver_type == other.solver_type and self.lengths == other.lengths

    def exactly(self, other):
        return (
            self.job == other.job
            and self.solver_type == other.solver_type
            and self.time_us == other.time_us
            and self.lengths == other.lengths
        )

    def assert_valid(self):
        self.job.assert_valid()
        if self.solver_type not in SolverType:
            raise ValueError(f"Result has invalid solver type {self.solver_type!r}")
