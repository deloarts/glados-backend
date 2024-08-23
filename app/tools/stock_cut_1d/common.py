"""
    Stock Cutting 1D: Common
"""

from enum import Enum
from enum import unique


@unique
class SolverType(str, Enum):
    bruteforce = "bruteforce"
    FFD = "FFD"
