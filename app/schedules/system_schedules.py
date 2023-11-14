"""
    Handles files schedules.
"""
from config import cfg
from mail.presets import MailPreset
from multilog import log
from schedules.base_schedules import BaseSchedules
from utilities.disc_space import get_disc_space


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
        log.info("Running system schedule: Retrieving disc space.")
        # TODO: Reactor this method

        ds = get_disc_space()

        if ds.db_free < cfg.filesystem.disc_space_warning or ds.backup_free < cfg.filesystem.disc_space_warning:
            log.warning(f"Disc space is running low (<{cfg.filesystem.disc_space_warning}GiB).")
            MailPreset.send_disc_space_warning(
                ds.db_total,
                ds.db_used,
                ds.db_free,
                str(ds.db_path),
                ds.backup_total,
                ds.backup_used,
                ds.backup_free,
                str(ds.backup_path),
            )
