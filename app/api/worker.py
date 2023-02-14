"""
    API worker.
"""

import os
from pathlib import Path
from typing import Optional

from const import LOGS
from multilog import log


def gather_logs() -> list:
    """Returns a list of all log files from the log-folder."""
    return os.listdir(LOGS)


def read_logfile(filename: str) -> Optional[list]:
    """
    Returns the content of a given logfile inside the logs-folder.
    Returns None is the file does not exists.
    """
    path = Path(LOGS, filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as log_file:
            value = [line.strip() for line in log_file]
        return value
    log.warning(f"Could not fetch log file {filename!r}: File does not exist.")
    return None
