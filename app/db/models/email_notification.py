"""
    DB user model.
"""

# pylint: disable=C0115,R0903

from db.base import Base
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String


class EmailNotification(Base):
    # data handled by the server
    id = Column(Integer, primary_key=True, index=True, unique=True, nullable=False)

    # data given on creation
    reason = Column(String, nullable=False)
    receiver_id = Column(Integer, nullable=False)
    bought_item_id = Column(Integer, nullable=False)
