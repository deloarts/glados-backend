"""
    Database models

    Models must be imported and renamed.
    Throughout the app all db models are uses as e.g. UserModel (to distinguish them from other objects).
    But: For correct relations and for alembic the models must be imported with their correct base name, e.g. User.
"""

from db.models.api_key import APIKey as APIKeyModel
from db.models.bought_item import BoughtItem as BoughtItemModel
from db.models.email_notification import EmailNotification as EmailNotificationModel
from db.models.project import Project as ProjectModel
from db.models.user import User as UserModel
from db.models.user_time import UserTime as UserTimeModel
