"""
    DB bought item model.
"""

# pylint: disable=C0115,R0903

from typing import TYPE_CHECKING

from config import cfg
from db.base import Base
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import PickleType
from sqlalchemy import String
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import relationship
from sqlalchemy.sql import false

if TYPE_CHECKING:
    from db.models.model_user import User  # noqa: F401


class BoughtItem(Base):  # type: ignore
    # data handled by the server
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        unique=True,
        nullable=False,
        autoincrement=True,
    )
    created = Column(Date, nullable=False)
    changed = Column(Date, nullable=True)
    changes = Column(MutableList.as_mutable(PickleType), nullable=False, default=[])
    deleted = Column(Boolean, nullable=False, default=False)

    # data given on creation/update
    high_priority = Column(Boolean, nullable=False, default=False, server_default=false())
    notify_on_delivery = Column(Boolean, nullable=False, default=False)
    group_1 = Column(String, nullable=True)
    project = Column(String, index=True, nullable=False)
    machine = Column(String, nullable=True)
    quantity = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    partnumber = Column(String, nullable=False)
    definition = Column(String, nullable=False)
    supplier = Column(String, nullable=True)
    manufacturer = Column(String, nullable=False)
    weblink = Column(String, nullable=True)
    note_general = Column(String, nullable=True)
    note_supplier = Column(String, nullable=True)
    desired_delivery_date = Column(Date, nullable=True)

    # data given on single value update
    status = Column(String, nullable=False, default=cfg.items.bought.status.default)
    requester_id = Column(Integer, nullable=True)  # changed with status
    requested_date = Column(Date, nullable=True)  # changed with status
    orderer_id = Column(Integer, nullable=True)  # changed with status
    ordered_date = Column(Date, nullable=True)  # changed with status
    expected_delivery_date = Column(Date, nullable=True)
    taken_over_id = Column(Integer, nullable=True)  # changed with status
    delivery_date = Column(Date, nullable=True)  # changed with status
    storage_place = Column(String, nullable=True)

    # relations
    creator_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    creator = relationship("db.models.model_user.User", back_populates="bought_items")
