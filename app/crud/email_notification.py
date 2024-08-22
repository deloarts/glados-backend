"""
    Create-Read-Update-Delete: Email Notification
"""

from typing import List
from typing import Optional

from api.schemas.email_notification import EmailNotificationCreateSchema
from api.schemas.email_notification import EmailNotificationUpdateSchema
from crud.base import CRUDBase
from db.models import EmailNotificationModel
from multilog import log
from sqlalchemy.orm import Session


class CRUDEmailNotification(
    CRUDBase[
        EmailNotificationModel,
        EmailNotificationCreateSchema,
        EmailNotificationUpdateSchema,
    ]
):
    """CRUDEmailNotification class. Descendent of the CRUDBase class."""

    def get_all(self, db: Session) -> Optional[List[EmailNotificationModel]]:
        """Returns all pending email notifications."""
        return db.query(EmailNotificationModel).all()

    def get_by_receiver_id(self, db: Session, *, receiver_id: int) -> Optional[List[EmailNotificationModel]]:
        """Returns all pending email notifications for a specific user."""
        return db.query(EmailNotificationModel).filter_by(receiver_id=receiver_id).all()

    def get_distinct_receiver_ids(self, db: Session) -> Optional[List[int]]:
        """Returns a list of all distinct user ids."""
        query = db.query(EmailNotificationModel.receiver_id).distinct().all()
        try:
            return [item[0] for item in query]
        except:
            return []

    def create(self, db: Session, *, obj_in: EmailNotificationCreateSchema) -> EmailNotificationModel:
        """Creates a new email notification by the given schema."""
        db_obj = super().create(db, obj_in=obj_in)
        log.info(
            f"Created new pending email notification for user ID={obj_in.receiver_id!r}"
            f" about bought-item ID={obj_in.bought_item_id}, ID={db_obj.id}."
        )
        return db_obj

    def delete(self, db: Session, *, id: int) -> Optional[EmailNotificationModel]:
        """Deletes an email notification by its id."""
        db_obj = super().delete(db, id=id)
        log.info(f"Deleted email notification with ID={id}.")
        return db_obj


crud_email_notification = CRUDEmailNotification(EmailNotificationModel)
