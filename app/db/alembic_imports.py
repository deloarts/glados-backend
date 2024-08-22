"""
Required if you use alembic for db migrations.
"""

# pylint: disable=W0611

# Import all the models, so that Base has them before being imported by Alembic.

# For alembic to recognize the models correctly, they must be imported with their native name.
# This is the class name from the model itself.
# Do not import the models like this: UserModel, BoughtItemModel, ...

from db.base import Base  # isort: skip
from db.models.user import User  # isort: skip
from db.models.bought_item import BoughtItem  # isort: skip
from db.models.api_key import APIKey  # isort: skip
from db.models.email_notification import EmailNotification  # isort: skip
