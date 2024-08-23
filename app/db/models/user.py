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
from sqlalchemy.orm import relationship
from sqlalchemy.sql import false

# For correct relations between the models, they must be imported with their native name.
# This is the class name from the model itself.
# Do not import the models like this: UserModel, BoughtItemModel, ...
if TYPE_CHECKING:
    from db.models.bought_item import BoughtItem  # noqa: F401


class User(Base):
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
    bought_items = relationship("db.models.bought_item.BoughtItem", back_populates="creator")
