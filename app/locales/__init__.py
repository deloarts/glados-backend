"""
Locales module
"""

from db.models import UserModel
from locales.deAT import deAT
from locales.enGB import enGB
from locales.languageModel import LanguageModel


def lang(user: UserModel) -> LanguageModel:
    if user.language == "enGB":
        return enGB  # type:ignore
    elif user.language == "deAT":
        return deAT  # type:ignore
    return enGB  # type:ignore
