from api.schemas.user import UserCreateSchema
from crud.user import crud_user
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from tests.utils.user import current_user_adminuser
from tests.utils.user import get_test_user
from tests.utils.utils import random_email
from tests.utils.utils import random_lower_string
from tests.utils.utils import random_name
from tests.utils.utils import random_username


def test_get_user(db: Session) -> None:
    """
    Test the retrieval of a user from the database.
    This test performs the following steps:

    1. Preparation: Create a test user in the database.
    2. Methods to Test: Retrieve the user from the database using the `crud_user.get` method.
    3. Validation: Assert that the retrieved user exists, is the same as the test user, and has the same attributes.

    Args:
        db (Session): The database session used for the test.
    """

    # ----------------------------------------------
    # GET USER: PREPARATION
    # ----------------------------------------------

    t_user = get_test_user(db)

    # ----------------------------------------------
    # GET USER: METHODS TO TEST
    # ----------------------------------------------

    user_2 = crud_user.get(db, id=t_user.id)

    # ----------------------------------------------
    # GET USER: VALIDATION
    # ----------------------------------------------

    assert user_2
    assert user_2 is t_user
    assert user_2.username == t_user.username
    assert user_2.email == t_user.email
    assert jsonable_encoder(t_user) == jsonable_encoder(user_2)


def test_get_user_non_existent(db: Session) -> None:
    """
    Test the retrieval of a non-existent user from the database.
    This test ensures that attempting to retrieve a user with an ID that does not
    exist in the database returns None.

    Test Steps:
    1. Attempt to retrieve a user with an ID of 0, which is assumed to be non-existent.
    2. Validate that the returned user is None.

    Args:
        db (Session): The database session used for the test.
    """

    # ----------------------------------------------
    # GET USER (NON-EXISTENT): PREPARATION
    # ----------------------------------------------

    # ----------------------------------------------
    # GET USER (NON-EXISTENT): METHODS TO TEST
    # ----------------------------------------------

    user = crud_user.get(db, id=0)

    # ----------------------------------------------
    # GET USER (NON-EXISTENT): VALIDATION
    # ----------------------------------------------

    assert user is None


def test_get_user_by_username(db: Session) -> None:
    """
    Test the functionality of retrieving a user by their username.
    This test performs the following steps:

    1. Preparation: Create a test user in the database.
    2. Methods to Test: Retrieve the user from the database using their username.
    3. Validation: Verify that the retrieved user matches the test user.

    Args:
        db (Session): The database session used for the test.

    Asserts:
        - The retrieved user exists.
        - The retrieved user is the same as the test user.
        - The username of the retrieved user matches the test user's username.
        - The email of the retrieved user matches the test user's email.
        - The JSON representation of the test user matches the JSON representation of the retrieved user.
    """

    # ----------------------------------------------
    # GET USER BY USERNAME: PREPARATION
    # ----------------------------------------------

    t_user = get_test_user(db)

    # ----------------------------------------------
    # GET USER BY USERNAME: METHODS TO TEST
    # ----------------------------------------------

    user_2 = crud_user.get_by_username(db, username=t_user.username)

    # ----------------------------------------------
    # GET USER BY USERNAME: VALIDATION
    # ----------------------------------------------

    assert user_2
    assert user_2 is t_user
    assert user_2.username == t_user.username
    assert user_2.email == t_user.email
    assert jsonable_encoder(t_user) == jsonable_encoder(user_2)


def test_get_user_by_username_non_existent(db: Session) -> None:
    """
    Test case for retrieving a user by username when the user does not exist.
    This test ensures that the `get_by_username` method of the `crud_user` module
    returns `None` when attempting to retrieve a user with a username that does not exist
    in the database.

    Args:
        db (Session): The database session used for the test.

    Steps:
        1. Call the `get_by_username` method with a non-existent username.
        2. Validate that the returned user is `None`.

    Asserts:
        - The returned user is `None`.
    """

    # ----------------------------------------------
    # GET USER BY USERNAME (NON-EXISTENT): PREPARATION
    # ----------------------------------------------

    # ----------------------------------------------
    # GET USER BY USERNAME (NON-EXISTENT): METHODS TO TEST
    # ----------------------------------------------

    user = crud_user.get_by_username(db, username="definitely not the username")

    # ----------------------------------------------
    # GET USER BY USERNAME (NON-EXISTENT): VALIDATION
    # ----------------------------------------------

    assert user is None


def test_get_user_by_mail(db: Session) -> None:
    """
    Test the functionality of retrieving a user by their email.
    This test performs the following steps:

    1. Preparation: Create a test user in the database.
    2. Methods to Test: Retrieve the user from the database using their email.
    3. Validation: Verify that the retrieved user matches the test user.

    Args:
        db (Session): The database session used for the test.

    Asserts:
        - The retrieved user exists.
        - The retrieved user is the same as the test user.
        - The username of the retrieved user matches the test user's username.
        - The email of the retrieved user matches the test user's email.
        - The JSON representation of the test user matches the JSON representation of the retrieved user.
    """

    # ----------------------------------------------
    # GET USER BY MAIL: PREPARATION
    # ----------------------------------------------

    t_user = get_test_user(db)

    # ----------------------------------------------
    # GET USER BY MAIL: METHODS TO TEST
    # ----------------------------------------------

    user_2 = crud_user.get_by_email(db, email=t_user.email)

    # ----------------------------------------------
    # GET USER BY MAIL: VALIDATION
    # ----------------------------------------------

    assert user_2
    assert user_2 is t_user
    assert user_2.username == t_user.username
    assert user_2.email == t_user.email
    assert jsonable_encoder(t_user) == jsonable_encoder(user_2)


def test_get_user_by_mail_non_existent(db: Session) -> None:
    """
    Test the retrieval of a user by email when the user does not exist in the database.
    This test ensures that the `get_by_email` method of the `crud_user` module
    returns `None` when queried with an email that does not correspond to any
    user in the database.

    Args:
        db (Session): The database session used for the test.

    Steps:
        1. Prepare the test by ensuring no user exists with the specified email.
        2. Call the `get_by_email` method with a non-existent email.
        3. Validate that the returned result is `None`.

    Asserts:
        - The returned user is `None`.
    """

    # ----------------------------------------------
    # GET USER BY MAIL (NON-EXISTENT): PREPARATION
    # ----------------------------------------------

    # ----------------------------------------------
    # GET USER BY MAIL (NON-EXISTENT): METHODS TO TEST
    # ----------------------------------------------

    user = crud_user.get_by_email(db, email="definitely not the mail")

    # ----------------------------------------------
    # GET USER BY MAIL (NON-EXISTENT): VALIDATION
    # ----------------------------------------------

    assert user is None


def test_get_user_by_rfid(db: Session) -> None:
    """
    Test the functionality of retrieving a user by RFID from the database.
    This test performs the following steps:

    1. Preparation:
        - Generate random values for username, full name, email, password, and RFID.
        - Ensure the generated username, email, and RFID are unique in the database.
        - Create a new user with the generated values.
    2. Methods to Test:
        - Retrieve the user by RFID using the CRUD operation.
    3. Validation:
        - Assert that the retrieved user exists.
        - Assert that the retrieved user is the same as the created user.
        - Assert that the username and email of the retrieved user match those of the created user.
        - Assert that the JSON representation of the created user matches that of the retrieved user.

    Args:
        db (Session): The database session used for the test.
    """

    # ----------------------------------------------
    # GET USER BY RFID: PREPARATION
    # ----------------------------------------------

    t_username = random_username()
    t_full_name = random_name()
    t_email = random_email()
    t_password = random_lower_string()
    t_rfid = random_lower_string()

    # Ensure that the generated username and mail does not exist
    # Both are unique in the db
    while (
        crud_user.get_by_username(db, username=t_username)
        or crud_user.get_by_email(db, email=t_email)
        or crud_user.get_by_rfid(db, rfid=t_rfid)
    ):
        t_username = random_username()
        t_email = random_email()
        t_rfid = random_lower_string()

    t_user_in = UserCreateSchema(
        username=t_username,
        full_name=t_full_name,
        email=t_email,
        password=t_password,
        rfid=t_rfid,
    )
    t_user = crud_user.create(db, obj_in=t_user_in, current_user=current_user_adminuser())

    # ----------------------------------------------
    # GET USER BY RFID: METHODS TO TEST
    # ----------------------------------------------

    user_2 = crud_user.get_by_rfid(db, rfid=t_rfid)

    # ----------------------------------------------
    # GET USER BY RFID: VALIDATION
    # ----------------------------------------------

    assert user_2
    assert user_2 is t_user
    assert user_2.username == t_user.username
    assert user_2.email == t_user.email
    assert jsonable_encoder(t_user) == jsonable_encoder(user_2)


def test_get_user_by_rfid_non_existent(db: Session) -> None:
    """
    Test the retrieval of a user by RFID when the user does not exist in the database.
    This test ensures that the `get_by_rfid` method of the `crud_user` module returns `None`
    when an RFID that does not correspond to any user in the database is provided.

    Args:
        db (Session): The database session used for the test.

    Assertions:
        Asserts that the returned user is `None` when a non-existent RFID is queried.
    """

    # ----------------------------------------------
    # GET USER BY RFID (NON-EXISTENT): PREPARATION
    # ----------------------------------------------

    # ----------------------------------------------
    # GET USER BY RFID (NON-EXISTENT): METHODS TO TEST
    # ----------------------------------------------

    user = crud_user.get_by_rfid(db, rfid="definitely not the mail")

    # ----------------------------------------------
    # GET USER BY RFID (NON-EXISTENT): VALIDATION
    # ----------------------------------------------

    assert user is None
