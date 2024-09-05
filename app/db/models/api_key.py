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
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class APIKey(Base):
    __tablename__ = "api_key_table"

    # data handled by the server:
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, unique=True, nullable=False)
    api_key: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    created: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # data given on creation:
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    expiration_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    def __init__(self, name: str, expiration_date: datetime) -> None:
        self.created = datetime.now(UTC)
        self.api_key = secrets.token_urlsafe(32)

        self.name = name
        if isinstance(expiration_date, datetime):
            self.expiration_date = expiration_date
        else:
            self.expiration_date = parser.parse(expiration_date)
