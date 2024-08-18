"""
    Stock Cutting Solver: Result model
"""

from enum import Enum
from enum import unique
from typing import List

from pydantic import BaseModel
from tools.stock_cut.models.model_job import Job


@unique
class SolverType(str, Enum):
    bruteforce = "bruteforce"
    FFD = "FFD"


class Result(BaseModel):
    job: Job
    solver_type: SolverType
    time_us: int = -1
    lengths: List[List[int]]

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
        if self.time_us < 0:
            raise ValueError(f"Result has invalid time {self.time_us!r}")
        if len(self.lengths) <= 0:
            raise ValueError("Result is missing lengths")
