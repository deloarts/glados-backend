"""
Required if you use alembic for db migrations.
"""

# pylint: disable=W0611

# Import all the models, so that Base has them before being imported by Alembic
from db.base import Base  # isort: skip
from db.models import UserModel  # isort: skip
from db.models import BoughtItemModel  # isort: skip
from db.models import APIKeyModel  # isort: skip
from db.models import EmailNotificationModel  # isort: skip
