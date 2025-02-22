"""
    CRUD tests (CREATE ONLY) for the user time model
"""

from datetime import datetime
from datetime import timedelta

import pytest
from api.schemas.user_time import UserTimeCreateSchema
from crud.user_time import crud_user_time
from exceptions import LoginNotTodayError
from exceptions import LogoutBeforeLoginError
from sqlalchemy.orm import Session

from tests.utils.user import create_random_user


def test_create_user_time(db: Session) -> None:
    """
    Test the creation of a user time entry in the database.
    This test performs the following steps:

    1. Preparation: Creates a random user and sets login, logout times, and a note.
    2. Methods to Test: Calls the `create` method from `crud_user_time` to create a user time entry.
    3. Validation: Asserts that the created entry has the correct user ID, login time, logout time, note,
       and calculates the duration in minutes correctly.

    Args:
        db (Session): The database session used for the test.

    Asserts:
        entry.user_id == t_user.id
        entry.login == t_login
        entry.logout == t_logout
        entry.note == t_note
        entry.duration_minutes == (t_logout - t_login).total_seconds() / 60
    """

    # ----------------------------------------------
    # CREATE USER TIME: PREPARATION
    # ----------------------------------------------

    t_user = create_random_user(db)
    t_login = datetime.now() - timedelta(hours=8)
    t_logout = datetime.now()
    t_note = "Test Note"

    t_obj_in = UserTimeCreateSchema(login=t_login, logout=t_logout, note=t_note)

    # ----------------------------------------------
    # CREATE USER TIME: METHODS TO TEST
    # ----------------------------------------------

    entry = crud_user_time.create(db, db_obj_user=t_user, obj_in=t_obj_in)

    # ----------------------------------------------
    # CREATE USER TIME: VALIDATION
    # ----------------------------------------------

    assert entry.user_id == t_user.id
    assert entry.login == t_login
    assert entry.logout == t_logout
    assert entry.note == t_note
    assert entry.duration_minutes == (t_logout - t_login).total_seconds() / 60


def test_create_user_time__login_after_logout(db: Session) -> None:
    """
    Test case for creating a user time entry where the login time is after the logout time.

    This test ensures that the system raises a LogoutBeforeLoginError when attempting to create
    a user time entry with a login time that occurs after the logout time.

    Steps:
    1. Create a random user.
    2. Set the login time to the current time.
    3. Set the logout time to 8 hours before the current time.
    4. Create a UserTimeCreateSchema object with the login, logout, and a test note.
    5. Attempt to create the user time entry using the CRUD method.
    6. Verify that a LogoutBeforeLoginError is raised.

    Args:
        db (Session): The database session used for the test.

    Raises:
        LogoutBeforeLoginError: If the logout time is before the login time.
    """

    # ----------------------------------------------
    # CREATE USER TIME: PREPARATION
    # ----------------------------------------------

    t_user = create_random_user(db)
    t_login = datetime.now()
    t_logout = datetime.now() - timedelta(hours=8)
    t_note = "Test Note"

    t_obj_in = UserTimeCreateSchema(login=t_login, logout=t_logout, note=t_note)

    # ----------------------------------------------
    # CREATE USER TIME: METHODS TO TEST
    # ----------------------------------------------

    with pytest.raises(LogoutBeforeLoginError):
        crud_user_time.create(db, db_obj_user=t_user, obj_in=t_obj_in)


def test_create_user_time__login_not_today(db: Session) -> None:
    """
    Test case for creating a user time entry where the login time is not today.

    This test verifies that the `create` method of the `crud_user_time` module
    raises a `LoginNotTodayError` when attempting to create a user time entry
    with a login time that is not within the current day.

    Args:
        db (Session): The database session used for the test.

    Steps:
        1. Create a random user.
        2. Set the login time to 25 hours ago (not today).
        3. Create a `UserTimeCreateSchema` object with the login time.
        4. Attempt to create the user time entry using the `crud_user_time.create` method.
        5. Verify that a `LoginNotTodayError` is raised.

    Raises:
        LoginNotTodayError: If the login time is not within the current day.
    """

    # ----------------------------------------------
    # CREATE USER TIME: PREPARATION
    # ----------------------------------------------

    t_user = create_random_user(db)
    t_login = datetime.now() - timedelta(hours=25)

    t_obj_in = UserTimeCreateSchema(login=t_login, logout=None, note=None)

    # ----------------------------------------------
    # CREATE USER TIME: METHODS TO TEST
    # ----------------------------------------------

    with pytest.raises(LoginNotTodayError):
        crud_user_time.create(db, db_obj_user=t_user, obj_in=t_obj_in)
