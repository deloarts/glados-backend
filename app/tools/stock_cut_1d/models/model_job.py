"""
    Stock Cutting Solver: Job model
"""

from typing import Iterator
from typing import List

from pydantic import BaseModel


class TargetSize(BaseModel):
    length: int
    quantity: int

    def __lt__(self, other):
        """
        compares lengths
        """
        return self.length < other.length

    def __str__(self):
        return f"l:{self.length}, n:{self.quantity}"


class Job(BaseModel):
    max_length: int
    cut_width: int = 0
    target_sizes: List[TargetSize]

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
