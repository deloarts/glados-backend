"""
    DB api key model.
"""

# pylint: disable=C0115,R0903

import secrets
from datetime import UTC
from datetime import datetime

from dateutil import parser
from db.base import Base
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String


class APIKey(Base):  # type: ignore
    # data handled by the server:
    id = Column(Integer, primary_key=True, index=True, unique=True, nullable=False)
    api_key = Column(String, unique=True, nullable=False)
    created = Column(DateTime, nullable=False)
    deleted = Column(Boolean, default=False, nullable=False)

    # data given on creation:
    name = Column(String, unique=True, nullable=False)
    expiration_date = Column(DateTime, nullable=False)

    def __init__(self, name: str, expiration_date: datetime) -> None:
        self.created = datetime.now(UTC)
        self.api_key = secrets.token_urlsafe(32)

        self.name = name
        if isinstance(expiration_date, datetime):
            self.expiration_date = expiration_date
        else:
            self.expiration_date = parser.parse(expiration_date)
