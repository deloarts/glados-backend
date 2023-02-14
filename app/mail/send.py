"""
    Mail sender submodule.
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from multiprocessing import Process

from config import cfg
from mail import Mail, Receiver
from multilog import log


def send_mail(receiver: Receiver, mail: Mail) -> None:
    """Sends email using SMTP.

    Args:
        receiver (Receiver): The receiver object.
        mail (Mail): The mail object.
    """

    if cfg.debug:
        if cfg.mailing.debug_no_send:
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
    msg["Subject"] = mail.subject
    msg["To"] = ", ".join(receiver.to)
    msg["Cc"] = ", ".join(receiver.cc)
    msg["Bcc"] = ", ".join(receiver.bcc)
    msg.attach(MIMEText(mail.body, "html"))

    def send():  # TODO: Refactor this.
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

    process = Process(target=send)
    process.start()
