"""
    TEST WEB API -- USERS -- UPDATE USER ME
"""

from typing import Dict

from api.schemas.user import UserSchema
from config import cfg
from const import SYSTEM_USER
from fastapi.testclient import TestClient
from locales import lang
from sqlalchemy.orm import Session

from tests.utils.user import TEST_ADMIN_MAIL
from tests.utils.user import TEST_GUEST_MAIL
from tests.utils.user import TEST_SUPER_MAIL
from tests.utils.user import TEST_USER_MAIL
from tests.utils.user import TEST_USER_RFID
from tests.utils.user import get_test_admin_user
from tests.utils.user import get_test_guest_user
from tests.utils.user import get_test_super_user
from tests.utils.user import get_test_user

UPDATE_USER_ME_API = f"{cfg.server.api.web}/users/me"


def test_update_user_me__unauthorized(client: TestClient) -> None:
    """
    Test the 'update user me' endpoint for unauthorized access.
    This test verifies that an unauthorized user (i.e., a user without
    proper authentication headers) cannot update their own user information.

    Steps:
    1. Send a PUT request to the 'update user me' endpoint without any headers.
    2. Validate that the response status code is 401 (Unauthorized).

    Args:
        client (TestClient): The test client used to make HTTP requests.

    Asserts:
        - The response object is not None.
        - The response status code is 401.
    """

    # ----------------------------------------------
    # UPDATE USER ME: METHODS TO TEST
    # ----------------------------------------------

    response = client.put(UPDATE_USER_ME_API, headers={})

    # ----------------------------------------------
    # GET OWN USER: VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid access token"


def test_update_user_me__normal_user(
    client: TestClient, normal_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test the 'update user me' endpoint for a normal user.
    This test performs the following steps:

    1. Preparation:
       - Retrieve a test user from the database.
       - Prepare the data payload with user details to update.
    2. Methods to Test:
       - Send a PUT request to the 'update user me' API endpoint with the prepared data and headers.
    3. Validation:
       - Assert that the response is received and the status code is 200.
       - Validate the response schema to ensure the user attributes are updated correctly:
         - `is_active` should remain True.
         - `is_superuser`, `is_adminuser`, `is_systemuser`, and `is_guestuser` should be False.
         - The email should match the test user's email.

    Args:
        client (TestClient): The test client to simulate API requests.
        normal_user_token_headers (Dict[str, str]): The headers containing the normal user's authentication token.
        db (Session): The database session for accessing the test user.
    """

    # ----------------------------------------------
    # UPDATE USER ME: PREPARATION
    # ----------------------------------------------

    t_user = get_test_user(db)
    data = {
        "email": t_user.email,
        "username": t_user.username,
        "full_name": t_user.full_name,
        "is_active": False,
        "is_superuser": True,
        "is_adminuser": True,
        "is_guestuser": True,
        "is_systemuser": True,
    }

    # ----------------------------------------------
    # UPDATE USER ME: METHODS TO TEST
    # ----------------------------------------------

    response = client.put(UPDATE_USER_ME_API, headers=normal_user_token_headers, json=data)
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


def test_update_user_me__super_user(client: TestClient, super_user_token_headers: Dict[str, str], db: Session) -> None:
    """
    Test the update of the current super user.
    This test verifies that a super user can update their own user information
    and that the changes are correctly applied and validated.

    Steps:
        1. Prepare the test data for updating the super user.
        2. Send a PUT request to update the super user information.
        3. Validate the response to ensure the update was successful and the data is correct.

    Args:
        client (TestClient): The test client to simulate API requests.
        super_user_token_headers (Dict[str, str]): The headers containing the super user token.
        db (Session): The database session for accessing the database.

    Assertions:
        - The response is not None.
        - The response status code is 200.
        - The response schema is correctly populated.
        - The user attributes are correctly updated and validated.
    """

    # ----------------------------------------------
    # UPDATE USER ME: PREPARATION
    # ----------------------------------------------

    t_user = get_test_super_user(db)
    data = {
        "email": t_user.email,
        "username": t_user.username,
        "full_name": t_user.full_name,
        "is_active": False,
        "is_superuser": False,
        "is_adminuser": True,
        "is_guestuser": True,
        "is_systemuser": True,
    }

    # ----------------------------------------------
    # UPDATE USER ME: METHODS TO TEST
    # ----------------------------------------------

    response = client.put(UPDATE_USER_ME_API, headers=super_user_token_headers, json=data)
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


def test_update_user_me__admin_user(client: TestClient, admin_user_token_headers: Dict[str, str], db: Session) -> None:
    """
    Test the 'update user me' endpoint for an admin user.
    This test verifies that an admin user can update their own user information
    and that the response contains the expected data.

    Steps:
        1. Prepare the test data for updating the admin user's information.
        2. Send a PUT request to the 'update user me' endpoint with the prepared data.
        3. Validate the response to ensure the update was successful and the returned data is correct.

    Args:
        client (TestClient): The test client to simulate API requests.
        admin_user_token_headers (Dict[str, str]): The headers containing the admin user's authentication token.
        db (Session): The database session for accessing the database.

    Assertions:
        - The response is not None.
        - The response status code is 200.
        - The response schema is valid.
        - The response schema contains the expected values for user attributes.
    """

    # ----------------------------------------------
    # UPDATE USER ME: PREPARATION
    # ----------------------------------------------

    t_user = get_test_admin_user(db)
    data = {
        "email": t_user.email,
        "username": t_user.username,
        "full_name": t_user.full_name,
        "is_active": False,
        "is_superuser": False,
        "is_adminuser": False,
        "is_guestuser": True,
        "is_systemuser": True,
    }

    # ----------------------------------------------
    # UPDATE USER ME: METHODS TO TEST
    # ----------------------------------------------

    response = client.put(UPDATE_USER_ME_API, headers=admin_user_token_headers, json=data)
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


def test_update_user_me__guest_user(client: TestClient, guest_user_token_headers: Dict[str, str], db: Session) -> None:
    """
    Test the update of the current user's information for a guest user.
    This test performs the following steps:

    1. Preparation: Retrieves a test guest user and prepares the data for updating the user.
    2. Methods to Test: Sends a PUT request to update the user's information.
    3. Validation: Asserts the response status and validates the updated user information.

    Args:
        client (TestClient): The test client to simulate API requests.
        guest_user_token_headers (Dict[str, str]): The headers containing the guest user's authentication token.
        db (Session): The database session for accessing the test database.

    Asserts:
        The response status code is 200.
        The response schema is valid.
        The user's active status is True.
        The user's superuser status is False.
        The user's admin user status is False.
        The user's system user status is False.
        The user's guest user status is True.
        The user's email matches the test guest email.
    """

    # ----------------------------------------------
    # UPDATE USER ME: PREPARATION
    # ----------------------------------------------

    t_user = get_test_guest_user(db)
    data = {
        "email": t_user.email,
        "username": t_user.username,
        "full_name": t_user.full_name,
        "is_active": False,
        "is_superuser": True,
        "is_adminuser": True,
        "is_guestuser": True,
        "is_systemuser": True,
    }

    # ----------------------------------------------
    # UPDATE USER ME: METHODS TO TEST
    # ----------------------------------------------

    response = client.put(UPDATE_USER_ME_API, headers=guest_user_token_headers, json=data)
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


def test_update_user_me__system_user(client: TestClient, systemuser_token_headers: Dict[str, str]) -> None:
    """
    Test the 'update user me' endpoint for a system user.
    This test verifies that the system user can update their own user information
    and that the response contains the expected updated user attributes.

    Steps:
        1. Prepare the data for updating the user information.
        2. Send a PUT request to the 'update user me' endpoint with the prepared data.
        3. Validate the response status code and the updated user attributes.

    Args:
        client (TestClient): The test client to simulate API requests.
        systemuser_token_headers (Dict[str, str]): The headers containing the system user's authentication token.

    Assertions:
        - The response is not None.
        - The response status code is 200.
        - The response schema is valid.
        - The user attributes in the response match the expected values.
    """

    # ----------------------------------------------
    # UPDATE USER ME: PREPARATION
    # ----------------------------------------------

    data = {
        "email": cfg.init.mail,
        "username": SYSTEM_USER,
        "full_name": cfg.init.full_name,
        "is_active": False,
        "is_superuser": False,
        "is_adminuser": False,
        "is_guestuser": True,
        "is_systemuser": False,
    }

    # ----------------------------------------------
    # UPDATE USER ME: METHODS TO TEST
    # ----------------------------------------------

    response = client.put(UPDATE_USER_ME_API, headers=systemuser_token_headers, json=data)
    response_schema = UserSchema(**response.json())

    # ----------------------------------------------
    # UPDATE USER ME: VALIDATION
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


def test_update_user_me__normal_user__password_criteria(
    client: TestClient, normal_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test the update user endpoint for a normal user with respect to password criteria.
    This test verifies that:
    1. A user can successfully update their information without changing the password.
    2. An attempt to update the user information with an invalid password (less than 8 characters) fails.

    Args:
        client (TestClient): The test client to simulate API requests.
        normal_user_token_headers (Dict[str, str]): The headers containing the normal user's authentication token.
        db (Session): The database session.

    Assertions:
        - The response for a successful update request has a status code of 200.
        - The response for an unsuccessful update request due to invalid password has a status code of 422.
        - The error message for the unsuccessful update request indicates that the password should have at least 8 characters.
    """

    # ----------------------------------------------
    # UPDATE USER ME: PREPARATION
    # ----------------------------------------------

    t_user = get_test_user(db)
    successful_data = {
        "email": t_user.email,
        "username": t_user.username,
    }
    unsuccessful_data = {
        "email": t_user.email,
        "username": t_user.username,
        "password": "1234567",
    }

    # ----------------------------------------------
    # UPDATE USER ME: METHODS TO TEST
    # ----------------------------------------------

    successful_response = client.put(UPDATE_USER_ME_API, headers=normal_user_token_headers, json=successful_data)
    unsuccessful_response = client.put(UPDATE_USER_ME_API, headers=normal_user_token_headers, json=unsuccessful_data)

    # ----------------------------------------------
    # GET OWN USER: VALIDATION
    # ----------------------------------------------

    assert successful_response
    assert successful_response.status_code == 200

    # Currently the PasswordCriteriaError will never occur, because pydantic validates the wrong input before it reaches
    # the endpoints function. Maybe change this behavior in the future
    assert unsuccessful_response
    assert unsuccessful_response.status_code == 422
    assert unsuccessful_response.json()["detail"][0]["msg"] == "String should have at least 8 characters"


def test_update_user_me__normal_user__username_exists(
    client: TestClient, normal_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test the update user endpoint for a normal user when the username already exists.
    This test verifies that a normal user can successfully update their own user information
    when the username is unique, and receives an appropriate error response when the username
    is already in use by another user.

    Steps:
        1. Prepare test data for a normal user and an admin user.
        2. Define the payload for a successful update (unique username) and an unsuccessful update (existing username).
        3. Send PUT requests to update the user information with both payloads.
        4. Validate that the successful update returns a 200 status code.
        5. Validate that the unsuccessful update returns a 406 status code and the appropriate error message.

    Args:
        client (TestClient): The test client to simulate API requests.
        normal_user_token_headers (Dict[str, str]): The authentication headers for a normal user.
        db (Session): The database session for accessing test data.

    Asserts:
        - The successful response is not None and has a status code of 200.
        - The unsuccessful response is not None, has a status code of 406, and contains the expected error message.
    """

    # ----------------------------------------------
    # UPDATE USER ME: PREPARATION
    # ----------------------------------------------

    t_user = get_test_user(db)
    t_admin_user = get_test_admin_user(db)

    successful_data = {
        "email": t_user.email,
        "username": t_user.username,
    }
    unsuccessful_data = {
        "email": t_user.email,
        "username": t_admin_user.username,
    }

    # ----------------------------------------------
    # UPDATE USER ME: METHODS TO TEST
    # ----------------------------------------------

    successful_response = client.put(UPDATE_USER_ME_API, headers=normal_user_token_headers, json=successful_data)
    unsuccessful_response = client.put(UPDATE_USER_ME_API, headers=normal_user_token_headers, json=unsuccessful_data)

    # ----------------------------------------------
    # GET OWN USER: VALIDATION
    # ----------------------------------------------

    assert successful_response
    assert successful_response.status_code == 200

    assert unsuccessful_response
    assert unsuccessful_response.status_code == 406
    assert unsuccessful_response.json()["detail"] == lang(t_user).API.USER.USERNAME_IN_USE


def test_update_user_me__normal_user__email_exists(
    client: TestClient, normal_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test the 'update user me' endpoint for a normal user when the email already exists.
    This test verifies the behavior of the 'update user me' endpoint when a normal user
    attempts to update their email to one that already exists in the system.

    Steps:
        1. Prepare test data for a normal user and an admin user.
        2. Define successful and unsuccessful update data.
        3. Send a PUT request to update the user's email with valid data.
        4. Send a PUT request to update the user's email with an email that already exists.
        5. Validate the responses:
            - The successful update should return a 200 status code.
            - The unsuccessful update should return a 406 status code with an appropriate error message.
    Args:
        client (TestClient): The test client to simulate API requests.
        normal_user_token_headers (Dict[str, str]): The headers containing the normal user's authentication token.
        db (Session): The database session for accessing the database.

    Asserts:
        - The successful response is not None and has a status code of 200.
        - The unsuccessful response is not None, has a status code of 406, and contains the expected error message.
    """

    # ----------------------------------------------
    # UPDATE USER ME: PREPARATION
    # ----------------------------------------------

    t_user = get_test_user(db)
    t_admin_user = get_test_admin_user(db)

    successful_data = {
        "email": t_user.email,
        "username": t_user.username,
    }
    unsuccessful_data = {
        "email": t_admin_user.email,
        "username": t_user.username,
    }

    # ----------------------------------------------
    # UPDATE USER ME: METHODS TO TEST
    # ----------------------------------------------

    successful_response = client.put(UPDATE_USER_ME_API, headers=normal_user_token_headers, json=successful_data)
    unsuccessful_response = client.put(UPDATE_USER_ME_API, headers=normal_user_token_headers, json=unsuccessful_data)

    # ----------------------------------------------
    # GET OWN USER: VALIDATION
    # ----------------------------------------------

    assert successful_response
    assert successful_response.status_code == 200

    assert unsuccessful_response
    assert unsuccessful_response.status_code == 406
    assert unsuccessful_response.json()["detail"] == lang(t_user).API.USER.MAIL_IN_USE


def test_update_user_me__super_user__rfid_exists(
    client: TestClient, super_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test the update of the current super user's information when the RFID already exists.
    This test ensures that when a super user attempts to update their own information
    with an RFID that is already in use, the API responds with the appropriate error.

    Args:
        client (TestClient): The test client to simulate API requests.
        super_user_token_headers (Dict[str, str]): The headers containing the super user's authentication token.
        db (Session): The database session for accessing the test database.

    Assertions:
        - The response is not None.
        - The response status code is 406 (Not Acceptable).
        - The response JSON contains the detail message indicating the RFID is already in use.
    """

    # ----------------------------------------------
    # UPDATE USER ME: PREPARATION
    # ----------------------------------------------

    t_super_user = get_test_super_user(db)

    data = {
        "email": t_super_user.email,
        "username": t_super_user.username,
        "rfid": TEST_USER_RFID,
    }

    # ----------------------------------------------
    # UPDATE USER ME: METHODS TO TEST
    # ----------------------------------------------

    response = client.put(UPDATE_USER_ME_API, headers=super_user_token_headers, json=data)

    # ----------------------------------------------
    # GET OWN USER: VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 406
    assert response.json()["detail"] == lang(t_super_user).API.USER.RFID_IN_USE
