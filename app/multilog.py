"""
    Logging module that connects to the glados logger.
"""

import logging
import logging.handlers
import os
from pathlib import Path

import coloredlogs
from config import cfg
from const import LOGS, NAME


class Log:
    """Main class for logging."""

    def __init__(self) -> None:
        """Inits the logger named glados."""

        self.logger = logging.getLogger(NAME)
        self.format = logging.Formatter(
            "%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s"
        )
        if cfg.debug:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)

        self.stream_handler: logging.StreamHandler = None  # type: ignore
        self.file_handler: logging.handlers.RotatingFileHandler = None  # type:ignore
        coloredlogs.install(level=logging.DEBUG if cfg.debug else logging.INFO)

    def add_stream_handler(self):
        """Adds a stream handler for stdout."""
        self.stream_handler = logging.StreamHandler()
        self.stream_handler.setLevel(self.logger.level)
        self.stream_handler.setFormatter(self.format)
        self.logger.addHandler(self.stream_handler)

    def add_file_handler(
        self,
        backup_count: int = 10,
    ):
        """
        Adds a rotating file handler.

        Args:
            backup_count (int, optional): The amount of backups. Each new file handler \
                will create a backup of an existing log file. Defaults to 10.
        """

        os.makedirs(LOGS, exist_ok=True)

        filename = f"{NAME}.debug.log" if cfg.debug else f"{NAME}.log"
        logfile_path = Path(LOGS, filename)

        self.file_handler = logging.handlers.RotatingFileHandler(
            logfile_path, mode="w", backupCount=backup_count, delay=True
        )
        self.file_handler.setLevel(self.logger.level)
        self.file_handler.setFormatter(self.format)
        self.logger.addHandler(self.file_handler)
        if os.path.isfile(logfile_path):
            self.file_handler.doRollover()

    def _set_level_debug(self) -> None:
        """Sets the log-level to DEBUG."""
        self.logger.setLevel(logging.DEBUG)
        if self.stream_handler:
            self.stream_handler.setLevel(logging.DEBUG)
        if self.file_handler:
            self.file_handler.setLevel(logging.DEBUG)

    def _set_level_info(self) -> None:
        """Sets the log-level to INFO."""
        self.logger.setLevel(logging.INFO)
        if self.stream_handler:
            self.stream_handler.setLevel(logging.INFO)
        if self.file_handler:
            self.file_handler.setLevel(logging.INFO)

    def debug(self, message: str) -> None:
        """Logs a debug message."""
        self.logger.debug(msg=message)

    def info(self, message: str) -> None:
        """Logs an info message."""
        self.logger.info(msg=message)

    def warning(self, message: str) -> None:
        """Logs a warning message."""
        self.logger.warning(msg=message)

    def error(self, message: str) -> None:
        """Logs an error message."""
        self.logger.error(msg=message, exc_info=False)

    def exception(self, message: str) -> None:
        """Logs an error message from an exception."""
        self.logger.exception(msg=message)


log = Log()
