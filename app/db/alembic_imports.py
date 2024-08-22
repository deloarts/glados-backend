"""
Required if you use alembic for db migrations.
"""

# pylint: disable=W0611

# Import all the models, so that Base has them before being imported by Alembic
from db.base import Base  # isort: skip
from db.models.user import UserModel  # isort: skip
from db.models.bought_item import BoughtItemModel  # isort: skip
from db.models.api_key import APIKeyModel  # isort: skip
from db.models.email_notification import EmailNotificationModel  # isort: skip
