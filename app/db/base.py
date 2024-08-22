"""Declarative base for the database."""

# pylint: disable=E0213,R0903

from typing import Any

from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.ext.declarative import declared_attr


@as_declarative()
class Base:
    """Declarative db base class."""

    id: Any
    __name__: str

    # Generate __tablename__ automatically
    # @declared_attr
    # def __tablename__(cls) -> str:
    #     return cls.__name__.lower()
