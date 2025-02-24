"""
    CRUD tests (COMMON METHODS ONLY) for the user model
"""

from api.schemas.user import UserCreateSchema
from crud.user import crud_user
from sqlalchemy.orm import Session

from tests.utils.user import TEST_PASSWORD
from tests.utils.user import current_user_adminuser
from tests.utils.user import get_test_admin_user
from tests.utils.user import get_test_super_user
from tests.utils.user import get_test_user
from tests.utils.utils import random_email
from tests.utils.utils import random_lower_string
from tests.utils.utils import random_name
from tests.utils.utils import random_username


def test_authenticate_user(db: Session) -> None:
    """
    Test the authentication of different types of users.
    This test performs the following steps:

    1. Preparation:
        - Retrieves a test user, super user, and admin user from the database.
        - Updates their passwords to a known test password.
    2. Methods to Test:
        - Authenticates the test user, super user, and admin user with the known test password.
        - Attempts to authenticate the test user with an incorrect password.
    3. Validation:
        - Asserts that the test user, super user, and admin user are successfully authenticated.
        - Asserts that the test user is not authenticated with the incorrect password.

    Args:
        db (Session): The database session used for the test.
    """

    # ----------------------------------------------
    # AUTH USER: PREPARATION
    # ----------------------------------------------

    t_user = get_test_user(db)
    t_super = get_test_super_user(db)
    t_admin = get_test_admin_user(db)

    # Some tests update the password, make sure to authenticate the user to their current pw
    crud_user.update(db, current_user=t_admin, db_obj=t_user, obj_in={"password": TEST_PASSWORD})
    crud_user.update(db, current_user=t_admin, db_obj=t_super, obj_in={"password": TEST_PASSWORD})
    crud_user.update(db, current_user=t_admin, db_obj=t_admin, obj_in={"password": TEST_PASSWORD})

    # ----------------------------------------------
    # AUTH USER: METHODS TO TEST
    # ----------------------------------------------

    authenticated_user = crud_user.authenticate(db, username=t_user.username, password=TEST_PASSWORD)
    authenticated_super_user = crud_user.authenticate(db, username=t_super.username, password=TEST_PASSWORD)
    authenticated_admin_user = crud_user.authenticate(db, username=t_admin.username, password=TEST_PASSWORD)
    unauthenticated_user = crud_user.authenticate(db, username=t_user.username, password="definitely not the password")

    # ----------------------------------------------
    # AUTH USER: VALIDATION
    # ----------------------------------------------

    assert authenticated_user
    assert authenticated_super_user
    assert authenticated_admin_user
    assert not unauthenticated_user


def test_check_if_user_is_active(db: Session) -> None:
    """
    Test the functionality of checking if a user is active.
    This test performs the following steps:

    1. Generates a random username, full name, email, and password.
    2. Ensures that the generated username and email do not already exist in the database.
    3. Creates a new user with the generated credentials.
    4. Checks if the newly created user is active using the `crud_user.is_active` method.
    5. Asserts that the user is active.

    Args:
        db (Session): The database session used for the test.
    """

    # ----------------------------------------------
    # ACTIVE USER: PREPARATION
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
    t_user = crud_user.create(db, obj_in=t_user_in, current_user=current_user_adminuser())

    # ----------------------------------------------
    # ACTIVE USER: METHODS TO TEST
    # ----------------------------------------------

    is_active = crud_user.is_active(t_user)

    # ----------------------------------------------
    # ACTIVE USER: VALIDATION
    # ----------------------------------------------

    assert is_active is True


def test_check_if_user_is_inactive(db: Session) -> None:
    """
    Test the functionality to check if a user is inactive.
    This test performs the following steps:

    1. Generates a random username, full name, email, and password.
    2. Ensures the generated username and email do not already exist in the database.
    3. Creates a new user with the generated credentials and sets the user as inactive.
    4. Checks if the created user is inactive using the `crud_user.is_active` method.
    5. Asserts that the user is indeed inactive.

    Args:
        db (Session): The database session used for the test.
    """

    # ----------------------------------------------
    # INACTIVE USER: PREPARATION
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
        is_active=False,
    )
    t_user = crud_user.create(db, obj_in=t_user_in, current_user=current_user_adminuser())

    # ----------------------------------------------
    # INACTIVE USER: METHODS TO TEST
    # ----------------------------------------------

    is_active = crud_user.is_active(t_user)

    # ----------------------------------------------
    # INACTIVE USER: VALIDATION
    # ----------------------------------------------

    assert is_active is False


def test_check_if_user_is_superuser(db: Session) -> None:
    """
    Test the functionality to check if a user is a superuser.
    This test performs the following steps:

    1. Generates a random username, full name, email, and password.
    2. Ensures the generated username and email do not already exist in the database.
    3. Creates a new user with the generated credentials and sets the user as a superuser.
    4. Tests the following methods from the CRUD user module:
        - `is_active`: Checks if the user is active.
        - `is_superuser`: Checks if the user is a superuser.
        - `is_adminuser`: Checks if the user is an admin user.
    5. Validates the results of the methods:
        - Asserts that the user is active.
        - Asserts that the user is a superuser.
        - Asserts that the user is not an admin user.

    Args:
        db (Session): The database session used for the test.

    Returns:
        None
    """

    # ----------------------------------------------
    # SUPER USER: PREPARATION
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
        is_superuser=True,
    )
    t_user = crud_user.create(db, obj_in=t_user_in, current_user=current_user_adminuser())

    # ----------------------------------------------
    # SUPER USER: METHODS TO TEST
    # ----------------------------------------------

    is_active = crud_user.is_active(t_user)
    is_superuser = crud_user.is_superuser(t_user)
    is_adminuser = crud_user.is_adminuser(t_user)

    # ----------------------------------------------
    # SUPER USER: VALIDATION
    # ----------------------------------------------

    assert is_active is True
    assert is_superuser is True
    assert is_adminuser is False


def test_check_if_user_is_adminuser(db: Session) -> None:
    """
    Test the functionality to check if a user is an admin user.
    This test performs the following steps:

    1. Generates a random username, full name, email, and password.
    2. Ensures that the generated username and email do not already exist in the database.
    3. Creates a new user with the generated credentials and sets the `is_adminuser` flag to True.
    4. Checks if the created user is active, a superuser, and an admin user.
    5. Validates that the user is active, a superuser, and an admin user.

    Args:
        db (Session): The database session used for the test.

    Asserts:
        The user is active.
        The user is a superuser.
        The user is an admin user.
    """

    # ----------------------------------------------
    # ADMIN USER: PREPARATION
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
        is_superuser=False,  # Even if set to false, when is_adminuser is set True, this will become True
        is_adminuser=True,
    )
    t_user = crud_user.create(db, obj_in=t_user_in, current_user=current_user_adminuser())

    # ----------------------------------------------
    # ADMIN USER: METHODS TO TEST
    # ----------------------------------------------

    is_active = crud_user.is_active(t_user)
    is_superuser = crud_user.is_superuser(t_user)
    is_adminuser = crud_user.is_adminuser(t_user)

    # ----------------------------------------------
    # ADMIN USER: VALIDATION
    # ----------------------------------------------

    assert is_active is True
    assert is_superuser is True
    assert is_adminuser is True


def test_check_if_user_is_guestuser(db: Session) -> None:
    """
    Test the functionality to check if a user is a guest user.
    This test performs the following steps:
    1. Generates a random username, full name, email, and password.
    2. Ensures the generated username and email do not already exist in the database.
    3. Creates a new user with the generated credentials and marks the user as a guest user.
    4. Tests various user status methods to verify the user's attributes:
        - Checks if the user is active.
        - Checks if the user is a superuser.
        - Checks if the user is an admin user.
        - Checks if the user is a guest user.
    5. Validates the expected outcomes:
        - The user should be active.
        - The user should not be a superuser.
        - The user should not be an admin user.
        - The user should be a guest user.
    Args:
        db (Session): The database session used for the test.
    """

    # ----------------------------------------------
    # GUEST USER: PREPARATION
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
        is_guestuser=True,
    )
    t_user = crud_user.create(db, obj_in=t_user_in, current_user=current_user_adminuser())

    # ----------------------------------------------
    # GUEST USER: METHODS TO TEST
    # ----------------------------------------------

    is_active = crud_user.is_active(t_user)
    is_superuser = crud_user.is_superuser(t_user)
    is_adminuser = crud_user.is_adminuser(t_user)
    is_guest = crud_user.is_guestuser(t_user)

    # ----------------------------------------------
    # GUEST USER: VALIDATION
    # ----------------------------------------------

    assert is_active is True
    assert is_superuser is False
    assert is_adminuser is False
    assert is_guest is True
