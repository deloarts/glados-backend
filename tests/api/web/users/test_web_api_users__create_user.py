"""
    TEST WEB API -- USERS -- CREATE USER
"""

from typing import Dict

from api.schemas.user import UserSchema
from config import cfg
from crud.user import crud_user
from fastapi.testclient import TestClient
from locales import lang
from sqlalchemy.orm import Session

from tests.utils.user import TEST_USER_MAIL
from tests.utils.user import TEST_USER_USERNAME
from tests.utils.user import get_test_admin_user
from tests.utils.user import get_test_user
from tests.utils.utils import random_email
from tests.utils.utils import random_lower_string
from tests.utils.utils import random_name
from tests.utils.utils import random_username

CREATE_USER_API = f"{cfg.server.api.web}/users"


def test_create_user__unauthorized(client: TestClient) -> None:
    """
    Test the unauthorized creation of a user.
    This test ensures that when an attempt is made to create a user without
    providing the necessary authorization headers, the API responds with a
    401 Unauthorized status code and an appropriate error message.

    Args:
        client (TestClient): The test client used to make requests to the API.

    Assertions:
        - The response object is not None.
        - The response status code is 401.
        - The response JSON contains a "detail" key with the value "Invalid access token".
    """

    # ----------------------------------------------
    # GET USER ME: METHODS TO TEST
    # ----------------------------------------------

    response = client.post(CREATE_USER_API, headers={})

    # ----------------------------------------------
    # GET OWN USER: VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid access token"


def test_create_user__normal_user(client: TestClient, normal_user_token_headers: Dict[str, str], db: Session) -> None:
    """
    Test the creation of a user with normal user privileges.
    This test verifies that a normal user is not allowed to create a new user
    and receives a 403 Forbidden status code in response.

    Args:
        client (TestClient): The test client used to make requests to the API.
        normal_user_token_headers (Dict[str, str]): The headers containing the
            authentication token for a normal user.

    Asserts:
        response: The response object from the API call.
        response.status_code == 403: Ensures that the status code of the response
            is 403 Forbidden.
    """

    # ----------------------------------------------
    # GET USER ME: METHODS TO TEST
    # ----------------------------------------------

    response = client.post(CREATE_USER_API, headers=normal_user_token_headers)

    # ----------------------------------------------
    # GET OWN USER: VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 403
    assert response.json()["detail"] == lang(get_test_user(db)).API.DEPS.ADMINUSER_REQUIRED


def test_create_user__super_user(client: TestClient, super_user_token_headers: Dict[str, str], db: Session) -> None:
    """
    Test the creation of a user by a super user.
    This test verifies that a super user is unable to create a new user
    and receives a 403 Forbidden status code.

    Args:
        client (TestClient): The test client to simulate API requests.
        super_user_token_headers (Dict[str, str]): The headers containing the super user token.
    """

    # ----------------------------------------------
    # GET USER ME: METHODS TO TEST
    # ----------------------------------------------

    response = client.post(CREATE_USER_API, headers=super_user_token_headers)

    # ----------------------------------------------
    # GET OWN USER: VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 403
    assert response.json()["detail"] == lang(get_test_user(db)).API.DEPS.ADMINUSER_REQUIRED


def test_create_user__admin_user(client: TestClient, admin_user_token_headers: dict, db: Session) -> None:
    """
    Test the creation of a new user by an admin user.
    This test performs the following steps:

    1. Preparation: Generate random user data (username, email, password, full name).
    2. Methods to Test: Send a POST request to create a new user using the admin user's token.
    3. Validation: Verify that the user is created successfully in the database and the response matches the expected data.

    Args:
        client (TestClient): The test client to simulate API requests.
        admin_user_token_headers (dict): The headers containing the admin user's authentication token.
        db (Session): The database session for querying the database.

    Asserts:
        - The user is successfully created in the database.
        - The response status code is 200.
        - The created user is active.
        - The created user's details (id, username, email, full name) match the expected data.
    """

    # ----------------------------------------------
    # CREATE USER: PREPARATION
    # ----------------------------------------------

    t_username = random_username()
    t_email = random_email()
    t_password = random_lower_string()
    t_full_name = random_name()
    t_data = {"email": t_email, "password": t_password, "username": t_username, "full_name": t_full_name}

    # ----------------------------------------------
    # CREATE USER: METHODS TO TEST
    # ----------------------------------------------

    response = client.post(CREATE_USER_API, headers=admin_user_token_headers, json=t_data)
    created_user = UserSchema(**response.json())

    # ----------------------------------------------
    # CREATE USER: VALIDATION
    # ----------------------------------------------

    db_user = crud_user.get_by_email(db, email=t_email)
    assert db_user

    assert response.status_code == 200

    assert created_user
    assert created_user.is_active == True
    assert created_user.id == db_user.id
    assert created_user.username == db_user.username == t_username
    assert created_user.email == db_user.email == t_email
    assert created_user.full_name == db_user.full_name == t_full_name


def test_create_user__system_user(client: TestClient, systemuser_token_headers: dict, db: Session) -> None:
    """
    Test the creation of a new user by a system user.
    This test performs the following steps:

    1. Prepares the data for a new user including username, email, password, and full name.
    2. Sends a POST request to create the user using the provided system user token headers.
    3. Validates the response and checks that the user was created successfully in the database.

    Args:
        client (TestClient): The test client to simulate API requests.
        systemuser_token_headers (dict): The headers containing the system user token for authentication.
        db (Session): The database session to query the database.

    Asserts:
        - The user exists in the database.
        - The response status code is 200.
        - The created user is active.
        - The created user's details match the expected values.
    """

    # ----------------------------------------------
    # CREATE USER: PREPARATION
    # ----------------------------------------------

    t_username = random_username()
    t_email = random_email()
    t_password = random_lower_string()
    t_full_name = random_name()
    t_data = {"email": t_email, "password": t_password, "username": t_username, "full_name": t_full_name}

    # ----------------------------------------------
    # CREATE USER: METHODS TO TEST
    # ----------------------------------------------

    response = client.post(CREATE_USER_API, headers=systemuser_token_headers, json=t_data)
    created_user = UserSchema(**response.json())

    # ----------------------------------------------
    # CREATE USER: VALIDATION
    # ----------------------------------------------

    db_user = crud_user.get_by_email(db, email=t_email)
    assert db_user

    assert response.status_code == 200

    assert created_user
    assert created_user.is_active == True
    assert created_user.id == db_user.id
    assert created_user.username == db_user.username == t_username
    assert created_user.email == db_user.email == t_email
    assert created_user.full_name == db_user.full_name == t_full_name


def test_create_user__admin_user__existing_username(
    client: TestClient, admin_user_token_headers: dict, db: Session
) -> None:
    """
    Test case for creating a user with an existing username by an admin user.
    This test verifies that attempting to create a user with a username that already exists
    in the database results in a 406 Not Acceptable status code and the appropriate error message.

    Args:
        client (TestClient): The test client to simulate API requests.
        admin_user_token_headers (dict): The headers containing the admin user's authentication token.
        db (Session): The database session.
    """

    # ----------------------------------------------
    # CREATE EXISTING USER: PREPARATION
    # ----------------------------------------------

    data = {
        "email": random_email(),
        "password": random_lower_string(),
        "username": TEST_USER_USERNAME,
        "full_name": random_name(),
    }

    # ----------------------------------------------
    # CREATE EXISTING USER: METHODS TO TEST
    # ----------------------------------------------

    response = client.post(CREATE_USER_API, headers=admin_user_token_headers, json=data)

    # ----------------------------------------------
    # CREATE EXISTING USER: VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 406
    assert response.json()["detail"] == lang(get_test_admin_user(db)).API.USER.USERNAME_IN_USE


def test_create_user__admin_user__existing_mail(
    client: TestClient, admin_user_token_headers: dict, db: Session
) -> None:
    """
    Test the creation of a user with an email that already exists in the system.
    This test simulates an admin user attempting to create a new user with an email
    that is already in use. It verifies that the API returns a 406 status code and
    the appropriate error message indicating that the email is already in use.

    Args:
        client (TestClient): The test client to simulate API requests.
        admin_user_token_headers (dict): The headers containing the admin user's authentication token.
        db (Session): The database session for accessing the database.

    Assertions:
        - The response object is not None.
        - The response status code is 406.
        - The response JSON contains the expected error message indicating the email is already in use.
    """

    # ----------------------------------------------
    # CREATE EXISTING USER: PREPARATION
    # ----------------------------------------------

    data = {
        "email": TEST_USER_MAIL,
        "password": random_lower_string(),
        "username": random_username(),
        "full_name": random_name(),
    }

    # ----------------------------------------------
    # CREATE EXISTING USER: METHODS TO TEST
    # ----------------------------------------------

    response = client.post(CREATE_USER_API, headers=admin_user_token_headers, json=data)

    # ----------------------------------------------
    # CREATE EXISTING USER: VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 406
    assert response.json()["detail"] == lang(get_test_admin_user(db)).API.USER.MAIL_IN_USE


def test_create_user__admin_user__missing_data(client: TestClient, admin_user_token_headers: dict) -> None:
    """
    Test the creation of a user with missing data by an admin user.
    This test verifies that attempting to create a user without providing all required fields
    results in a 422 Unprocessable Entity status code and the appropriate error message.

    Args:
        client (TestClient): The test client used to make HTTP requests.
        admin_user_token_headers (dict): The headers containing the admin user's authentication token.

    Assertions:
        - The response is not None.
        - The response status code is 422.
        - The error detail indicates that the 'username' field is required.
    """

    # ----------------------------------------------
    # CREATE EXISTING USER: PREPARATION
    # ----------------------------------------------

    data = {
        "email": random_email(),
        "password": random_lower_string(),
        "full_name": random_name(),
    }

    # ----------------------------------------------
    # CREATE EXISTING USER: METHODS TO TEST
    # ----------------------------------------------

    response = client.post(CREATE_USER_API, headers=admin_user_token_headers, json=data)

    # ----------------------------------------------
    # CREATE EXISTING USER: VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"][1] == "username"
    assert response.json()["detail"][0]["msg"] == "Field required"
    assert response.json()["detail"][0]["type"] == "missing"
