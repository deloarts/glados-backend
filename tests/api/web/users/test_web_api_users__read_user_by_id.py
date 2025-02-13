"""
    TEST WEB API -- USERS -- READ USER BY ID
"""

from api.schemas.user import UserSchema
from config import cfg
from fastapi.testclient import TestClient
from locales import lang
from sqlalchemy.orm import Session

from tests.utils.user import get_test_user

READ_USER_BY_ID_API = f"{cfg.server.api.web}/users"


def test_read_user_by_id__unauthorized(client: TestClient, db: Session) -> None:
    """
    Test case for reading a user by ID without authorization.
    This test verifies that an unauthorized request to read a user by ID
    returns a 401 Unauthorized status code.

    Steps:
        1. Prepare a test user in the database.
        2. Make a GET request to the read user by ID endpoint without authorization headers.
        3. Validate that the response status code is 401 Unauthorized.

    Args:
        client (TestClient): The test client used to make HTTP requests.
        db (Session): The database session used to interact with the test database.

    Asserts:
        - The response object is not None.
        - The response status code is 401 Unauthorized.
    """

    # ----------------------------------------------
    # READ USER BY ID: PREPARATION
    # ----------------------------------------------

    t_user = get_test_user(db)

    # ----------------------------------------------
    # READ USER BY ID: METHODS TO TEST
    # ----------------------------------------------

    response = client.get(f"{READ_USER_BY_ID_API}/{t_user.id}", headers={})

    # ----------------------------------------------
    # READ USER BY ID: VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid access token"


def test_read_user_by_id__normal_user(client: TestClient, normal_user_token_headers: dict, db: Session) -> None:
    """
    Test the 'read user by id' functionality for a normal user.
    This test verifies that a normal user can successfully retrieve their own user information
    by making a GET request to the 'read user by id' API endpoint.

    Args:
        client (TestClient): The test client used to make HTTP requests.
        normal_user_token_headers (dict): The headers containing the authentication token for a normal user.
        db (Session): The database session used to interact with the database.
    """

    # ----------------------------------------------
    # READ USER BY ID: PREPARATION
    # ----------------------------------------------

    t_user = get_test_user(db)

    # ----------------------------------------------
    # READ USER BY ID: METHODS TO TEST
    # ----------------------------------------------

    response = client.get(f"{READ_USER_BY_ID_API}/{t_user.id}", headers=normal_user_token_headers)
    response_schema = UserSchema(**response.json())

    # ----------------------------------------------
    # READ USER BY ID: VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 200

    assert response_schema
    assert response_schema.id == t_user.id
    assert response_schema.email == t_user.email
    assert response_schema.username == t_user.username


def test_read_user_by_id__super_user(client: TestClient, super_user_token_headers: dict, db: Session) -> None:
    """
    Test the 'read user by ID' API endpoint for a super user.
    This test performs the following steps:

    1. Preparation:
       - Retrieve a test user from the database.
    2. Methods to Test:
       - Send a GET request to the 'read user by ID' API endpoint with the super user token headers.
    3. Validation:
       - Assert that the response is not None.
       - Assert that the response status code is 200 (OK).
       - Assert that the response schema is valid and matches the test user's details (ID, email, username).

    Args:
        client (TestClient): The test client to simulate API requests.
        super_user_token_headers (dict): The headers containing the super user authentication token.
        db (Session): The database session for accessing the test user.
    """

    # ----------------------------------------------
    # READ USER BY ID: PREPARATION
    # ----------------------------------------------

    t_user = get_test_user(db)

    # ----------------------------------------------
    # READ USER BY ID: METHODS TO TEST
    # ----------------------------------------------

    response = client.get(f"{READ_USER_BY_ID_API}/{t_user.id}", headers=super_user_token_headers)
    response_schema = UserSchema(**response.json())

    # ----------------------------------------------
    # READ USER BY ID: VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 200

    assert response_schema
    assert response_schema.id == t_user.id
    assert response_schema.email == t_user.email
    assert response_schema.username == t_user.username


def test_read_user_by_id__admin_user(client: TestClient, admin_user_token_headers: dict, db: Session) -> None:
    """
    Test the 'read user by ID' functionality for an admin user.
    This test performs the following steps:

    1. Preparation: Retrieve a test user from the database.
    2. Methods to Test: Send a GET request to the 'read user by ID' API endpoint using the admin user's token headers.
    3. Validation: Verify the response status code and the response schema to ensure the user details match the expected values.

    Args:
        client (TestClient): The test client to simulate API requests.
        admin_user_token_headers (dict): The headers containing the admin user's authentication token.
        db (Session): The database session to interact with the database.
    """

    # ----------------------------------------------
    # READ USER BY ID: PREPARATION
    # ----------------------------------------------

    t_user = get_test_user(db)

    # ----------------------------------------------
    # READ USER BY ID: METHODS TO TEST
    # ----------------------------------------------

    response = client.get(f"{READ_USER_BY_ID_API}/{t_user.id}", headers=admin_user_token_headers)
    response_schema = UserSchema(**response.json())

    # ----------------------------------------------
    # READ USER BY ID: VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 200

    assert response_schema
    assert response_schema.id == t_user.id
    assert response_schema.email == t_user.email
    assert response_schema.username == t_user.username


def test_read_user_by_id__guest_user(client: TestClient, guest_user_token_headers: dict, db: Session) -> None:
    """
    Test the 'read user by ID' endpoint for a guest user.
    This test verifies that a guest user can successfully retrieve user details by ID.

    Steps:
        1. Prepare a test user.
        2. Make a GET request to the 'read user by ID' endpoint with the test user's ID.
        3. Validate the response status code and the returned user details.

    Args:
        client (TestClient): The test client to simulate API requests.
        guest_user_token_headers (dict): The headers containing the guest user's authentication token.
        db (Session): The database session for accessing the test database.

    Assertions:
        - The response is not None.
        - The response status code is 200 (OK).
        - The response schema is valid and matches the test user's details.
    """

    # ----------------------------------------------
    # READ USER BY ID: PREPARATION
    # ----------------------------------------------

    t_user = get_test_user(db)

    # ----------------------------------------------
    # READ USER BY ID: METHODS TO TEST
    # ----------------------------------------------

    response = client.get(f"{READ_USER_BY_ID_API}/{t_user.id}", headers=guest_user_token_headers)
    response_schema = UserSchema(**response.json())

    # ----------------------------------------------
    # READ USER BY ID: VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 200

    assert response_schema
    assert response_schema.id == t_user.id
    assert response_schema.email == t_user.email
    assert response_schema.username == t_user.username


def test_read_user_by_id__system_user(client: TestClient, systemuser_token_headers: dict, db: Session) -> None:
    """
    Test the 'read user by id' endpoint for a system user.
    This test performs the following steps:

    1. Preparation:
       - Retrieve a test user from the database.
    2. Methods to Test:
       - Send a GET request to the 'read user by id' API endpoint with the system user's token headers.
    3. Validation:
       - Assert that the response is not None.
       - Assert that the response status code is 200 (OK).
       - Assert that the response schema is valid and matches the test user's details (id, email, username).

    Args:
        client (TestClient): The test client to simulate API requests.
        systemuser_token_headers (dict): The headers containing the system user's authentication token.
        db (Session): The database session for accessing the test user.
    """

    # ----------------------------------------------
    # READ USER BY ID: PREPARATION
    # ----------------------------------------------

    t_user = get_test_user(db)

    # ----------------------------------------------
    # READ USER BY ID: METHODS TO TEST
    # ----------------------------------------------

    response = client.get(f"{READ_USER_BY_ID_API}/{t_user.id}", headers=systemuser_token_headers)
    response_schema = UserSchema(**response.json())

    # ----------------------------------------------
    # READ USER BY ID: VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 200

    assert response_schema
    assert response_schema.id == t_user.id
    assert response_schema.email == t_user.email
    assert response_schema.username == t_user.username


def test_read_user_by_id__normal_user__unknown_user_id(
    client: TestClient, normal_user_token_headers: dict, db: Session
) -> None:
    """
    Test the 'read user by id' endpoint with a normal user and an unknown user ID.
    This test ensures that when a normal user tries to read a user by an ID that does not exist,
    the API responds with a 404 status code and the appropriate error message.

    Args:
        client (TestClient): The test client to simulate API requests.
        normal_user_token_headers (dict): The headers containing the normal user's authentication token.
        db (Session): The database session for accessing the test database.

    Assertions:
        - The response is not None.
        - The response status code is 404.
        - The response JSON contains the detail message indicating the user was not found.
    """

    # ----------------------------------------------
    # READ USER BY ID: PREPARATION
    # ----------------------------------------------

    t_user = get_test_user(db)

    # ----------------------------------------------
    # READ USER BY ID: METHODS TO TEST
    # ----------------------------------------------

    response = client.get(f"{READ_USER_BY_ID_API}/9999999", headers=normal_user_token_headers)

    # ----------------------------------------------
    # READ USER BY ID: VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 404
    assert response.json()["detail"] == lang(t_user).API.USER.NOT_FOUND


def test_read_user_by_id__normal_user__invalid_query_param(client: TestClient, normal_user_token_headers: dict) -> None:
    """
    Test case for reading a user by ID with an invalid query parameter.
    This test ensures that when a normal user attempts to read a user by ID
    using an invalid query parameter (non-integer), the API responds with
    a 422 Unprocessable Entity status code and the appropriate validation
    error message.

    Args:
        client (TestClient): The test client to simulate API requests.
        normal_user_token_headers (dict): The headers containing the normal user's authentication token.
        db (Session): The database session.

    Asserts:
        - The response is not None.
        - The response status code is 422.
        - The validation error location is in the path and specifically for the 'user_id' parameter.
        - The validation error message indicates that the input should be a valid integer.
    """

    # ----------------------------------------------
    # READ USER BY ID: METHODS TO TEST
    # ----------------------------------------------

    response = client.get(f"{READ_USER_BY_ID_API}/A", headers=normal_user_token_headers)

    # ----------------------------------------------
    # READ USER BY ID: VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"][0] == "path"
    assert response.json()["detail"][0]["loc"][1] == "user_id"
    assert (
        response.json()["detail"][0]["msg"] == "Input should be a valid integer, unable to parse string as an integer"
    )
