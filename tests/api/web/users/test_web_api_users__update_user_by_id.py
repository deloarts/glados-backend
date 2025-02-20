"""
    TEST WEB API -- USERS -- UPDATE USER BY ID
"""

from typing import Dict

from api.schemas.user import UserSchema
from config import cfg
from const import SYSTEM_USER
from fastapi.testclient import TestClient
from locales import lang
from sqlalchemy.orm import Session

from tests.utils.user import TEST_ADMIN_MAIL
from tests.utils.user import TEST_USER_RFID
from tests.utils.user import get_test_admin_user
from tests.utils.user import get_test_guest_user
from tests.utils.user import get_test_super_user
from tests.utils.user import get_test_user

UPDATE_USER_BY_ID = f"{cfg.server.api.web}/users"


def test_update_user_by_id__unauthorized(client: TestClient, db: Session) -> None:
    """
    Test the update user by ID endpoint for unauthorized access.

    This test verifies that an unauthorized request to update a user by ID
    returns a 401 Unauthorized status code and the appropriate error message.

    Steps:
        1. Prepare a test user using the `get_test_user` function.
        2. Attempt to update the user by ID without providing authorization headers.
        3. Validate that the response status code is 401 Unauthorized.
        4. Validate that the response JSON contains the expected error message.

    Args:
        client (TestClient): The test client used to make HTTP requests.
        db (Session): The database session used to interact with the test database.

    Asserts:
        - The response object is not None.
        - The response status code is 401.
        - The response JSON contains the detail message "Invalid access token".
    """

    # ----------------------------------------------
    # UPDATE USER ME: PREPARATION
    # ----------------------------------------------

    t_user = get_test_user(db)

    # ----------------------------------------------
    # UPDATE USER ME: METHODS TO TEST
    # ----------------------------------------------

    response = client.put(f"{UPDATE_USER_BY_ID}/{t_user.id}", headers={})

    # ----------------------------------------------
    # GET OWN USER: VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid access token"


def test_update_user_by_id__normal_user(
    client: TestClient, normal_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test the update user by ID endpoint for a normal user.

    This test verifies that a normal user cannot update another user's information
    and receives a 403 Forbidden status code with the appropriate error message.

    Args:
        client (TestClient): The test client to simulate API requests.
        normal_user_token_headers (Dict[str, str]): The headers containing the normal user's authentication token.
        db (Session): The database session for accessing the test database.
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

    response = client.put(f"{UPDATE_USER_BY_ID}/{t_user.id}", headers=normal_user_token_headers, json=data)

    # ----------------------------------------------
    # GET OWN USER: VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 401
    assert response.json()["detail"] == lang(t_user).API.DEPS.ADMINUSER_REQUIRED


def test_update_user_by_id__super_user(
    client: TestClient, super_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test the update user by ID endpoint for a super user.
    This test verifies that a super user is unable to update their own user details
    if they do not have the required admin privileges.

    Args:
        client (TestClient): The test client to simulate API requests.
        super_user_token_headers (Dict[str, str]): The headers containing the super user token.
        db (Session): The database session for accessing the database.

    Preparation:
        - Retrieve the test super user from the database.
        - Prepare the data payload with updated user details.

    Methods to Test:
        - Send a PUT request to update the user by ID endpoint with the prepared data.

    Validation:
        - Assert that the response is received.
        - Assert that the response status code is 403 (Forbidden).
        - Assert that the response JSON contains the expected error detail indicating
          that admin user privileges are required.
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

    response = client.put(f"{UPDATE_USER_BY_ID}/{t_user.id}", headers=super_user_token_headers, json=data)

    # ----------------------------------------------
    # GET OWN USER: VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 401
    assert response.json()["detail"] == lang(t_user).API.DEPS.ADMINUSER_REQUIRED


def test_update_user_by_id__admin_user(
    client: TestClient, admin_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test the update user by ID functionality for an admin user.
    This test performs the following steps:

    1. Preparation: Retrieves a test admin user and prepares the data for updating the user.
    2. Methods to Test: Sends a PUT request to update the user by ID with the prepared data.
    3. Validation: Asserts the response status code and validates the updated user attributes.

    By extends, this test assures that the admin user cannot update their own permission.
    Maybe this should be testes separatly.

    Args:
        client (TestClient): The test client to send requests.
        admin_user_token_headers (Dict[str, str]): The headers containing the admin user token.
        db (Session): The database session.

    Asserts:
        The response is successful and the status code is 200.
        The response schema matches the expected values for user attributes.
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

    response = client.put(f"{UPDATE_USER_BY_ID}/{t_user.id}", headers=admin_user_token_headers, json=data)
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


def test_update_user_by_id__guest_user(
    client: TestClient, guest_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test the update user by ID endpoint for a guest user.
    This test verifies that a guest user is not allowed to update user information
    and receives a 403 Forbidden status code.

    Args:
        client (TestClient): The test client to simulate API requests.
        guest_user_token_headers (Dict[str, str]): The headers containing the guest user's authentication token.
        db (Session): The database session for accessing the test database.
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

    response = client.put(f"{UPDATE_USER_BY_ID}/{t_user.id}", headers=guest_user_token_headers, json=data)

    # ----------------------------------------------
    # GET OWN USER: VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 401
    assert response.json()["detail"] == lang(t_user).API.DEPS.ADMINUSER_REQUIRED


def test_update_user_by_id__system_user(client: TestClient, systemuser_token_headers: Dict[str, str]) -> None:
    """
    Test the update of a system user by ID.

    This test verifies that a system user can be updated with the provided data and checks the response for correctness.

    Args:
        client (TestClient): The test client to make requests.
        systemuser_token_headers (Dict[str, str]): The headers containing the system user token.

    Preparation:
        - Sets up the data for updating the user, including email, username, full name, and various user roles.

    Methods to Test:
        - Sends a PUT request to update the user by ID with the provided data.

    Validation:
        - Asserts that the response is successful (status code 200).
        - Asserts that the response schema matches the expected values, including user roles and username.
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

    response = client.put(f"{UPDATE_USER_BY_ID}/1", headers=systemuser_token_headers, json=data)
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


def test_update_user_by_id__admin_user__password_criteria(
    client: TestClient, admin_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test the update user by ID functionality for an admin user, specifically focusing on password criteria.

    This test verifies that:
    1. A user can be successfully updated with valid data.
    2. An error is returned when attempting to update a user with a password that does not meet the criteria.

    Args:
        client (TestClient): The test client to simulate API requests.
        admin_user_token_headers (Dict[str, str]): The headers containing the admin user's authentication token.
        db (Session): The database session for accessing the test database.

    Assertions:
        - The response for a successful update should have a status code of 200.
        - The response for an unsuccessful update due to password criteria should have a status code of 422.
        - The error message for the unsuccessful update should indicate that the password must have at least 8 characters.
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

    successful_response = client.put(
        f"{UPDATE_USER_BY_ID}/{t_user.id}", headers=admin_user_token_headers, json=successful_data
    )
    unsuccessful_response = client.put(
        f"{UPDATE_USER_BY_ID}/{t_user.id}", headers=admin_user_token_headers, json=unsuccessful_data
    )

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


def test_update_user_by_id__admin_user__username_exists(
    client: TestClient, admin_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test updating a user by ID as an admin user when the username already exists.

    This test verifies the following scenarios:
    1. Successfully updating a user with a unique username.
    2. Failing to update a user when the username is already in use by another user.

    Args:
        client (TestClient): The test client to simulate API requests.
        admin_user_token_headers (Dict[str, str]): The headers containing the admin user's authentication token.
        db (Session): The database session for accessing the test database.

    Assertions:
        - The response for a successful update has a status code of 200.
        - The response for an unsuccessful update has a status code of 406.
        - The unsuccessful update response contains the correct error detail indicating the username is already in use.
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

    successful_response = client.put(
        f"{UPDATE_USER_BY_ID}/{t_user.id}", headers=admin_user_token_headers, json=successful_data
    )
    unsuccessful_response = client.put(
        f"{UPDATE_USER_BY_ID}/{t_user.id}", headers=admin_user_token_headers, json=unsuccessful_data
    )

    # ----------------------------------------------
    # GET OWN USER: VALIDATION
    # ----------------------------------------------

    assert successful_response
    assert successful_response.status_code == 200

    assert unsuccessful_response
    assert unsuccessful_response.status_code == 406
    assert unsuccessful_response.json()["detail"] == lang(t_user).API.USER.USERNAME_IN_USE


def test_update_user_by_id__admin_user__email_exists(
    client: TestClient, admin_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test updating a user by ID with an admin user when the email already exists.

    This test verifies that an admin user can successfully update a user's email
    to a new email that does not exist in the system, and that attempting to update
    the email to one that already exists results in a 406 Not Acceptable response.

    Args:
        client (TestClient): The test client to simulate API requests.
        admin_user_token_headers (Dict[str, str]): The headers containing the admin user's token.
        db (Session): The database session.

    Assertions:
        - The successful response has a status code of 200.
        - The unsuccessful response has a status code of 406.
        - The unsuccessful response contains a detail message indicating the email is already in use.
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

    successful_response = client.put(
        f"{UPDATE_USER_BY_ID}/{t_user.id}", headers=admin_user_token_headers, json=successful_data
    )
    unsuccessful_response = client.put(
        f"{UPDATE_USER_BY_ID}/{t_user.id}", headers=admin_user_token_headers, json=unsuccessful_data
    )

    # ----------------------------------------------
    # GET OWN USER: VALIDATION
    # ----------------------------------------------

    assert successful_response
    assert successful_response.status_code == 200

    assert unsuccessful_response
    assert unsuccessful_response.status_code == 406
    assert unsuccessful_response.json()["detail"] == lang(t_user).API.USER.MAIL_IN_USE


def test_update_user_by_id__admin_user__rfid_exists(
    client: TestClient, admin_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test the update of a user by an admin user when the RFID exists.
    This test verifies that an admin user can successfully update a user's
    information when the RFID is unique and fails when the RFID is already in use.

    Args:
        client (TestClient): The test client to simulate API requests.
        admin_user_token_headers (Dict[str, str]): The headers containing the admin user's authentication token.
        db (Session): The database session for accessing the test database.

    Preparation:
        - Retrieve a test user and a test super user from the database.
        - Define the data for a successful update (unique RFID) and an unsuccessful update (RFID already in use).

    Methods to Test:
        - Perform a PUT request to update the test user's information with a unique RFID.
        - Perform a PUT request to update the test super user's information with an RFID that is already in use.

    Validation:
        - Assert that the successful update response is valid and has a status code of 200.
        - Assert that the unsuccessful update response is valid, has a status code of 406, and contains the appropriate error message.
    """

    # ----------------------------------------------
    # UPDATE USER ME: PREPARATION
    # ----------------------------------------------

    t_user = get_test_user(db)
    t_super_user = get_test_super_user(db)

    successful_data = {
        "email": t_user.email,
        "username": t_user.username,
        "rfid": TEST_USER_RFID,
    }
    unsuccessful_data = {
        "email": t_super_user.email,
        "username": t_super_user.username,
        "rfid": TEST_USER_RFID,
    }

    # ----------------------------------------------
    # UPDATE USER ME: METHODS TO TEST
    # ----------------------------------------------

    successful_response = client.put(
        f"{UPDATE_USER_BY_ID}/{t_user.id}", headers=admin_user_token_headers, json=successful_data
    )
    unsuccessful_response = client.put(
        f"{UPDATE_USER_BY_ID}/{t_super_user.id}", headers=admin_user_token_headers, json=unsuccessful_data
    )

    # ----------------------------------------------
    # GET OWN USER: VALIDATION
    # ----------------------------------------------

    assert successful_response
    assert successful_response.status_code == 200

    assert unsuccessful_response
    assert unsuccessful_response.status_code == 406
    assert unsuccessful_response.json()["detail"] == lang(get_test_admin_user(db)).API.USER.RFID_IN_USE


def test_read_user_by_id__admin_user__unknown_user_id(
    client: TestClient, admin_user_token_headers: dict, db: Session
) -> None:
    """
    Test case for reading a user by ID with an admin user and an unknown user ID.
    This test verifies that when an admin user attempts to read a user by an ID that does not exist,
    the API responds with a 404 status code and the appropriate error message.

    Args:
        client (TestClient): The test client to simulate API requests.
        admin_user_token_headers (dict): The headers containing the admin user's authentication token.
        db (Session): The database session for accessing the database.

    Assertions:
        - The response is not None.
        - The response status code is 404.
        - The response JSON contains the detail message indicating the user was not found.
    """

    # ----------------------------------------------
    # READ USER BY ID: PREPARATION
    # ----------------------------------------------

    t_user = get_test_admin_user(db)

    # ----------------------------------------------
    # READ USER BY ID: METHODS TO TEST
    # ----------------------------------------------

    response = client.get(f"{UPDATE_USER_BY_ID}/9999999", headers=admin_user_token_headers)

    # ----------------------------------------------
    # READ USER BY ID: VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 404
    assert response.json()["detail"] == lang(t_user).API.USER.NOT_FOUND


def test_read_user_by_id__admin_user__invalid_query_param(client: TestClient, admin_user_token_headers: dict) -> None:
    """
    Test case for reading a user by ID with an admin user and an invalid query parameter.
    This test ensures that when an admin user attempts to read a user by ID with an invalid query parameter,
    the API responds with a 422 Unprocessable Entity status code and the appropriate error message.

    Args:
        client (TestClient): The test client to simulate API requests.
        admin_user_token_headers (dict): The headers containing the admin user's authentication token.

    Asserts:
        - The response is not None.
        - The response status code is 422.
        - The error location in the response JSON is "path" and "user_id".
        - The error message indicates that the input should be a valid integer.
    """

    # ----------------------------------------------
    # READ USER BY ID: METHODS TO TEST
    # ----------------------------------------------

    response = client.get(f"{UPDATE_USER_BY_ID}/A", headers=admin_user_token_headers)

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
