from typing import Dict
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
    target_sizes: Dict[int, int]

    # utility

    def iterate_sizes(self) -> Iterator[int]:
        """
        yields all lengths, sorted descending
        """

        # sort descending to favor combining larger sizes first
        for size, quantity in sorted(self.target_sizes.items(), reverse=True):
            for _ in range(quantity):
                yield size

    def sizes_from_list(self, sizes_list: List[TargetSize]):
        known_sizes = {}

        # list to dict to make them unique
        for size in sizes_list:
            if size.length in known_sizes:
                known_sizes[size.length] += size.quantity
            else:
                known_sizes[size.length] = size.quantity

        self.target_sizes = known_sizes

    def sizes_as_list(self) -> List[TargetSize]:
        """
        Compatibility function
        """
        # back to list again for compatibility
        return [TargetSize(length=l, quantity=q) for (l, q) in self.target_sizes.items()]

    def assert_valid(self):
        if self.max_length <= 0:
            raise ValueError(f"Job has invalid max_length {self.max_length}")
        if self.cut_width < 0:
            raise ValueError(f"Job has invalid cut_width {self.cut_width}")
        if len(self.target_sizes) <= 0:
            raise ValueError(f"Job is missing target_sizes")
        if any(size > (self.max_length - self.cut_width) for size in self.target_sizes.keys()):
            raise ValueError(f"Job has target sizes longer than the stock")

    def __len__(self) -> int:
        """
        Number of target sizes in job
        """
        return sum(self.target_sizes.values())

    def __eq__(self, other):
        return (
            self.max_length == other.max_length
            and self.cut_width == other.cut_width
            and self.target_sizes == other.target_sizes
        )

    def __hash__(self) -> int:
        return hash((self.max_length, self.cut_width, str(sorted(self.target_sizes.items()))))
