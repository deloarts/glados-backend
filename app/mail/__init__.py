"""
    Mailing submodule.
"""

# pylint: disable=C0115

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Mail:
    subject: str
    body: str


@dataclass
class Receiver:
    to: List[str]
    cc: Optional[List[str]] = None
    bcc: Optional[List[str]] = None
