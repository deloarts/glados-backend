"""
    TEST WEB API -- USERS -- UPDATE USER ME -- PERSONAL ACCESS TOKEN
"""

from typing import Dict

from config import cfg
from fastapi.testclient import TestClient
from locales import lang
from sqlalchemy.orm import Session

from tests.utils.user import get_test_guest_user

PUT_USER_ME_PERSONAL_ACCESS_TOKEN_API = f"{cfg.server.api.web}/users/me/personal-access-token"


def test_update_user_personal_access_token__unauthorized(client: TestClient) -> None:
    """
    Test the unauthorized update of a user's personal access token.

    This test ensures that an unauthorized request to update the user's personal access token
    returns a 401 status code with the appropriate error message.

    Args:
        client (TestClient): The test client used to make the request.

    Assertions:
        - The response is not None.
        - The response status code is 401 (Unauthorized).
        - The response JSON contains a "detail" key with the value "Invalid access token".
    """

    # ----------------------------------------------
    # GET USER ME: METHODS TO TEST
    # ----------------------------------------------

    response = client.put(PUT_USER_ME_PERSONAL_ACCESS_TOKEN_API, headers={})

    # ----------------------------------------------
    # GET OWN USER: VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid access token"


def test_update_user_personal_access_token__normal_user(
    client: TestClient, normal_user_token_headers: Dict[str, str]
) -> None:
    """
    Test the update of a user's personal access token for a normal user.
    This test performs the following steps:

    1. Prepares the expiration time for the token.
    2. Sends a PUT request to update the user's personal access token.
    3. Validates the response to ensure the token was updated successfully.

    Args:
        client (TestClient): The test client to send requests.
        normal_user_token_headers (Dict[str, str]): The headers containing the normal user's token.

    Asserts:
        The response is not None.
        The response status code is 200.
        The response JSON is a string.
    """

    # ----------------------------------------------
    # UPDATE USER ME: PREPARATION
    # ----------------------------------------------

    t_expiration_in_minutes = 1

    # ----------------------------------------------
    # GET USER ME: METHODS TO TEST
    # ----------------------------------------------

    response = client.put(
        PUT_USER_ME_PERSONAL_ACCESS_TOKEN_API,
        headers=normal_user_token_headers,
        params={"expires_in_minutes": t_expiration_in_minutes},
    )

    # ----------------------------------------------
    # GET OWN USER: VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 200
    assert isinstance(response.json(), str)


def test_update_user_personal_access_token__super_user(
    client: TestClient, super_user_token_headers: Dict[str, str]
) -> None:
    """
    Test the update of a personal access token for a super user.

    This test performs the following steps:
    1. Sets the expiration time for the token to 1 minute.
    2. Sends a PUT request to update the personal access token using the provided super user headers.
    3. Validates the response to ensure the token was updated successfully.

    Args:
        client (TestClient): The test client to send requests.
        super_user_token_headers (Dict[str, str]): The headers containing the super user token.

    Asserts:
        The response is not None.
        The response status code is 200.
        The response JSON is a string.
    """

    # ----------------------------------------------
    # UPDATE USER ME: PREPARATION
    # ----------------------------------------------

    t_expiration_in_minutes = 1

    # ----------------------------------------------
    # GET USER ME: METHODS TO TEST
    # ----------------------------------------------

    response = client.put(
        PUT_USER_ME_PERSONAL_ACCESS_TOKEN_API,
        headers=super_user_token_headers,
        params={"expires_in_minutes": t_expiration_in_minutes},
    )

    # ----------------------------------------------
    # GET OWN USER: VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 200
    assert isinstance(response.json(), str)


def test_update_user_personal_access_token__admin_user(
    client: TestClient, admin_user_token_headers: Dict[str, str]
) -> None:
    """
    Test the update of a user's personal access token by an admin user.

    This test performs the following steps:
    1. Prepares the expiration time for the token.
    2. Sends a PUT request to update the user's personal access token.
    3. Validates the response to ensure the token is updated successfully.

    Args:
        client (TestClient): The test client to send requests.
        admin_user_token_headers (Dict[str, str]): Headers containing the admin user's token.

    Asserts:
        The response is not None.
        The response status code is 200.
        The response JSON is a string.
    """

    # ----------------------------------------------
    # UPDATE USER ME: PREPARATION
    # ----------------------------------------------

    t_expiration_in_minutes = 1

    # ----------------------------------------------
    # GET USER ME: METHODS TO TEST
    # ----------------------------------------------

    response = client.put(
        PUT_USER_ME_PERSONAL_ACCESS_TOKEN_API,
        headers=admin_user_token_headers,
        params={"expires_in_minutes": t_expiration_in_minutes},
    )

    # ----------------------------------------------
    # GET OWN USER: VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 200
    assert isinstance(response.json(), str)


def test_update_user_personal_access_token__system_user(
    client: TestClient, systemuser_token_headers: Dict[str, str]
) -> None:
    """
    Test the update of a user's personal access token for a system user.

    This test performs the following steps:
    1. Prepares the expiration time for the personal access token.
    2. Sends a PUT request to update the user's personal access token with the specified expiration time.
    3. Validates the response to ensure the update was successful.

    Args:
        client (TestClient): The test client used to make requests to the API.
        systemuser_token_headers (Dict[str, str]): The headers containing the system user's authentication token.

    Asserts:
        The response is not None.
        The response status code is 200 (OK).
        The response JSON is a string.
    """

    # ----------------------------------------------
    # UPDATE USER ME: PREPARATION
    # ----------------------------------------------

    t_expiration_in_minutes = 1

    # ----------------------------------------------
    # GET USER ME: METHODS TO TEST
    # ----------------------------------------------

    response = client.put(
        PUT_USER_ME_PERSONAL_ACCESS_TOKEN_API,
        headers=systemuser_token_headers,
        params={"expires_in_minutes": t_expiration_in_minutes},
    )

    # ----------------------------------------------
    # GET OWN USER: VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 200
    assert isinstance(response.json(), str)


def test_update_user_personal_access_token__guest_user(
    client: TestClient, guest_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test the update of a personal access token for a guest user.

    This test verifies that a guest user is not allowed to update their personal access token.
    It sends a PUT request to the API endpoint responsible for updating the user's personal access token
    and checks that the response status code is 403 Forbidden, indicating that the guest user does not
    have permission to perform this action.

    Args:
        client (TestClient): The test client used to make requests to the API.
        guest_user_token_headers (Dict[str, str]): The headers containing the guest user's token.
        db (Session): The database session used to retrieve the test guest user.

    Assertions:
        - The response is not None.
        - The response status code is 403 Forbidden.
        - The response JSON contains the expected error detail indicating that the guest user does not have permission.
    """

    # ----------------------------------------------
    # UPDATE USER ME: PREPARATION
    # ----------------------------------------------

    t_guest_user = get_test_guest_user(db)
    t_expiration_in_minutes = 1

    # ----------------------------------------------
    # GET USER ME: METHODS TO TEST
    # ----------------------------------------------

    response = client.put(
        PUT_USER_ME_PERSONAL_ACCESS_TOKEN_API,
        headers=guest_user_token_headers,
        params={"expires_in_minutes": t_expiration_in_minutes},
    )

    # ----------------------------------------------
    # GET OWN USER: VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 403
    assert response.json()["detail"] == lang(t_guest_user).API.USER.TOKEN_GUEST_NO_PERMISSION
