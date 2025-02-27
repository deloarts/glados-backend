"""
    Handles files schedules.
"""

from pathlib import Path

from config import cfg
from const import TEMPLATES
from crud.bought_item import crud_bought_item
from crud.email_notification import crud_email_notification
from crud.user import crud_user
from fastapi.encoders import jsonable_encoder
from mail import Mail
from mail import Receiver
from mail.render import render_template
from mail.send import send_mail
from multilog import log
from schedules.base_schedules import BaseSchedules


class NotificationSchedules(BaseSchedules):
    """Class for schedules."""

    def __init__(self) -> None:
        """Initializes the notification schedules."""
        super().__init__()

        self.add(
            function=self._send_item_notification,
            hour=cfg.schedules.email_notifications_hour,
        )

        if cfg.debug:
            self._send_item_notification()

    def _send_item_notification(self) -> None:
        log.info("Running notification schedule: Sending pending bought item notifications.")

        pending = crud_email_notification.get_all(self.db)
        pending_count = len(pending) if pending else 0
        log.info(f"There are {pending_count} pending notifications.")

        receiver_ids = crud_email_notification.get_distinct_receiver_ids(self.db)
        if not receiver_ids:
            return
        log.debug(f"Notification receivers are {receiver_ids}.")

        for receiver_id in receiver_ids:
            current_user = crud_user.get(db=self.db, id=receiver_id)
            current_items = []
            pending_notifications = crud_email_notification.get_by_receiver_id(self.db, receiver_id=receiver_id)
            if not current_user or not pending_notifications:
                break

            for pending in pending_notifications:
                current_item = crud_bought_item.get(db=self.db, id=pending.bought_item_id)
                if not current_item:
                    break
                current_items.append(jsonable_encoder(current_item))
                crud_email_notification.delete(db=self.db, id=pending.id)

            log.info(f"Sending email notification to {current_user.email!r}...")

            if Path(TEMPLATES, cfg.templates.mail_item_notification).exists():
                body_path = Path(TEMPLATES, cfg.templates.mail_item_notification)
            else:
                log.error(f"Mail template file {cfg.templates.mail_item_notification!r} not found")
                body_path = Path(TEMPLATES, "item_notification.sample.j2")

            body = render_template(template_file=body_path, items=current_items, user=jsonable_encoder(current_user))
            receiver = Receiver(to=[current_user.email])
            mail = Mail(subject="Glados Notification Service", body=body)
            send_mail(receiver=receiver, mail=mail)
