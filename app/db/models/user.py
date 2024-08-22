"""
    DB user model.

    Important note: There can only be one `system user`.
    This user is created at db init.
"""

# pylint: disable=C0115,R0903

from typing import TYPE_CHECKING

from db.base import Base
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship
from sqlalchemy.sql import false

if TYPE_CHECKING:
    from db.models import BoughtItemModel  # noqa: F401


class UserModel(Base):
    @declared_attr
    def __tablename__(cls) -> str:
        return "user"

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
    is_adminuser = Column(Boolean, nullable=False, default=False, server_default=false())
    is_guestuser = Column(Boolean, nullable=False, default=False, server_default=false())
    is_systemuser = Column(Boolean, nullable=False, default=False, server_default=false())

    # relations
    bought_items = relationship("db.models.bought_item.BoughtItemModel", back_populates="creator")
