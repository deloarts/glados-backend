"""
    Handles disc space related operations.
"""
import shutil
from dataclasses import dataclass
from pathlib import Path

from config import cfg
from const import DB_PRODUCTION
from multilog import log


@dataclass(slots=True, kw_only=True)
class DiscSpace:
    db_total: float
    db_used: float
    db_free: float
    db_path: Path

    backup_total: float
    backup_used: float
    backup_free: float
    backup_path: Path | None


def get_disc_space() -> DiscSpace:
    """Returns the disc space of the host system.

    Returns:
        DiscSpace: The disc space dataclass.
    """
    db_total, db_used, db_free = shutil.disk_usage(DB_PRODUCTION.parent)
    db_total = db_total // (2**30)
    db_used = db_used // (2**30)
    db_free = db_free // (2**30)
    db_path = DB_PRODUCTION.parent.resolve()

    if Path(cfg.filesystem.db_backup.path).exists():
        backup_total, backup_used, backup_free = shutil.disk_usage(cfg.filesystem.db_backup.path)
        backup_total = backup_total // (2**30)
        backup_used = backup_used // (2**30)
        backup_free = backup_free // (2**30)
        backup_path = Path(cfg.filesystem.db_backup.path).resolve()
    else:
        backup_total = 0
        backup_used = 0
        backup_free = 0
        backup_path = None

    log.info(f"Free disc space at {str(db_path)!r}: {db_free}GiB.")
    log.info(f"Free disc space at {str(backup_path)!r}: {backup_free}GiB.")

    return DiscSpace(
        db_total=db_total,
        db_used=db_used,
        db_free=db_free,
        db_path=db_path,
        backup_total=backup_total,
        backup_used=backup_used,
        backup_free=backup_free,
        backup_path=backup_path,
    )
