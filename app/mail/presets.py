"""
    Mailing presets submodule.
"""

# pylint: disable=R0913

from pathlib import Path

from config import cfg
from const import TEMPLATES
from mail import Mail
from mail import Receiver
from mail.render import render_template
from mail.send import send_mail
from multilog import log


class MailPreset:
    """The preset class. Has only static methods."""

    @staticmethod
    def send_schedule_error(task_name: str, message: str) -> None:
        """Send a schedule error message to the init-systemuser."""
        log.info(f"Sending schedule error email notification to {cfg.init.mail!r}...")
        body = render_template(
            template_file=Path(TEMPLATES, cfg.templates.mail_schedule_error), **locals()
        )
        receiver = Receiver(to=[cfg.init.mail])
        mail = Mail(subject="Glados Notification Service", body=body)
        send_mail(receiver=receiver, mail=mail)

    @staticmethod
    def send_disc_space_warning(
        db_total: float,
        db_used: float,
        db_free: float,
        db_path: str,
        backup_total: float,
        backup_used: float,
        backup_free: float,
        backup_path: str,
    ) -> None:
        """Send a disc space warning message to the init-systemuser."""
        log.info(
            f"Sending disc space warning email notification to {cfg.init.mail!r}..."
        )
        body = render_template(
            template_file=Path(TEMPLATES, cfg.templates.mail_disc_space_warning),
            **locals(),
        )
        receiver = Receiver(to=[cfg.init.mail])
        mail = Mail(subject="Glados Notification Service", body=body)
        send_mail(receiver=receiver, mail=mail)
