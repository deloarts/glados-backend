"""
    DB user model.
"""

# pylint: disable=C0115,R0903

from db.base import Base
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String

from sqlalchemy.ext.declarative import declared_attr


class EmailNotificationModel(Base):
    @declared_attr
    def __tablename__(cls) -> str:
        return "emailnotification"

    # data handled by the server
    id = Column(Integer, primary_key=True, index=True, unique=True, nullable=False)

    # data given on creation
    reason = Column(String, nullable=False)
    receiver_id = Column(Integer, nullable=False)
    bought_item_id = Column(Integer, nullable=False)
