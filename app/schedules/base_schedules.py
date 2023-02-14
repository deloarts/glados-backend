"""
    Handles files schedules.
"""

import atexit
from typing import Callable

from apscheduler.schedulers.background import BackgroundScheduler
from config import cfg
from db.session import SessionLocal
from multilog import log
from sqlalchemy.orm import Session


class BaseSchedules:
    """Base class for schedules."""

    def __init__(self) -> None:
        """Initializes the schedules."""
        self._schedule = BackgroundScheduler()
        self._schedule.configure(timezone=cfg.locale.tz)
        self._schedule_db_session = SessionLocal()

        atexit.register(lambda: self.stop())

    def add(self, function: Callable, hour: int) -> None:
        """Adds a job to the schedule."""
        log.info(f"Added function {function.__qualname__!r} to scheduled.")
        self._schedule.add_job(function, "cron", hour=str(hour))

    def start(self) -> None:
        """Starts all jobs of the schedule."""
        self._schedule.start()

    def stop(self) -> None:
        """Stops the schedule."""
        self._schedule.shutdown()

    @property
    def db(self) -> Session:
        return self._schedule_db_session
