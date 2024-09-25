"""
    DB project model.
"""

# pylint: disable=C0115,R0903

from datetime import datetime
from typing import TYPE_CHECKING
from typing import List
from typing import Optional

from db.base import Base
from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

# For correct relations between the models, they must be imported with their native name.
# This is the class name from the model itself.
# Do not import the models like this: UserModel, BoughtItemModel, ...
if TYPE_CHECKING:
    from db.models.bought_item import BoughtItem  # noqa: F401
    from db.models.user import User  # noqa: F401


class Project(Base):
    __tablename__ = "project_table"

    # data handled by the server
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, unique=True, nullable=False)
    created: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # data given on creation
    number: Mapped[str] = mapped_column(String, index=True, unique=True, nullable=False)
    product_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    customer: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # relations
    designated_user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user_table.id", name="fk_project_table_designated_user_id_user_table"),
        nullable=False,
    )
    designated_user: Mapped["User"] = relationship(
        "db.models.user.User",
        back_populates="projects",
        foreign_keys=[designated_user_id],
    )

    bought_items: Mapped[List["BoughtItem"]] = relationship(
        "db.models.bought_item.BoughtItem",
        back_populates="project",
        foreign_keys="db.models.bought_item.BoughtItem.project_id",
    )
