"""Declarative base for the database."""

# pylint: disable=E0213,R0903

from typing import Any

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Declarative db base class."""

    id: Any
    __name__: str

    # Automatic table naming has been removed in alembic revision f74f18d478ec
    # Now all db models need to be named manually by setting __tablename__
    # @declared_attr
    # def __tablename__(cls) -> str:
    #     return cls.__name__.lower()
