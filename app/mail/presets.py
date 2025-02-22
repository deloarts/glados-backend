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

SAMPLE_WELCOME = "welcome.sample.j2"
SAMPLE_DISC_SPACE_WARN = "disc_space_warning.sample.j2"
SAMPLE_SCHEDULE_ERROR = "schedule_error.sample.j2"


class MailPreset:
    """The preset class. Has only static methods."""

    @staticmethod
    def send_schedule_error(task_name: str, message: str) -> None:
        """Send a schedule error message to the init-systemuser."""
        log.info(f"Sending schedule error email notification to {cfg.init.mail!r}...")

        if Path(TEMPLATES, cfg.templates.mail_schedule_error).exists():
            body = render_template(template_file=Path(TEMPLATES, cfg.templates.mail_schedule_error), **locals())
        else:
            log.error(f"Mail template file {cfg.templates.mail_schedule_error!r} not found")
            body = render_template(template_file=Path(TEMPLATES, SAMPLE_SCHEDULE_ERROR), **locals())

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
        log.info(f"Sending disc space warning email notification to {cfg.init.mail!r}...")

        if Path(TEMPLATES, cfg.templates.mail_disc_space_warning).exists():
            body = render_template(template_file=Path(TEMPLATES, cfg.templates.mail_disc_space_warning), **locals())
        else:
            log.error(f"Mail template file {cfg.templates.mail_disc_space_warning!r} not found")
            body = render_template(template_file=Path(TEMPLATES, SAMPLE_DISC_SPACE_WARN), **locals())

        receiver = Receiver(to=[cfg.init.mail])
        mail = Mail(subject="Glados Notification Service", body=body)
        send_mail(receiver=receiver, mail=mail)

    @staticmethod
    def send_welcome_mail(email: str, full_name: str, username: str, password: str) -> None:
        """Send a welcome mail for new users."""
        local_url = cfg.server.domain
        log.info(f"Sending welcome email to {email!r}...")

        if Path(TEMPLATES, cfg.templates.mail_welcome).exists():
            body = render_template(template_file=Path(TEMPLATES, cfg.templates.mail_welcome), **locals())
        else:
            log.error(f"Mail template file {cfg.templates.mail_welcome!r} not found")
            body = render_template(template_file=Path(TEMPLATES, SAMPLE_WELCOME), **locals())

        receiver = Receiver(to=[email])
        mail = Mail(subject="Glados Notification Service", body=body)
        send_mail(receiver=receiver, mail=mail)
