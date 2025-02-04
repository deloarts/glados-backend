"""
    CRUD tests (CREATE ONLY) for the user model
"""

import pytest
from api.schemas.user import UserCreateSchema
from const import SERVER_DEFAULT_LANGUAGE
from const import SERVER_DEFAULT_THEME
from crud.user import crud_user
from exceptions import EmailAlreadyExistsError
from exceptions import RfidAlreadyExistsError
from exceptions import UserError
from exceptions import UsernameAlreadyExistsError
from sqlalchemy.orm import Session

from tests.utils.user import current_user_adminuser
from tests.utils.user import get_test_user
from tests.utils.utils import random_email
from tests.utils.utils import random_lower_string
from tests.utils.utils import random_name
from tests.utils.utils import random_username


def test_create_user(db: Session) -> None:
    """
    Test the creation of a new user in the database.

    This test performs the following steps:
    1. Generates random username, full name, email, and password.
    2. Ensures the generated username and email do not already exist in the database.
    3. Creates a UserCreateSchema object with the generated data.
    4. Calls the CRUD method to create the user in the database.

    Args:
        db (Session): The database session used for the test.

    Asserts:
        The user is successfully created in the database.
    """

    # ----------------------------------------------
    # CREATE USER: PREPARATION
    # ----------------------------------------------

    t_username = random_username()
    t_full_name = random_name()
    t_email = random_email()
    t_password = random_lower_string()

    # Ensure that the generated username and mail does not exist
    # Both are unique in the db
    while crud_user.get_by_username(db, username=t_username) or crud_user.get_by_email(db, email=t_email):
        t_username = random_username()
        t_email = random_email()

    t_user_in = UserCreateSchema(
        username=t_username,
        full_name=t_full_name,
        email=t_email,
        password=t_password,
        rfid=None,
    )

    # ----------------------------------------------
    # CREATE USER: METHODS TO TEST
    # ----------------------------------------------

    user = crud_user.create(db, obj_in=t_user_in, current_user=current_user_adminuser())

    # ----------------------------------------------
    # CREATE USER: VALIDATION
    # ----------------------------------------------

    # Given properties
    assert user.username == t_username
    assert user.email == t_email
    assert user.full_name == t_full_name

    # Auto-generated properties
    assert user.language == SERVER_DEFAULT_LANGUAGE
    assert user.theme == SERVER_DEFAULT_THEME
    assert user.is_active is True
    assert user.is_superuser is False
    assert user.is_adminuser is False
    assert user.is_systemuser is False

    assert hasattr(user, "id")
    assert hasattr(user, "created")
    assert hasattr(user, "personal_access_token")
    assert hasattr(user, "hashed_password")
    assert hasattr(user, "hashed_rfid")

    assert hasattr(user, "projects")
    assert hasattr(user, "created_bought_items")
    assert hasattr(user, "requested_bought_items")
    assert hasattr(user, "ordered_bought_items")
    assert hasattr(user, "received_items")


def test_create_existing_user_username(db: Session) -> None:
    """
    Test case for creating a user with an existing username.
    This test ensures that attempting to create a user with a username that already exists in the database
    raises the appropriate exceptions.

    Steps:
    1. Retrieve an existing user's username from the database.
    2. Generate a new full name, email, and password for the new user.
    3. Ensure the generated email does not already exist in the database.
    4. Create a UserCreateSchema object with the existing username and new user details.
    5. Attempt to create the user and verify that a UserError is raised.
    6. Attempt to create the user again and verify that a UsernameAlreadyExistsError is raised.

    Args:
        db (Session): The database session used for the test.

    Raises:
        UserError: If a user with the existing username is attempted to be created.
        UsernameAlreadyExistsError: If a user with the existing username is attempted to be created.
    """

    # ----------------------------------------------
    # CREATE EXISTING USER (USERNAME): PREPARATION
    # ----------------------------------------------

    t_username = get_test_user(db).username

    t_full_name = random_name()
    t_email = random_email()
    t_password = random_lower_string()

    # Ensure that the generated mail does not exist (not part of this test case)
    while crud_user.get_by_email(db, email=t_email):
        t_email = random_email()

    t_user_in = UserCreateSchema(
        username=t_username,
        full_name=t_full_name,
        email=t_email,
        password=t_password,
        rfid=None,
    )

    # ----------------------------------------------
    # CREATE EXISTING USER (USERNAME): METHODS TO TEST
    # ----------------------------------------------

    with pytest.raises(UserError):
        crud_user.create(db, obj_in=t_user_in, current_user=current_user_adminuser())

    with pytest.raises(UsernameAlreadyExistsError):  # Descendent-Error of UserError
        crud_user.create(db, obj_in=t_user_in, current_user=current_user_adminuser())


def test_create_existing_user_mail(db: Session) -> None:
    """
    Test case for creating a user with an existing email.
    This test ensures that attempting to create a user with an email that already
    exists in the database raises the appropriate exceptions.

    Steps:
    1. Retrieve an existing user's email from the database.
    2. Generate a random username, full name, and password.
    3. Ensure the generated username does not already exist in the database.
    4. Create a UserCreateSchema object with the existing email and generated details.
    5. Attempt to create a user with the existing email and verify that a UserError is raised.
    6. Attempt to create a user with the existing email and verify that an EmailAlreadyExistsError is raised.

    Args:
        db (Session): The database session used for the test.

    Raises:
        UserError: If a user with the existing email is attempted to be created.
        EmailAlreadyExistsError: If a user with the existing email is attempted to be created.
    """

    # ----------------------------------------------
    # CREATE EXISTING USER (MAIL): PREPARATION
    # ----------------------------------------------

    t_email = get_test_user(db).email

    t_username = random_username()
    t_full_name = random_name()
    t_password = random_lower_string()

    # Ensure that the generated username does not exist (not part of this test case)
    while crud_user.get_by_username(db, username=t_username):
        t_email = random_email()

    t_user_in = UserCreateSchema(
        username=t_username,
        full_name=t_full_name,
        email=t_email,
        password=t_password,
        rfid=None,
    )

    # ----------------------------------------------
    # CREATE EXISTING USER (MAIL): METHODS TO TEST
    # ----------------------------------------------

    with pytest.raises(UserError):
        crud_user.create(db, obj_in=t_user_in, current_user=current_user_adminuser())

    with pytest.raises(EmailAlreadyExistsError):  # Descendent-Error of UserError
        crud_user.create(db, obj_in=t_user_in, current_user=current_user_adminuser())


def test_create_existing_user_rfid(db: Session) -> None:
    """
    Test the creation of a user with an existing RFID.
    This test ensures that the system correctly handles the creation of a user
    with an RFID that is already associated with another user.

    It performs the following steps:
    1. Generate a unique RFID and ensure it does not already exist in the database.
    2. Generate unique usernames and emails for two users.
    3. Create the first user with the generated RFID.
    4. Attempt to create a second user with the same RFID and verify that the
       appropriate exceptions are raised.

    Args:
        db (Session): The database session used for the test.

    Raises:
        UserError: If a user with the same RFID already exists.
        RfidAlreadyExistsError: If a user with the same RFID already exists (specific error).
    """

    # ----------------------------------------------
    # CREATE EXISTING USER (RFID): PREPARATION
    # ----------------------------------------------

    t_rfid = random_lower_string()
    while crud_user.get_by_rfid(db, rfid=t_rfid):
        t_rfid = random_lower_string()

    t_username_1 = random_username()
    t_full_name_1 = random_name()
    t_email_1 = random_email()
    t_password_1 = random_lower_string()

    t_username_2 = random_username()
    t_full_name_2 = random_name()
    t_email_2 = random_email()
    t_password_2 = random_lower_string()

    # Ensure that the generated username and mail does not exist
    while crud_user.get_by_username(db, username=t_username_1) or crud_user.get_by_email(db, email=t_email_1):
        t_username_1 = random_username()
        t_email_1 = random_email()

    # Ensure that the generated username and mail does not exist and are not those from user 1
    while (
        crud_user.get_by_username(db, username=t_username_2)
        or crud_user.get_by_email(db, email=t_email_2)
        or t_username_2 == t_username_1
        or t_email_2 == t_email_1
    ):
        t_username_2 = random_username()
        t_email_2 = random_email()

    t_user_in_1 = UserCreateSchema(
        username=t_username_1,
        full_name=t_full_name_1,
        email=t_email_1,
        password=t_password_1,
        rfid=t_rfid,
    )
    t_user_in_2 = UserCreateSchema(
        username=t_username_2,
        full_name=t_full_name_2,
        email=t_email_2,
        password=t_password_2,
        rfid=t_rfid,
    )
    crud_user.create(db, obj_in=t_user_in_1, current_user=current_user_adminuser())

    # ----------------------------------------------
    # CREATE EXISTING USER (RFID): METHODS TO TEST
    # ----------------------------------------------

    with pytest.raises(UserError):
        crud_user.create(db, obj_in=t_user_in_2, current_user=current_user_adminuser())

    with pytest.raises(RfidAlreadyExistsError):  # Descendent-Error of UserError
        crud_user.create(db, obj_in=t_user_in_2, current_user=current_user_adminuser())
