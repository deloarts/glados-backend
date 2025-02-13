"""
    TEST WEB API -- USERS -- READ USER ME
"""

from typing import Dict

from api.schemas.user import UserSchema
from config import cfg
from const import SYSTEM_USER
from fastapi.testclient import TestClient

from tests.utils.user import TEST_ADMIN_MAIL
from tests.utils.user import TEST_GUEST_MAIL
from tests.utils.user import TEST_SUPER_MAIL
from tests.utils.user import TEST_USER_MAIL

READ_USER_ME_API = f"{cfg.server.api.web}/users/me"


def test_read_user_me__unauthorized(client: TestClient) -> None:
    """
    Test the /me endpoint for unauthorized access.
    This test verifies that an unauthorized request to the /me endpoint
    returns a 401 status code and the appropriate error message.

    Args:
        client (TestClient): The test client used to make the request.

    Assertions:
        - The response is not None.
        - The response status code is 401.
        - The response JSON contains the detail message.
    """

    # ----------------------------------------------
    # GET USER ME: METHODS TO TEST
    # ----------------------------------------------

    response = client.get(READ_USER_ME_API, headers={})

    # ----------------------------------------------
    # GET OWN USER: VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid access token"


def test_read_user_me__normal_user(client: TestClient, normal_user_token_headers: Dict[str, str]) -> None:
    """
    Test the 'read user me' endpoint for a normal user.
    This test verifies that a normal user can successfully retrieve their own user information
    using the 'read user me' API endpoint. It checks the following:

    - The response is received and has a status code of 200.
    - The response schema is correctly parsed.
    - The user is active.
    - The user is not a superuser.
    - The user is not an admin user.
    - The user is not a system user.
    - The user is not a guest user.
    - The user's email matches the expected test user email.

    Args:
        client (TestClient): The test client to simulate API requests.
        normal_user_token_headers (Dict[str, str]): The headers containing the normal user's authentication token.
    """

    # ----------------------------------------------
    # GET USER ME: METHODS TO TEST
    # ----------------------------------------------

    response = client.get(READ_USER_ME_API, headers=normal_user_token_headers)
    response_schema = UserSchema(**response.json())

    # ----------------------------------------------
    # GET OWN USER: VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 200

    assert response_schema
    assert response_schema.is_active is True
    assert response_schema.is_superuser is False
    assert response_schema.is_adminuser is False
    assert response_schema.is_systemuser is False
    assert response_schema.is_guestuser is False
    assert response_schema.email == TEST_USER_MAIL


def test_read_user_me__super_user(client: TestClient, super_user_token_headers: Dict[str, str]) -> None:
    """
    Test the 'read user me' endpoint for a super user.
    This test verifies that a super user can successfully retrieve their own user information
    using the 'read user me' endpoint. It checks the following:

    - The response status code is 200.
    - The response schema is valid.
    - The user is active.
    - The user is a superuser.
    - The user is not an admin user.
    - The user is not a system user.
    - The user is not a guest user.
    - The user's email matches the expected super user email.

    Args:
        client (TestClient): The test client to simulate API requests.
        super_user_token_headers (Dict[str, str]): The headers containing the super user's authentication token.
    """

    # ----------------------------------------------
    # GET USER ME: METHODS TO TEST
    # ----------------------------------------------

    response = client.get(READ_USER_ME_API, headers=super_user_token_headers)
    response_schema = UserSchema(**response.json())

    # ----------------------------------------------
    # GET OWN USER: VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 200

    assert response_schema
    assert response_schema.is_active is True
    assert response_schema.is_superuser is True
    assert response_schema.is_adminuser is False
    assert response_schema.is_systemuser is False
    assert response_schema.is_guestuser is False
    assert response_schema.email == TEST_SUPER_MAIL


def test_read_user_me__admin_user(client: TestClient, admin_user_token_headers: Dict[str, str]) -> None:
    """
    Test the 'read user me' endpoint for an admin user.
    This test verifies that an admin user can successfully retrieve their own user information
    using the 'read user me' API endpoint. It checks the following:

    - The response is received and has a status code of 200.
    - The response schema is valid and contains the expected user attributes.
    - The user is active, a superuser, and an admin user.
    - The user is not a system user or a guest user.
    - The user's email matches the expected admin email.

    Args:
        client (TestClient): The test client to simulate API requests.
        admin_user_token_headers (Dict[str, str]): The headers containing the admin user's authentication token.
    """

    # ----------------------------------------------
    # GET USER ME: METHODS TO TEST
    # ----------------------------------------------

    response = client.get(READ_USER_ME_API, headers=admin_user_token_headers)
    response_schema = UserSchema(**response.json())

    # ----------------------------------------------
    # GET OWN USER: VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 200

    assert response_schema
    assert response_schema.is_active is True
    assert response_schema.is_superuser is True
    assert response_schema.is_adminuser is True
    assert response_schema.is_systemuser is False
    assert response_schema.is_guestuser is False
    assert response_schema.email == TEST_ADMIN_MAIL


def test_read_user_me__guest_user(client: TestClient, guest_user_token_headers: Dict[str, str]) -> None:
    """
    Test the 'read user me' endpoint for a guest user.
    This test verifies that a guest user can successfully retrieve their own user information
    using the 'read user me' API endpoint. It checks the following:

    - The response is received and has a status code of 200.
    - The response schema is correctly populated.
    - The user is active.
    - The user is not a superuser, admin user, or system user.
    - The user is identified as a guest user.
    - The user's email matches the expected guest email.

    Args:
        client (TestClient): The test client to simulate API requests.
        guest_user_token_headers (Dict[str, str]): The headers containing the guest user's authentication token.
    """

    # ----------------------------------------------
    # GET USER ME: METHODS TO TEST
    # ----------------------------------------------

    response = client.get(READ_USER_ME_API, headers=guest_user_token_headers)
    response_schema = UserSchema(**response.json())

    # ----------------------------------------------
    # GET OWN USER: VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 200

    assert response_schema
    assert response_schema.is_active is True
    assert response_schema.is_superuser is False
    assert response_schema.is_adminuser is False
    assert response_schema.is_systemuser is False
    assert response_schema.is_guestuser is True
    assert response_schema.email == TEST_GUEST_MAIL


def test_read_user_me__system_user(client: TestClient, systemuser_token_headers: Dict[str, str]) -> None:
    """
    Test the 'read user me' endpoint for a system user.
    This test verifies that the 'read user me' endpoint returns the correct
    user information for a system user, including the user's active status,
    superuser status, admin user status, system user status, guest user status,
    and username.

    Args:
        client (TestClient): The test client to use for making the request.
        systemuser_token_headers (Dict[str, str]): The headers containing the
            authentication token for the system user.

    Asserts:
        - The response is not None.
        - The response status code is 200.
        - The response schema is valid.
        - The user is active.
        - The user is a superuser.
        - The user is an admin user.
        - The user is a system user.
        - The user is not a guest user.
        - The username matches the expected system user username.
    """

    # ----------------------------------------------
    # GET USER ME: METHODS TO TEST
    # ----------------------------------------------

    response = client.get(READ_USER_ME_API, headers=systemuser_token_headers)
    response_schema = UserSchema(**response.json())

    # ----------------------------------------------
    # GET USER ME: VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 200

    assert response_schema
    assert response_schema.is_active is True
    assert response_schema.is_superuser is True
    assert response_schema.is_adminuser is True
    assert response_schema.is_systemuser is True
    assert response_schema.is_guestuser is False
    assert response_schema.username == SYSTEM_USER
