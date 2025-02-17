"""
    Handles files schedules.
"""

from copy import deepcopy
from datetime import date
from datetime import datetime

from config import cfg
from const import SYSTEM_USER
from crud.api_key import crud_api_key
from crud.bought_item import crud_bought_item
from crud.user import crud_user
from crud.user_time import crud_user_time
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
        self.add(
            function=self._delete_api_keys,
            hour=cfg.schedules.database_hour,
        )
        self.add(function=self._user_time_past_midnight, hour=0, minute=1)

        if cfg.debug:
            self._set_status_late()
            self._delete_api_keys()

    def _set_status_late(self) -> None:
        log.info("Running database schedule: Automatically setting status of late items")
        system_user = crud_user.get_by_username(db=self.db, username=SYSTEM_USER)
        count, bought_items = crud_bought_item.get_multi(
            db=self.db,
            status=cfg.items.bought.status.ordered,
            expected_to=date.today(),
        )
        for bought_item in bought_items:
            crud_bought_item.update_status(
                db=self.db,
                db_obj_user=system_user,  # type: ignore
                db_obj_item=bought_item,
                status=cfg.items.bought.status.late,
            )

    def _delete_api_keys(self) -> None:
        log.info("Running database schedule: Deleting API keys")
        deleted_api_keys = crud_api_key.get_deleted_multi(db=self.db)
        for key in deleted_api_keys:
            crud_api_key.delete(db=self.db, id=key.id, forever=True)
            log.info(f"Deleted API key #{key.id} ({key.name})")

    def _user_time_past_midnight(self) -> None:
        items = crud_user_time.get_logged_in(db=self.db)
        for user, entry in items:
            login_timestamp = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
            logout_timestamp = deepcopy(entry.login).replace(hour=23, minute=59, second=59, microsecond=0)
            crud_user_time.logout(db=self.db, db_obj_user=user, timestamp=logout_timestamp)
            if not user.auto_logout:
                crud_user_time.login(db=self.db, db_obj_user=user, timestamp=login_timestamp)
