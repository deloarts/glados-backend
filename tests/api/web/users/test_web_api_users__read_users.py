"""
    TEST WEB API -- USERS -- READ USERS
"""

from api.schemas.user import UserSchema
from config import cfg
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

READ_USERS_API = f"{cfg.server.api.web}/users"


def test_read_users__unauthorized(client: TestClient) -> None:
    """
    Test the unauthorized access to the read users API endpoint.
    This test ensures that when an unauthorized request is made to the
    READ_USERS_API endpoint, the response status code is 401 (Unauthorized).

    Args:
        client (TestClient): The test client used to make the API request.

    Assertions:
        - The response object is not None.
        - The response status code is 401.
    """

    # ----------------------------------------------
    # READ USERS: METHODS TO TEST
    # ----------------------------------------------

    response = client.get(READ_USERS_API, headers={})

    # ----------------------------------------------
    # READ USERS: VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 401
    assert response.json()["detail"] == "Access token not valid"


def test_read_users__normal_user(client: TestClient, normal_user_token_headers: dict) -> None:
    """
    Test the 'read users' API endpoint for a normal user.
    This test performs the following steps:

    1. Sends a GET request to the READ_USERS_API endpoint with normal user token headers.
    2. Parses the response into a list of UserSchema objects.
    3. Validates that the response contains users and that each user has an email, username, and full name.

    Args:
        client (TestClient): The test client to use for making requests.
        normal_user_token_headers (dict): The headers containing the normal user's authentication token.

    Asserts:
        The response contains a list of users.
        The list of users contains more than 4 users (test users).
        Each user in the response has an email, username, and full name.
    """

    # ----------------------------------------------
    # READ USERS: METHODS TO TEST
    # ----------------------------------------------

    response = client.get(READ_USERS_API, headers=normal_user_token_headers)
    response_schema = [UserSchema(**item) for item in response.json()]

    # ----------------------------------------------
    # READ USERS: VALIDATION
    # ----------------------------------------------

    assert response_schema
    assert len(response_schema) > 4
    for user in response_schema:
        assert user.email
        assert user.username
        assert user.full_name


def test_read_users__super_user(client: TestClient, super_user_token_headers: dict) -> None:
    """
    Test the 'read users' API endpoint for a super user.
    This test performs the following steps:

    1. Sends a GET request to the READ_USERS_API endpoint with super user token headers.
    2. Parses the response into a list of UserSchema objects.
    3. Validates that the response contains users and that each user has an email, username, and full name.

    Args:
        client (TestClient): The test client to use for making requests.
        super_user_token_headers (dict): The headers containing the super user token.
        db (Session): The database session.

    Asserts:
        The response contains a list of users.
        The list of users contains more than 4 users (test users).
        Each user in the response has an email, username, and full name.
    """

    # ----------------------------------------------
    # READ USERS: METHODS TO TEST
    # ----------------------------------------------

    response = client.get(READ_USERS_API, headers=super_user_token_headers)
    response_schema = [UserSchema(**item) for item in response.json()]

    # ----------------------------------------------
    # READ USERS: VALIDATION
    # ----------------------------------------------

    assert response_schema
    assert len(response_schema) > 4
    for user in response_schema:
        assert user.email
        assert user.username
        assert user.full_name


def test_read_users__admin_user(client: TestClient, admin_user_token_headers: dict) -> None:
    """
    Test the 'read users' functionality for an admin user.
    This test performs the following steps:

    1. Sends a GET request to the READ_USERS_API endpoint with admin user headers.
    2. Parses the response into a list of UserSchema objects.
    3. Validates that the response contains users and that each user has an email, username, and full name.

    Args:
        client (TestClient): The test client to simulate HTTP requests.
        admin_user_token_headers (dict): The headers containing the admin user's authentication token.
        db (Session): The database session.

    Asserts:
        The response contains a list of users.
        The list of users contains more than 4 users (test users).
        Each user in the response has an email, username, and full name.
    """

    # ----------------------------------------------
    # READ USERS: METHODS TO TEST
    # ----------------------------------------------

    response = client.get(READ_USERS_API, headers=admin_user_token_headers)
    response_schema = [UserSchema(**item) for item in response.json()]

    # ----------------------------------------------
    # READ USERS: VALIDATION
    # ----------------------------------------------

    assert response_schema
    assert len(response_schema) > 4
    for user in response_schema:
        assert user.email
        assert user.username
        assert user.full_name


def test_read_users__guest_user(client: TestClient, guest_user_token_headers: dict) -> None:
    """
    Test the 'read users' API endpoint for a guest user.
    This test verifies that a guest user can successfully retrieve a list of users
    from the 'read users' API endpoint. It checks the following:

    - The response contains a list of users.
    - The list contains more than 4 users.
    - Each user in the response has an email, username, and full name.

    Args:
        client (TestClient): The test client to simulate API requests.
        guest_user_token_headers (dict): The headers containing the guest user's authentication token.
        db (Session): The database session.

    Asserts:
        The response contains a list of users.
        The list of users contains more than 4 users (test users).
        Each user in the response has an email, username, and full name.
    """

    # ----------------------------------------------
    # READ USERS: METHODS TO TEST
    # ----------------------------------------------

    response = client.get(READ_USERS_API, headers=guest_user_token_headers)
    response_schema = [UserSchema(**item) for item in response.json()]

    # ----------------------------------------------
    # READ USERS: VALIDATION
    # ----------------------------------------------

    assert response_schema
    assert len(response_schema) > 4
    for user in response_schema:
        assert user.email
        assert user.username
        assert user.full_name


def test_read_users__system_user(client: TestClient, systemuser_token_headers: dict) -> None:
    """
    Test the 'read users' API endpoint for a system user.
    This test performs the following steps:

    1. Sends a GET request to the READ_USERS_API endpoint with system user token headers.
    2. Parses the response into a list of UserSchema objects.
    3. Validates that the response contains users and that each user has an email, username, and full name.

    Args:
        client (TestClient): The test client to use for making requests.
        systemuser_token_headers (dict): The headers to include in the request, containing the system user token.

    Asserts:
        - The response contains a list of users.
        - The number of users in the response is greater than 4.
        - Each user in the response has an email, username, and full name.
    """

    # ----------------------------------------------
    # READ USERS: METHODS TO TEST
    # ----------------------------------------------

    response = client.get(READ_USERS_API, headers=systemuser_token_headers)
    response_schema = [UserSchema(**item) for item in response.json()]

    # ----------------------------------------------
    # READ USERS: VALIDATION
    # ----------------------------------------------

    assert response_schema
    assert len(response_schema) > 4
    for user in response_schema:
        assert user.email
        assert user.username
        assert user.full_name
