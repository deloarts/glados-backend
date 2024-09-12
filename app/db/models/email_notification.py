"""
    DB user model.
"""

# pylint: disable=C0115,R0903

from db.base import Base
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class EmailNotification(Base):
    __tablename__ = "email_notification_table"

    # data handled by the server
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, unique=True, nullable=False)

    # data given on creation
    reason: Mapped[str] = mapped_column(String, nullable=False)
    receiver_id: Mapped[int] = mapped_column(Integer, nullable=False)
    bought_item_id: Mapped[int] = mapped_column(Integer, nullable=False)
