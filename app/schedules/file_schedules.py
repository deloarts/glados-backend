"""
    Handles files schedules.
"""

import os
import shutil
from datetime import datetime
from pathlib import Path

from config import cfg
from const import DB_DEVELOPMENT, DB_PRODUCTION, TEMP, UPLOADS
from mail.presets import MailPreset
from multilog import log
from schedules.base_schedules import BaseSchedules


class FileSchedules(BaseSchedules):
    """Class for schedules."""

    def __init__(self) -> None:
        """Initializes the file schedules."""
        super().__init__()

        # Make sure all directories exist for all schedules
        os.makedirs(TEMP, exist_ok=True)
        os.makedirs(UPLOADS, exist_ok=True)

        self.add(function=self._delete_temp, hour=cfg.schedules.delete_temp_hour)
        self.add(function=self._delete_uploads, hour=cfg.schedules.delete_uploads_hour)
        self.add(function=self._backup_database, hour=cfg.schedules.backup_db_hour)

        if cfg.debug:
            self._delete_temp()
            self._delete_uploads()
            self._backup_database()

    def _delete_temp(self) -> None:
        try:
            Files.delete_content(path=TEMP)
        except Exception as e:
            log.error(f"Could not delete content from temp directory: {e}")
            MailPreset.send_schedule_error("Delete Temp Files", str(e))

    def _delete_uploads(self) -> None:
        try:
            Files.delete_content(path=UPLOADS)
        except Exception as e:
            log.error(f"Could not delete content from uploads directory: {e}")
            MailPreset.send_schedule_error("Delete Uploaded Files", str(e))

    def _backup_database(self) -> None:
        backup_dir = Path(cfg.filesystem.db_backup.path)
        if not backup_dir.exists():
            log.error(msg := f"Backup destination {str(backup_dir)!r} does not exist.")
            MailPreset.send_schedule_error("Database Backup", msg)
            return

        if cfg.filesystem.db_backup.is_mount and not backup_dir.is_mount():
            log.error(msg := f"Backup destination {str(backup_dir)!r} is not mounted.")
            MailPreset.send_schedule_error("Database Backup", msg)
            return

        try:
            Files.copy_file(
                src=DB_DEVELOPMENT if cfg.debug else DB_PRODUCTION,
                dst=backup_dir,
                timestamp=True,
            )
        except Exception as e:
            log.error(f"Could not create database backup: {e}")
            MailPreset.send_schedule_error("Database Backup", str(e))


class Files:
    """File handler (helper for the schedules)."""

    @staticmethod
    def copy_file(src: Path, dst: Path, timestamp: bool = False) -> None:
        """Copies a single file."""
        if timestamp:
            stem = src.stem
            ext = src.suffix
            dst = Path(dst, f"{stem}.{datetime.now().strftime('%Y%m%d%H%M%S')}{ext}")
        try:
            shutil.copy(src, dst)
            log.info(f"Copied file {src.name!r} to {str(dst)!r}")
        except Exception as e:
            raise Exception(e) from e

    @staticmethod
    def delete_file(path: Path) -> None:
        """Deletes a single file."""
        try:
            os.remove(path)
            log.info(f"Deleted file {path.name!r} from {str(path)!r}")
        except Exception as e:
            raise Exception(e) from e

    @staticmethod
    def delete_content(path: Path) -> None:
        """Deletes all files inside the folder."""
        if path.is_file():
            Files.delete_file(path=path)
            log.info(f"Deleted files {str(path)!r}")
        elif len(os.listdir(path)) == 0:
            log.info(f"Nothing to delete, folder {str(path)!r} is already empty")
        else:
            for filename in os.listdir(path):
                Files.delete_file(path=Path(path, filename))
            log.info(f"Deleted files in folder {str(path)!r}")
