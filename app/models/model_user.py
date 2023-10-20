"""
    DB user model.
"""

# pylint: disable=C0115,R0903

from typing import TYPE_CHECKING

from db.base import Base
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import false

if TYPE_CHECKING:
    from models.model_bought_item import BoughtItem  # noqa: F401


class User(Base):  # type: ignore
    # __table_args__ = {"extend_existing": True}

    # data handled by the server
    id = Column(Integer, primary_key=True, index=True, unique=True, nullable=False)
    created = Column(DateTime, nullable=False)
    personal_access_token = Column(String, nullable=True)

    # data given on creation
    username = Column(String, index=True, unique=True, nullable=False)
    full_name = Column(String, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    is_superuser = Column(Boolean, nullable=False, default=False)
    is_systemuser = Column(
        Boolean, nullable=False, default=False, server_default=false()
    )

    # relations
    bought_items = relationship(
        "models.model_bought_item.BoughtItem", back_populates="creator"
    )
