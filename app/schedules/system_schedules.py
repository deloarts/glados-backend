"""
    Handles files schedules.
"""
import shutil
from pathlib import Path

from config import cfg
from const import DB_PRODUCTION
from mail.presets import MailPreset
from multilog import log
from schedules.base_schedules import BaseSchedules


class SystemSchedules(BaseSchedules):
    """Class for schedules."""

    def __init__(self) -> None:
        """Initializes the system schedules."""
        super().__init__()

        self.add(
            function=self._get_disc_space,
            hour=cfg.schedules.system_hour,
        )

        if cfg.debug:
            self._get_disc_space()

    def _get_disc_space(self) -> None:
        db_total, db_used, db_free = shutil.disk_usage(DB_PRODUCTION.parent)
        db_total = db_total // (2**30)
        db_used = db_used // (2**30)
        db_free = db_free // (2**30)
        db_path = DB_PRODUCTION.parent.resolve()

        backup_total, backup_used, backup_free = shutil.disk_usage(
            cfg.filesystem.db_backup.path
        )
        backup_total = backup_total // (2**30)
        backup_used = backup_used // (2**30)
        backup_free = backup_free // (2**30)
        backup_path = Path(cfg.filesystem.db_backup.path).resolve()

        if (
            db_free < cfg.filesystem.disc_space_warning
            or backup_free < cfg.filesystem.disc_space_warning
        ):
            log.warning(
                f"Disc space is running low (<{cfg.filesystem.disc_space_warning}GB)"
            )
            MailPreset.send_disc_space_warning(
                db_total,
                db_used,
                db_free,
                str(db_path),
                backup_total,
                backup_used,
                backup_free,
                str(backup_path),
            )