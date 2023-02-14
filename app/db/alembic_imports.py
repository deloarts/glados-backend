"""
Required if you use alembic for db migrations.
"""

# pylint: disable=W0611

# Import all the models, so that Base has them before being
# imported by Alembic
from db.base import Base  # isort: skip
from models.model_user import User  # isort: skip
from models.model_bought_item import BoughtItem  # isort: skip
from models.model_api_key import APIKey  # isort: skip
from models.model_email_notification import EmailNotification  # isort: skip
