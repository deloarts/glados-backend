"""
    Mail sender submodule.
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from multiprocessing import Process

import dill
from config import cfg
from mail import Mail
from mail import Receiver
from multilog import log


class SendProcess(Process):
    """Middleman class for serializing closure function send_mail."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._target = dill.dumps(self._target)  # Save the target function as bytes

    def run(self):
        if self._target:
            self._target = dill.loads(self._target)  # Unpickle the target function before executing
            self._target(*self._args, **self._kwargs)  # type: ignore


def send_mail(receiver: Receiver, mail: Mail, force: bool = False) -> None:
    """Sends email using SMTP.

    Args:
        receiver (Receiver): The receiver object.
        mail (Mail): The mail object.
    """

    if not (cfg.mailing.server and cfg.mailing.port and cfg.mailing.account and cfg.mailing.password):
        log.warning("Mailing is disabled: Missing required information in the config file")
        return

    if cfg.debug and not force:
        if cfg.mailing.debug_no_send or not cfg.mailing.debug_receiver:
            log.warning("Debug-Mode: Mails are not sent.")
            return
        receiver.to = [cfg.mailing.debug_receiver]
        receiver.cc = []
        receiver.bcc = []
        log.warning(f"Debug-Mode: Redirecting mail to {cfg.mailing.debug_receiver!r}.")

    if receiver.cc is None:
        receiver.cc = []

    if receiver.bcc is None:
        receiver.bcc = []

    to_list = list(filter(None, receiver.to + receiver.cc + receiver.bcc))

    msg = MIMEMultipart("alternative")
    msg["From"] = cfg.mailing.account
    msg["Subject"] = f"DEBUG | {mail.subject}" if cfg.debug else mail.subject
    msg["To"] = ", ".join(receiver.to)
    msg["Cc"] = ", ".join(receiver.cc)
    msg["Bcc"] = ", ".join(receiver.bcc)
    msg.attach(MIMEText(mail.body, "html"))

    def send():  # TODO: Refactor this.
        if not (cfg.mailing.server and cfg.mailing.port and cfg.mailing.account and cfg.mailing.password):
            log.error("Mailing is disabled")
            return

        smtp = smtplib.SMTP(cfg.mailing.server, cfg.mailing.port)
        try:
            smtp.ehlo("mylowercasehost")
            smtp.starttls()
            smtp.ehlo("mylowercasehost")
            smtp.login(cfg.mailing.account, cfg.mailing.password)
            smtp.sendmail(cfg.mailing.account, to_list, msg.as_string())
            log.info(f"Sent mail to {to_list!r}")
        except Exception as e:
            log.error(f"Failed sending mail: {e!r}")
        finally:
            smtp.quit()

    process = SendProcess(target=send)
    process.start()


def send_test_mail(receiver_mail: str) -> None:
    receiver = Receiver(to=[receiver_mail])
    mail = Mail(subject="Glados test mail", body="This is a test mail.")
    send_mail(receiver=receiver, mail=mail, force=True)
