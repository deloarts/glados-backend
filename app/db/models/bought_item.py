"""
    DB bought item model.
"""

# pylint: disable=C0115,R0903

from datetime import date
from typing import TYPE_CHECKING
from typing import List
from typing import Optional

from config import cfg
from db.base import Base
from pydantic import ConfigDict
from sqlalchemy import Boolean
from sqlalchemy import Date
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import PickleType
from sqlalchemy import String
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.sql import false

# For correct relations between the models, they must be imported with their native name.
# This is the class name from the model itself.
# Do not import the models like this: UserModel, BoughtItemModel, ...
if TYPE_CHECKING:
    from db.models.project import Project  # noqa: F401
    from db.models.user import User  # noqa: F401


class BoughtItem(Base):
    __tablename__ = "bought_item_table"
    model_config = ConfigDict(from_attributes=True)

    # data handled by the server
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        unique=True,
        nullable=False,
        autoincrement=True,
    )
    created: Mapped[date] = mapped_column(Date, nullable=False)
    changed: Mapped[date] = mapped_column(Date, nullable=True)
    changes: Mapped[List] = mapped_column(MutableList.as_mutable(PickleType), nullable=False, default=[])  # type:ignore
    deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # data given on creation/update
    high_priority: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=false())
    notify_on_delivery: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    group_1: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String, nullable=False)
    partnumber: Mapped[str] = mapped_column(String, nullable=False)
    definition: Mapped[str] = mapped_column(String, nullable=False)
    supplier: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    manufacturer: Mapped[str] = mapped_column(String, nullable=False)
    weblink: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    note_general: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    note_supplier: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    desired_delivery_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # data given on single value update
    status: Mapped[str] = mapped_column(String, nullable=False, default=cfg.items.bought.status.default)
    requested_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)  # changed with status
    ordered_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)  # changed with status
    expected_delivery_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    delivery_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)  # changed with status
    storage_place: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # relations
    project_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("project_table.id", name="fk_bought_item_table_project_id_project_table"),
        nullable=False,
    )
    project: Mapped["Project"] = relationship(
        "db.models.project.Project",
        back_populates="bought_items",
        foreign_keys=[project_id],
    )

    creator_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user_table.id", name="fk_bought_item_table_creator_id_user_table"),
        nullable=False,
    )
    creator: Mapped["User"] = relationship(
        "db.models.user.User",
        back_populates="created_bought_items",
        foreign_keys=[creator_id],
    )

    # Warning: requester_id and requester is None at creation and only changed with status
    requester_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("user_table.id", name="fk_bought_item_table_requester_id_user_table"),
        nullable=True,
    )
    requester: Mapped[Optional["User"]] = relationship(
        "db.models.user.User",
        back_populates="requested_bought_items",
        foreign_keys=[requester_id],
    )

    # Warning: orderer_id and orderer is None at creation and only changed with status
    orderer_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("user_table.id", name="fk_bought_item_table_orderer_id_user_table"),
        nullable=True,
    )
    orderer: Mapped[Optional["User"]] = relationship(
        "db.models.user.User",
        back_populates="ordered_bought_items",
        foreign_keys=[orderer_id],
    )

    # Warning: receiver_id and receiver is None at creation and only changed with status
    receiver_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("user_table.id", name="fk_bought_item_table_receiver_id_user_table"),
        nullable=True,
    )
    receiver: Mapped[Optional["User"]] = relationship(
        "db.models.user.User",
        back_populates="received_items",
        foreign_keys=[receiver_id],
    )

    # associations
    project_number = association_proxy("project", "number")
    project_is_active = association_proxy("project", "is_active")
    machine = association_proxy("project", "machine")
    creator_full_name = association_proxy("creator", "full_name")
    requester_full_name = association_proxy("requester", "full_name")
    orderer_full_name = association_proxy("orderer", "full_name")
    receiver_full_name = association_proxy("creator", "full_name")
