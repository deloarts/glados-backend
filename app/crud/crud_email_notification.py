"""
    Create-Read-Update-Delete: Email Notification
"""

from typing import List, Optional

from crud.crud_base import CRUDBase
from models import model_email_notification
from multilog import log
from schemas import schema_email_notification
from sqlalchemy.orm import Session


class CRUDEmailNotification(
    CRUDBase[
        model_email_notification.EmailNotification,
        schema_email_notification.EmailNotificationCreate,
        schema_email_notification.EmailNotificationUpdate,
    ]
):
    """CRUDEmailNotification class. Descendent of the CRUDBase class."""

    def get_all(
        self, db: Session
    ) -> Optional[List[model_email_notification.EmailNotification]]:
        """Returns all pending email notifications."""
        return db.query(model_email_notification.EmailNotification).all()

    def get_by_receiver_id(
        self, db: Session, *, receiver_id: int
    ) -> Optional[List[model_email_notification.EmailNotification]]:
        """Returns all pending email notifications for a specific user."""
        return (
            db.query(model_email_notification.EmailNotification)
            .filter_by(receiver_id=receiver_id)
            .all()
        )

    def get_distinct_receiver_ids(self, db: Session) -> Optional[List[int]]:
        """Returns a list of all distinct user ids."""
        query = db.query(
            model_email_notification.EmailNotification.receiver_id
        ).distinct()
        try:
            return query[0]
        except:
            return []

    def create(
        self, db: Session, *, obj_in: schema_email_notification.EmailNotificationCreate
    ) -> model_email_notification.EmailNotification:
        """Creates a new email notification by the given schema."""
        db_obj = super().create(db, obj_in=obj_in)
        log.info(
            f"Created new pending email notification for {obj_in.receiver_id!r} "
            f"about item ID={obj_in.bought_item_id}, ID={db_obj.id}."
        )
        return db_obj

    def delete(
        self,
        db: Session,
        *,
        id: int,  # pylint: disable=W0622
    ) -> Optional[model_email_notification.EmailNotification]:
        """Deletes an email notification by its id."""
        db_obj = super().delete(db, id=id)
        log.info(f"Deleted email notification with ID={id}.")
        return db_obj


email_notification = CRUDEmailNotification(model_email_notification.EmailNotification)
