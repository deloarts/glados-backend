"""
    DB user model.

    Important note: There can only be one `system user`.
    This user is created at db init.
"""

# pylint: disable=C0115,R0903

from datetime import datetime
from typing import TYPE_CHECKING
from typing import List
from typing import Optional

from db.base import Base
from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.sql import false
from sqlalchemy.sql import text

# For correct relations between the models, they must be imported with their native name.
# This is the class name from the model itself.
# Do not import the models like this: UserModel, BoughtItemModel, ...
if TYPE_CHECKING:
    from db.models.bought_item import BoughtItem  # noqa: F401
    from db.models.project import Project  # noqa: F401


class User(Base):
    __tablename__ = "user_table"

    # __table_args__ = {"extend_existing": True}

    # data handled by the server
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, unique=True, nullable=False)
    created: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    personal_access_token: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # data given on creation
    username: Mapped[str] = mapped_column(String, index=True, unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    hashed_rfid: Mapped[str] = mapped_column(String, unique=True, nullable=True)
    language: Mapped[str] = mapped_column(String, nullable=False, server_default="enGB")
    theme: Mapped[str] = mapped_column(String, nullable=True, server_default="dark")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_adminuser: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=false())
    is_guestuser: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=false())
    is_systemuser: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=false())

    # relations
    projects: Mapped[List["Project"]] = relationship(
        "db.models.project.Project",
        back_populates="designated_user",
        foreign_keys="db.models.project.Project.designated_user_id",
    )

    created_bought_items: Mapped[List["BoughtItem"]] = relationship(
        "db.models.bought_item.BoughtItem",
        back_populates="creator",
        foreign_keys="db.models.bought_item.BoughtItem.creator_id",
    )
    requested_bought_items: Mapped[List["BoughtItem"]] = relationship(
        "db.models.bought_item.BoughtItem",
        back_populates="requester",
        foreign_keys="db.models.bought_item.BoughtItem.requester_id",
    )
    ordered_bought_items: Mapped[List["BoughtItem"]] = relationship(
        "db.models.bought_item.BoughtItem",
        back_populates="orderer",
        foreign_keys="db.models.bought_item.BoughtItem.orderer_id",
    )
    received_items: Mapped[List["BoughtItem"]] = relationship(
        "db.models.bought_item.BoughtItem",
        back_populates="receiver",
        foreign_keys="db.models.bought_item.BoughtItem.receiver_id",
    )
