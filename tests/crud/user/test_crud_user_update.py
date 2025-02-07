"""
    CRUD tests (UPDATE ONLY) for the user model
"""

import pytest
from api.schemas.user import UserCreateSchema
from api.schemas.user import UserUpdateSchema
from crud.user import crud_user
from exceptions import EmailAlreadyExistsError
from exceptions import InsufficientPermissionsError
from exceptions import PasswordCriteriaError
from exceptions import RfidAlreadyExistsError
from exceptions import UserError
from exceptions import UsernameAlreadyExistsError
from security.pwd import verify_hash
from sqlalchemy.orm import Session

from tests.utils.user import TEST_PASS
from tests.utils.user import current_user_adminuser
from tests.utils.user import get_test_admin_user
from tests.utils.user import get_test_guest_user
from tests.utils.user import get_test_super_user
from tests.utils.user import get_test_user
from tests.utils.utils import random_email
from tests.utils.utils import random_lower_string
from tests.utils.utils import random_name
from tests.utils.utils import random_username


def test_update_user(db: Session) -> None:
    """
    Test the update functionality of the user CRUD operations.
    This test performs the following steps:

    1. Generates random user data for a new user and ensures the generated username and email do not already exist in the database.
    2. Creates a new user with the generated data.
    3. Generates new random data for updating the user and ensures the new username and email do not conflict with existing ones.
    4. Updates the created user with the new data.
    5. Validates that the user has been updated correctly by checking the updated fields.

    Args:
        db (Session): The database session used for the test.

    Asserts:
        - The user exists after creation.
        - The user's ID remains the same after the update.
        - The user's username, email, full name, password, language, and theme are updated correctly.
    """

    # ----------------------------------------------
    # UPDATE USER: PREPARATION
    # ----------------------------------------------

    t_username = random_username()
    t_full_name = random_name()
    t_email = random_email()
    t_password = random_lower_string()

    t_new_username = random_username()
    t_new_full_name = random_name()
    t_new_email = random_email()
    t_new_password = random_lower_string()

    # Ensure that the generated username and mail does not exist
    # Both are unique in the db
    while crud_user.get_by_username(db, username=t_username) or crud_user.get_by_email(db, email=t_email):
        t_username = random_username()
        t_email = random_email()

    while (
        crud_user.get_by_username(db, username=t_new_username)
        or crud_user.get_by_email(db, email=t_new_email)
        or t_new_username == t_username
        or t_new_email == t_email
    ):
        t_new_username = random_username()
        t_new_email = random_email()

    t_user_in = UserCreateSchema(
        username=t_username,
        full_name=t_full_name,
        email=t_email,
        password=t_password,
        rfid=None,
        is_guestuser=True,
    )
    t_user = crud_user.create(db, obj_in=t_user_in, current_user=current_user_adminuser())

    t_user_in_update = UserUpdateSchema(
        username=t_new_username,
        full_name=t_new_full_name,
        email=t_new_email,
        password=t_new_password,
        language="deAT",
        theme="dark",
        rfid=None,
    )

    # ----------------------------------------------
    # UPDATE USER: METHODS TO TEST
    # ----------------------------------------------

    crud_user.update(db, db_obj=t_user, obj_in=t_user_in_update, current_user=current_user_adminuser())

    # ----------------------------------------------
    # UPDATE USER: VALIDATION
    # ----------------------------------------------

    user_2 = crud_user.get(db, id=t_user.id)
    assert user_2
    assert user_2.id == t_user.id
    assert user_2.username == t_new_username
    assert user_2.email == t_new_email
    assert user_2.full_name == t_new_full_name
    assert verify_hash(t_new_password, user_2.hashed_password)
    assert user_2.language == "deAT"
    assert user_2.theme == "dark"


def test_update_user_existing_username(db: Session) -> None:
    """
    Test updating a user with an existing username.
    This test ensures that attempting to update a user's username to one that already exists in the database
    raises the appropriate exceptions and does not change the original user's username.

    Preparation:
        - Retrieve a normal user and an admin user from the test database.
        - Create a UserUpdateSchema object with the admin user's username and the normal user's other details.
    Methods to Test:
        - Attempt to update the normal user's username to the admin user's username.
        - Verify that a UserError is raised.
        - Verify that a UsernameAlreadyExistsError, which is a descendant of UserError, is raised.
    Validation:
        - Retrieve the normal user from the database.
        - Assert that the user exists.
        - Assert that the user's username has not changed.

    Args:
        db (Session): The database session used for the test.
    """

    # ----------------------------------------------
    # UPDATE USER (EXISTENT USERNAME): PREPARATION
    # ----------------------------------------------

    normal_user = get_test_user(db)
    admin_user = get_test_admin_user(db)

    t_user_in_update = UserUpdateSchema(
        username=admin_user.username,
        full_name=normal_user.full_name,
        email=normal_user.email,
        password="12345678",
        language="deAT",
        theme="dark",
        rfid=None,
    )

    # ----------------------------------------------
    # UPDATE USER (EXISTENT USERNAME): METHODS TO TEST
    # ----------------------------------------------

    with pytest.raises(UserError):
        crud_user.update(db, db_obj=normal_user, obj_in=t_user_in_update, current_user=current_user_adminuser())

    with pytest.raises(UsernameAlreadyExistsError):  # Descendent-Error of UserError
        crud_user.update(db, db_obj=normal_user, obj_in=t_user_in_update, current_user=current_user_adminuser())

    # ----------------------------------------------
    # UPDATE USER (EXISTENT USERNAME): VALIDATION
    # ----------------------------------------------

    user = crud_user.get(db, id=normal_user.id)
    assert user
    assert user.username == normal_user.username


def test_update_user_existing_mail(db: Session) -> None:
    """
    Test updating a user with an email that already exists in the database.
    This test performs the following steps:

    1. Preparation:
       - Retrieve a normal user and an admin user from the database.
       - Create a UserUpdateSchema object with the normal user's username and full name,
         but with the admin user's email, along with other attributes.
    2. Methods to Test:
       - Attempt to update the normal user's email to the admin user's email.
       - Expect a UserError to be raised.
       - Attempt the update again and expect an EmailAlreadyExistsError, which is a
         descendant of UserError, to be raised.
    3. Validation:
       - Retrieve the normal user from the database.
       - Assert that the user exists and that their email has not changed.

    Args:
        db (Session): The database session used for the test.

    Raises:
        UserError: If the update operation fails due to a user-related error.
        EmailAlreadyExistsError: If the update operation fails because the email already exists.
    """

    # ----------------------------------------------
    # UPDATE USER (EXISTENT MAIL): PREPARATION
    # ----------------------------------------------

    normal_user = get_test_user(db)
    admin_user = get_test_admin_user(db)

    t_user_in_update = UserUpdateSchema(
        username=normal_user.username,
        full_name=normal_user.full_name,
        email=admin_user.email,
        password=TEST_PASS,
        language="deAT",
        theme="dark",
        rfid=None,
    )

    # ----------------------------------------------
    # UPDATE USER (EXISTENT MAIL): METHODS TO TEST
    # ----------------------------------------------

    with pytest.raises(UserError):
        crud_user.update(db, db_obj=normal_user, obj_in=t_user_in_update, current_user=current_user_adminuser())

    with pytest.raises(EmailAlreadyExistsError):  # Descendent-Error of UserError
        crud_user.update(db, db_obj=normal_user, obj_in=t_user_in_update, current_user=current_user_adminuser())

    # ----------------------------------------------
    # UPDATE USER (EXISTENT MAIL): VALIDATION
    # ----------------------------------------------

    user = crud_user.get(db, id=normal_user.id)
    assert user
    assert user.email == normal_user.email


def test_update_user_existing_rfid(db: Session) -> None:
    """
    Test updating a user with an existing RFID.

    This test ensures that attempting to update a user with an RFID that already exists in the database
    raises the appropriate exceptions.

    Steps:
    1. Generate random user details and ensure the username and email are unique in the database.
    2. Create a normal user with the generated details.
    3. Prepare an update schema for an admin user with the same RFID as the normal user.
    4. Attempt to update the admin user with the existing RFID and check for the expected exceptions.

    Assertions:
    - Ensure that a UserError is raised when trying to update the user.
    - Ensure that an RfidAlreadyExistsError (a descendant of UserError) is raised when trying to update the user.
    - Validate that the normal user still exists in the database after the failed update attempts.

    Args:
        db (Session): The database session used for the test.
    """

    # ----------------------------------------------
    # UPDATE USER (EXISTENT RFID): PREPARATION
    # ----------------------------------------------

    t_rfid = random_lower_string()

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
        rfid=t_rfid,
    )
    normal_user = crud_user.create(db, obj_in=t_user_in, current_user=current_user_adminuser())

    admin_user = get_test_admin_user(db)
    t_user_in_update = UserUpdateSchema(
        username=admin_user.username,
        full_name=admin_user.full_name,
        email=admin_user.email,
        password=TEST_PASS,
        language="deAT",
        theme="dark",
        rfid=t_rfid,
    )

    # ----------------------------------------------
    # UPDATE USER (EXISTENT RFID): METHODS TO TEST
    # ----------------------------------------------

    with pytest.raises(UserError):
        crud_user.update(db, db_obj=admin_user, obj_in=t_user_in_update, current_user=current_user_adminuser())

    with pytest.raises(RfidAlreadyExistsError):  # Descendent-Error of UserError
        crud_user.update(db, db_obj=admin_user, obj_in=t_user_in_update, current_user=current_user_adminuser())

    # ----------------------------------------------
    # UPDATE USER (EXISTENT RFID): VALIDATION
    # ----------------------------------------------

    user = crud_user.get(db, id=normal_user.id)
    assert user


def test_update_user_password_criteria(db: Session) -> None:
    """
    Test case for updating a user's password with criteria validation.
    This test ensures that updating a user's password to a value that does not
    meet the required criteria raises a PasswordCriteriaError.

    Steps:
    1. Prepare a test user and a new password that does not meet the criteria.
    2. Attempt to update the user's password using the CRUD operation.
    3. Verify that a PasswordCriteriaError is raised.

    Args:
        db (Session): The database session used for the test.

    Raises:
        PasswordCriteriaError: If the password does not meet the required criteria.
    """

    # ----------------------------------------------
    # UPDATE USER (PASSWORD CRITERIA): PREPARATION
    # ----------------------------------------------

    t_password = "1234567"
    t_normal_user = get_test_user(db)

    t_user_in_update = {
        "username": t_normal_user.username,
        "full_name": t_normal_user.full_name,
        "email": t_normal_user.email,
        "password": t_password,
        "language": "deAT",
        "theme": "dark",
        "rfid": None,
    }

    # ----------------------------------------------
    # UPDATE USER (PASSWORD CRITERIA): METHODS TO TEST
    # ----------------------------------------------

    with pytest.raises(PasswordCriteriaError):
        crud_user.update(db, db_obj=t_normal_user, obj_in=t_user_in_update, current_user=current_user_adminuser())


def test_update_system_user(db: Session) -> None:
    """
    Test the update functionality for a system user.
    This test verifies that attempting to update a system user raises an
    InsufficientPermissionsError when the current user does not have the
    necessary permissions (system user permission).

    Steps:
    1. Retrieve the system user with ID 1 from the database.
    2. Prepare an update schema with new user details.
    3. Attempt to update the system user using the prepared schema.
    4. Assert that an InsufficientPermissionsError is raised.

    Args:
        db (Session): The database session used for the test.
    """

    # ----------------------------------------------
    # UPDATE SYSTEM USER: PREPARATION
    # ----------------------------------------------

    system_user = crud_user.get(db, id=1)
    assert system_user

    t_user_in_update = UserUpdateSchema(
        username=system_user.username,
        full_name=system_user.full_name,
        email=system_user.email,
        password=TEST_PASS,
        language="deAT",
        theme="dark",
        rfid=None,
    )

    # ----------------------------------------------
    # UPDATE SYSTEM USER: METHODS TO TEST
    # ----------------------------------------------

    with pytest.raises(InsufficientPermissionsError):
        crud_user.update(db, db_obj=system_user, obj_in=t_user_in_update, current_user=current_user_adminuser())


def test_update_user_own_permissions(db: Session) -> None:
    """
    Test the update of a user's own permissions.
    This test performs the following steps:

    1. Preparation: Retrieve a test user from the database and create an update schema with modified attributes.
    2. Methods to Test: Call the `update` method from the `crud_user` module to update the user's information.
    3. Validation: Retrieve the updated user from the database and assert that the changes have been applied correctly.

    Args:
        db (Session): The database session used for the test.

    Asserts:
        - The user exists in the database.
        - The user's ID remains unchanged.
        - The user's `is_active` attribute is set to True.
        - The user's `is_superuser` attribute is set to False.
        - The user's `is_adminuser` attribute is set to False.
        - The user's `is_guestuser` attribute is set to False.
    """

    # ----------------------------------------------
    # UPDATE USER: PREPARATION
    # ----------------------------------------------

    t_user = get_test_user(db)

    t_user_in_update = UserUpdateSchema(
        username=t_user.username,
        full_name=t_user.full_name,
        email=t_user.email,
        password=TEST_PASS,
        language="deAT",
        theme="dark",
        rfid=None,
        is_active=False,
        is_superuser=True,
        is_adminuser=True,
        is_guestuser=True,
    )

    # ----------------------------------------------
    # UPDATE USER: METHODS TO TEST
    # ----------------------------------------------

    crud_user.update(db, db_obj=t_user, obj_in=t_user_in_update, current_user=t_user)

    # ----------------------------------------------
    # UPDATE USER: VALIDATION
    # ----------------------------------------------

    user = crud_user.get(db, id=t_user.id)
    assert user
    assert user.id == t_user.id
    assert user.is_active is True
    assert user.is_superuser is False
    assert user.is_adminuser is False
    assert user.is_guestuser is False


def test_update_super_user_own_permissions(db: Session) -> None:
    """
    Test case for updating a super user's own permissions.

    This test performs the following steps:
    1. Preparation: Retrieves a test super user from the database and creates an update schema with modified attributes.
    2. Methods to Test: Calls the `update` method from the `crud_user` module to update the user's information.
    3. Validation: Retrieves the updated user from the database and asserts that the user's attributes have been correctly updated.

    Args:
        db (Session): The database session used for the test.

    Asserts:
        - The user exists in the database.
        - The user's ID remains unchanged.
        - The user's `is_active` attribute is True.
        - The user's `is_superuser` attribute is True.
        - The user's `is_adminuser` attribute is False.
        - The user's `is_guestuser` attribute is False.
    """

    # ----------------------------------------------
    # UPDATE USER: PREPARATION
    # ----------------------------------------------

    t_user = get_test_super_user(db)

    t_user_in_update = UserUpdateSchema(
        username=t_user.username,
        full_name=t_user.full_name,
        email=t_user.email,
        password=TEST_PASS,
        language="deAT",
        theme="dark",
        rfid=None,
        is_active=False,
        is_superuser=False,
        is_adminuser=True,
        is_guestuser=True,
    )

    # ----------------------------------------------
    # UPDATE USER: METHODS TO TEST
    # ----------------------------------------------

    crud_user.update(db, db_obj=t_user, obj_in=t_user_in_update, current_user=t_user)

    # ----------------------------------------------
    # UPDATE USER: VALIDATION
    # ----------------------------------------------

    user = crud_user.get(db, id=t_user.id)
    assert user
    assert user.id == t_user.id
    assert user.is_active is True
    assert user.is_superuser is True
    assert user.is_adminuser is False
    assert user.is_guestuser is False


def test_update_admin_user_own_permissions(db: Session) -> None:
    """
    Test the update of an admin user's own permissions.

    This test verifies that an admin user cannot change their own permissions
    to lower their access level. Specifically, it ensures that the user remains
    active, a superuser, and an admin user, even if the update request attempts
    to change these attributes.

    Args:
        db (Session): The database session used for the test.

    Steps:
        1. Retrieve a test admin user from the database.
        2. Prepare an update schema with modified user attributes.
        3. Attempt to update the user with the new attributes.
        4. Validate that the user's critical permissions (is_active, is_superuser,
           is_adminuser) remain unchanged, while other attributes are updated
           as specified.

    Asserts:
        - The user exists in the database.
        - The user's ID remains unchanged.
        - The user's 'is_active' attribute remains True.
        - The user's 'is_superuser' attribute remains True.
        - The user's 'is_adminuser' attribute remains True.
        - The user's 'is_guestuser' attribute is updated to False.
    """

    # ----------------------------------------------
    # UPDATE USER: PREPARATION
    # ----------------------------------------------

    t_user = get_test_admin_user(db)

    t_user_in_update = UserUpdateSchema(
        username=t_user.username,
        full_name=t_user.full_name,
        email=t_user.email,
        password=TEST_PASS,
        language="deAT",
        theme="dark",
        rfid=None,
        is_active=False,
        is_superuser=False,
        is_adminuser=False,
        is_guestuser=True,
    )

    # ----------------------------------------------
    # UPDATE USER: METHODS TO TEST
    # ----------------------------------------------

    crud_user.update(db, db_obj=t_user, obj_in=t_user_in_update, current_user=t_user)

    # ----------------------------------------------
    # UPDATE USER: VALIDATION
    # ----------------------------------------------

    user = crud_user.get(db, id=t_user.id)
    assert user
    assert user.id == t_user.id
    assert user.is_active is True
    assert user.is_superuser is True
    assert user.is_adminuser is True
    assert user.is_guestuser is False


def test_update_guest_user_own_permissions(db: Session) -> None:
    """
    Test the update of a guest user's own permissions.

    This test performs the following steps:
    1. Preparation: Retrieve a test guest user from the database and create an update schema with new user details.
    2. Methods to Test: Call the `update` method from `crud_user` to update the user's information.
    3. Validation: Retrieve the updated user from the database and assert that the user's details have been updated correctly.

    Args:
        db (Session): The database session used for the test.

    Asserts:
        - The user exists in the database.
        - The user's ID remains unchanged.
        - The user's `is_active` status is `True`.
        - The user's `is_superuser` status is `False`.
        - The user's `is_adminuser` status is `False`.
        - The user's `is_guestuser` status is `True`.
    """

    # ----------------------------------------------
    # UPDATE USER: PREPARATION
    # ----------------------------------------------

    t_user = get_test_guest_user(db)

    t_user_in_update = UserUpdateSchema(
        username=t_user.username,
        full_name=t_user.full_name,
        email=t_user.email,
        password=TEST_PASS,
        language="deAT",
        theme="dark",
        rfid=None,
        is_active=False,
        is_superuser=True,
        is_adminuser=True,
        is_guestuser=False,
    )

    # ----------------------------------------------
    # UPDATE USER: METHODS TO TEST
    # ----------------------------------------------

    crud_user.update(db, db_obj=t_user, obj_in=t_user_in_update, current_user=t_user)

    # ----------------------------------------------
    # UPDATE USER: VALIDATION
    # ----------------------------------------------

    user = crud_user.get(db, id=t_user.id)
    assert user
    assert user.id == t_user.id
    assert user.is_active is True
    assert user.is_superuser is False
    assert user.is_adminuser is False
    assert user.is_guestuser is True
