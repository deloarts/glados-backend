"""
    DB user time model.
"""

# pylint: disable=C0115,R0903

from datetime import datetime
from typing import TYPE_CHECKING
from typing import Optional

from db.base import Base
from sqlalchemy import DateTime
from sqlalchemy import Float
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
    from db.models.user import User  # noqa: F401


class UserTime(Base):
    __tablename__ = "user_time_table"

    # data handled by the server
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, unique=True, nullable=False)
    duration_minutes: Mapped[float] = mapped_column(Float, nullable=True)

    # data given by user
    login: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    logout: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    note: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # relations
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user_table.id", name="fk_user_time_table_user_id_user_table"),
        nullable=False,
    )
    user: Mapped["User"] = relationship(
        "db.models.user.User",
        back_populates="user_time",
        foreign_keys=[user_id],
    )
