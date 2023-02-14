"""
    Handles files schedules.
"""

from datetime import date

from config import cfg
from const import SYSTEM_USER
from crud import crud_bought_item, crud_user
from multilog import log
from schedules.base_schedules import BaseSchedules


class DatabaseSchedules(BaseSchedules):
    """Class for schedules."""

    def __init__(self) -> None:
        """Initializes the database schedules."""
        super().__init__()

        self.add(
            function=self._set_status_late,
            hour=cfg.schedules.database_hour,
        )

        if cfg.debug:
            self._set_status_late()

    def _set_status_late(self) -> None:
        log.info("Running automatic status schedule.")

        system_user = crud_user.user.get_by_username(db=self.db, username=SYSTEM_USER)
        bought_items = crud_bought_item.bought_item.get_multi(
            db=self.db,
            status=cfg.items.bought.status.ordered,
            expected_to=date.today(),
        )
        for bought_item in bought_items:
            crud_bought_item.bought_item.update_status(
                db=self.db,
                db_obj_user=system_user,  # type: ignore
                db_obj_item=bought_item,
                status=cfg.items.bought.status.late,
            )
