"""
Locales module
"""

from enum import Enum
from enum import unique

from db.models import UserModel
from locales.de_AT import deAT
from locales.en_GB import enGB

Language = type[enGB] | type[deAT]


@unique
class Locales(str, Enum):
    EN_GB = "enGB"
    DE_AT = "deAT"


def lang(user: UserModel | None) -> Language:
    if not user:
        return enGB
    match user.language:
        case Locales.EN_GB:
            return enGB
        case Locales.DE_AT:
            return deAT
        case _:
            return enGB
