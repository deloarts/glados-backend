#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
GLADOS Backend
"""

import server
from db import session
from multilog import log
from schedules.database_schedules import DatabaseSchedules
from schedules.file_schedules import FileSchedules
from schedules.notification_schedules import NotificationSchedules
from schedules.system_schedules import SystemSchedules


def main() -> None:
    # log.add_stream_handler()
    log.add_file_handler()
    log.info("Application started.")

    system_schedule = SystemSchedules()
    system_schedule.start()

    file_schedule = FileSchedules()
    file_schedule.start()

    notification_schedule = NotificationSchedules()
    notification_schedule.start()

    database_schedules = DatabaseSchedules()
    database_schedules.start()

    session.InitDatabase()
    server.run()


if __name__ == "__main__":
    main()
