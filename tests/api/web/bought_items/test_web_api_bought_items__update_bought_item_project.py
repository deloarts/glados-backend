"""
    TEST WEB API -- BOUGHT ITEMS -- UPDATE PROJECT
"""

from string import Template
from typing import Dict

from api.schemas.bought_item import BoughtItemSchema
from config import cfg
from crud.bought_item import crud_bought_item
from crud.project import crud_project
from fastapi.testclient import TestClient
from locales import lang
from sqlalchemy.orm import Session

from tests.utils.bought_item import create_random_item
from tests.utils.project import create_random_project
from tests.utils.user import get_test_guest_user
from tests.utils.user import get_test_super_user
from tests.utils.user import get_test_user

UPDATE_ITEM_PROJECT = Template(f"{cfg.server.api.web}/items/bought/$item_id/project")


def test_update_item_project__unauthorized(client: TestClient, db: Session) -> None:
    """
    Test the unauthorized update of an item project.

    This test ensures that an unauthorized request to update an item project
    returns a 401 status code with an appropriate error message.

    Args:
        client (TestClient): The test client used to make the request.
        db (Session): The database session used to create a random item.

    Steps:
        1. Create a random item in the database.
        2. Attempt to update the item project without authorization.
        3. Validate that the response status code is 401.
        4. Validate that the response contains the expected error message.

    Asserts:
        - The response is not None.
        - The response status code is 401.
        - The response JSON contains the detail "Invalid access token".
    """
    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_item = create_random_item(db)

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.put(UPDATE_ITEM_PROJECT.substitute(item_id=t_item.id), headers={})

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid access token"


def test_update_item_project__normal_user(
    client: TestClient, normal_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test the update of an item's project by a normal user.

    This test performs the following steps:
    1. Preparation:
        - Create a random project.
        - Create a random item.
        - Ensure the item is not part of the project's bought items.
    2. Methods to Test:
        - Send a PUT request to update the item's project using the normal user's token headers.
        - Parse the response into a BoughtItemSchema.
    3. Validation:
        - Assert the response is successful (status code 200).
        - Assert the response schema matches the expected item and project details.

    Args:
        client (TestClient): The test client to simulate API requests.
        normal_user_token_headers (Dict[str, str]): The headers containing the normal user's authentication token.
        db (Session): The database session for accessing and manipulating the database.
    """
    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_project = create_random_project(db)
    t_item = create_random_item(db)
    assert t_item not in t_project.bought_items

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.put(
        UPDATE_ITEM_PROJECT.substitute(item_id=t_item.id),
        headers=normal_user_token_headers,
        params={"project_number": t_project.number},
    )
    responseScheme = BoughtItemSchema(**response.json())

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 200

    assert responseScheme
    assert responseScheme.id == t_item.id
    assert responseScheme.project_id == t_project.id
    assert responseScheme.project_number == t_project.number


def test_update_item_project__normal_user__not_found(
    client: TestClient, normal_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test updating an item project with a normal user when the item is not found.

    This test ensures that when a normal user attempts to update a project for an item
    that does not exist, the API responds with a 404 Not Found status code and the
    appropriate error message.

    Args:
        client (TestClient): The test client to simulate API requests.
        normal_user_token_headers (Dict[str, str]): The headers containing the normal user's authentication token.
        db (Session): The database session.

    Asserts:
        The response is not None.
        The response status code is 404.
        The response JSON contains the detail message indicating the item was not found.
    """

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.put(
        UPDATE_ITEM_PROJECT.substitute(item_id=9999999),
        headers=normal_user_token_headers,
        params={"project_number": "an_unknown_project"},
    )

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 404
    assert response.json()["detail"] == lang(get_test_user(db)).API.BOUGHTITEM.ITEM_NOT_FOUND


def test_update_item_project__normal_user__invalid_id(
    client: TestClient, normal_user_token_headers: Dict[str, str]
) -> None:
    """
    Test updating an item project with an invalid item ID by a normal user.
    This test verifies that when a normal user attempts to update an item project
    with an invalid item ID (non-integer), the API responds with a 422 Unprocessable Entity
    status code and the appropriate error message indicating that the item ID should be a valid integer.

    Args:
        client (TestClient): The test client to simulate API requests.
        normal_user_token_headers (Dict[str, str]): The headers containing the normal user's authentication token.

    Asserts:
        - The response is not None.
        - The response status code is 422.
        - The error location in the response JSON is "path" and "item_id".
        - The error message indicates that the item ID should be a valid integer.
    """
    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.put(
        UPDATE_ITEM_PROJECT.substitute(item_id="A"),
        headers=normal_user_token_headers,
        params={"project_number": "an_unknown_project"},
    )

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"][0] == "path"
    assert response.json()["detail"][0]["loc"][1] == "item_id"
    assert (
        response.json()["detail"][0]["msg"] == "Input should be a valid integer, unable to parse string as an integer"
    )


def test_update_item_project__normal_user__unknown_project(
    client: TestClient, normal_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test updating an item project with a normal user when the project is unknown.
    This test verifies that when a normal user attempts to update an item project
    with a project number that does not exist, the API responds with a 404 status code
    and the appropriate error message.

    Args:
        client (TestClient): The test client to simulate API requests.
        normal_user_token_headers (Dict[str, str]): The headers containing the normal user's authentication token.
        db (Session): The database session for accessing the database.

    Assertions:
        - The response is not None.
        - The response status code is 404.
        - The response JSON contains the detail message indicating the project was not found.
    """

    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_item = create_random_item(db)

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.put(
        UPDATE_ITEM_PROJECT.substitute(item_id=t_item.id),
        headers=normal_user_token_headers,
        params={"project_number": "an_unknown_project"},
    )

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 404
    assert response.json()["detail"] == lang(get_test_user(db)).API.BOUGHTITEM.PROJECT_NOT_FOUND


def test_update_item_project__normal_user__inactive_project(
    client: TestClient, normal_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test case for updating an item project by a normal user when the project is inactive.
    This test verifies that a normal user cannot update an item project if the project is inactive.
    It performs the following steps:
    1. Preparation:
        - Retrieves a test user.
        - Creates a random item.
        - Creates a random project and sets it to inactive.
    2. Methods to Test:
        - Attempts to update the item project using the PUT method.
    3. Validation:
        - Asserts that the response status code is 403 (Forbidden).
        - Asserts that the response contains the appropriate error message indicating the project is inactive.
    Args:
        client (TestClient): The test client to simulate API requests.
        normal_user_token_headers (Dict[str, str]): The headers containing the normal user's authentication token.
        db (Session): The database session for accessing the database.
    """
    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_user = get_test_user(db)
    t_item = create_random_item(db)

    t_project = create_random_project(db)
    crud_project.update(
        db,
        db_obj_user=t_user,
        db_obj=t_project,
        obj_in={"is_active": False, "designated_user_id": t_user.id},
    )

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.put(
        UPDATE_ITEM_PROJECT.substitute(item_id=t_item.id),
        headers=normal_user_token_headers,
        params={"project_number": t_project.number},
    )

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 403
    assert response.json()["detail"] == lang(get_test_user(db)).API.BOUGHTITEM.PROJECT_INACTIVE


def test_update_item_project__super_user__inactive_project(
    client: TestClient, super_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test the update of an item's project by a super user when the project is inactive.
    This test performs the following steps:

    1. Preparation:
        - Retrieve a test user from the database.
        - Create a random item.
        - Create a random project and set it to inactive, assigning it to the test user.
    2. Methods to Test:
        - Attempt to update the item's project using a PUT request with the super user token headers.
    3. Validation:
        - Assert that the response is received.
        - Assert that the status code of the response is 403 (Forbidden).
        - Assert that the response JSON contains the expected detail message indicating the project is inactive.

    Args:
        client (TestClient): The test client to perform HTTP requests.
        super_user_token_headers (Dict[str, str]): The headers containing the super user token.
        db (Session): The database session.
    """
    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_user = get_test_user(db)
    t_item = create_random_item(db)

    t_project = create_random_project(db)
    crud_project.update(
        db,
        db_obj_user=t_user,
        db_obj=t_project,
        obj_in={"is_active": False, "designated_user_id": t_user.id},
    )

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.put(
        UPDATE_ITEM_PROJECT.substitute(item_id=t_item.id),
        headers=super_user_token_headers,
        params={"project_number": t_project.number},
    )

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 403
    assert response.json()["detail"] == lang(get_test_user(db)).API.BOUGHTITEM.PROJECT_INACTIVE


def test_update_item_project__admin_user__inactive_project(
    client: TestClient, admin_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test updating an item project by an admin user when the project is inactive.
    This test verifies that an admin user cannot update an item project if the project is inactive.
    It performs the following steps:
    1. Preparation:
        - Retrieve a test user from the database.
        - Create a random item.
        - Create a random project and set it to inactive with a designated user.
    2. Methods to Test:
        - Attempt to update the item project using a PUT request with the admin user's token headers and the inactive project's number.
    3. Validation:
        - Assert that the response is received.
        - Assert that the status code of the response is 403 (Forbidden).
        - Assert that the response JSON contains the expected error detail indicating the project is inactive.
    Args:
        client (TestClient): The test client to simulate API requests.
        admin_user_token_headers (Dict[str, str]): The headers containing the admin user's authentication token.
        db (Session): The database session for accessing the database.
    """

    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_user = get_test_user(db)
    t_item = create_random_item(db)

    t_project = create_random_project(db)
    crud_project.update(
        db,
        db_obj_user=t_user,
        db_obj=t_project,
        obj_in={"is_active": False, "designated_user_id": t_user.id},
    )

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.put(
        UPDATE_ITEM_PROJECT.substitute(item_id=t_item.id),
        headers=admin_user_token_headers,
        params={"project_number": t_project.number},
    )

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 403
    assert response.json()["detail"] == lang(get_test_user(db)).API.BOUGHTITEM.PROJECT_INACTIVE


def test_update_item_project__normal_user__already_planned(
    client: TestClient, normal_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test the update of an item project by a normal user when the item is already planned.
    This test verifies that a normal user cannot update the project of an item that has already been planned.
    It performs the following steps:
    1. Preparation:
        - Create a test user, project, and item.
        - Update the status of the item to 'ordered'.
        - Ensure the item is not part of the project's bought items.
    2. Methods to Test:
        - Attempt to update the item project using a PUT request.
    3. Validation:
        - Check that the response status code is 403 (Forbidden).
        - Verify that the response contains the appropriate error message indicating that a planned item cannot be changed.
    Args:
        client (TestClient): The test client to simulate API requests.
        normal_user_token_headers (Dict[str, str]): The headers containing the normal user's authentication token.
        db (Session): The database session for interacting with the test database.
    """
    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_user = get_test_user(db)
    t_project = create_random_project(db)
    t_item = create_random_item(db)
    crud_bought_item.update_status(db, db_obj_user=t_user, db_obj_item=t_item, status=cfg.items.bought.status.ordered)
    assert t_item not in t_project.bought_items

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.put(
        UPDATE_ITEM_PROJECT.substitute(item_id=t_item.id),
        headers=normal_user_token_headers,
        params={"project_number": t_project.number},
    )

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 403
    assert response.json()["detail"] == lang(get_test_user(db)).API.BOUGHTITEM.CANNOT_CHANGE_PLANNED_ITEM


def test_update_item_project__super_user__already_planned(
    client: TestClient, super_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test the update of an item's project by a super user when the item is already planned.
    This test performs the following steps:

    1. Preparation:
        - Retrieve a test user from the database.
        - Create a random project and item.
        - Update the status of the item to 'ordered'.
        - Ensure the item is not part of the project's bought items.
    2. Methods to Test:
        - Send a PUT request to update the item's project using the super user token headers.
        - Parse the response into a BoughtItemSchema.
    3. Validation:
        - Assert that the response is received and has a status code of 200.
        - Assert that the response schema is valid and the project ID matches the expected project ID.

    Args:
        client (TestClient): The test client to simulate API requests.
        super_user_token_headers (Dict[str, str]): Headers containing the super user token for authentication.
        db (Session): The database session for interacting with the database.
    """
    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_user = get_test_user(db)
    t_project = create_random_project(db)
    t_item = create_random_item(db)
    crud_bought_item.update_status(db, db_obj_user=t_user, db_obj_item=t_item, status=cfg.items.bought.status.ordered)
    assert t_item not in t_project.bought_items

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.put(
        UPDATE_ITEM_PROJECT.substitute(item_id=t_item.id),
        headers=super_user_token_headers,
        params={"project_number": t_project.number},
    )
    responseSchema = BoughtItemSchema(**response.json())

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 200

    assert responseSchema
    assert responseSchema.project_id == t_project.id


def test_update_item_project__admin_user__already_planned(
    client: TestClient, admin_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test the update of an item's project by an admin user when the item is already planned.
    This test performs the following steps:
    1. Preparation:
        - Retrieve a test user from the database.
        - Create a random project and item.
        - Update the status of the item to 'ordered'.
        - Ensure the item is not part of the project's bought items.
    2. Methods to Test:
        - Send a PUT request to update the item's project using the admin user's token.
        - Parse the response into a BoughtItemSchema.
    3. Validation:
        - Assert the response is valid and has a status code of 200.
        - Assert the response schema is valid and the project ID matches the expected project ID.
    Args:
        client (TestClient): The test client to simulate API requests.
        admin_user_token_headers (Dict[str, str]): The headers containing the admin user's authentication token.
        db (Session): The database session for interacting with the database.
    """
    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_user = get_test_user(db)
    t_project = create_random_project(db)
    t_item = create_random_item(db)
    crud_bought_item.update_status(db, db_obj_user=t_user, db_obj_item=t_item, status=cfg.items.bought.status.ordered)
    assert t_item not in t_project.bought_items

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.put(
        UPDATE_ITEM_PROJECT.substitute(item_id=t_item.id),
        headers=admin_user_token_headers,
        params={"project_number": t_project.number},
    )
    responseSchema = BoughtItemSchema(**response.json())

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 200

    assert responseSchema
    assert responseSchema.project_id == t_project.id


def test_update_item_project__normal_user__of_another_user(
    client: TestClient, normal_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test updating an item project with a normal user when the item belongs to another user.

    This test ensures that a normal user cannot update the project of an item that belongs to another user.
    It performs the following steps:
    1. Preparation:
        - Retrieve a test user and a super user from the database.
        - Create a random project.
        - Create a random item and assign it to the super user.
        - Ensure the item is not part of the project's bought items.
    2. Methods to Test:
        - Attempt to update the item project using a PUT request with the normal user's token headers.
    3. Validation:
        - Assert that the response status code is 403 (Forbidden).
        - Assert that the response JSON contains the appropriate error message indicating that the user cannot change another user's item.

    Args:
        client (TestClient): The test client to simulate API requests.
        normal_user_token_headers (Dict[str, str]): The headers containing the normal user's authentication token.
        db (Session): The database session for interacting with the test database.
    """
    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_user = get_test_user(db)
    t_project = create_random_project(db)
    t_super = get_test_super_user(db)
    t_item = create_random_item(db, user=t_super)
    assert t_item not in t_project.bought_items

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.put(
        UPDATE_ITEM_PROJECT.substitute(item_id=t_item.id),
        headers=normal_user_token_headers,
        params={"project_number": t_project.number},
    )

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 403
    assert response.json()["detail"] == lang(t_user).API.BOUGHTITEM.CANNOT_CHANGE_OTHER_USER_ITEM


def test_update_item_project__super_user__of_another_user(
    client: TestClient, super_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test the update of an item project by a super user on behalf of another user.

    This test performs the following steps:
    1. Preparation:
        - Create a random project.
        - Retrieve a test super user.
        - Create a random item associated with the super user.
        - Ensure the item is not part of the project's bought items.
    2. Methods to Test:
        - Send a PUT request to update the item's project using the super user's token headers.
        - Parse the response into a BoughtItemSchema.
    3. Validation:
        - Assert the response is successful (status code 200).
        - Assert the response schema is valid and the project ID matches the expected project ID.

    Args:
        client (TestClient): The test client to simulate API requests.
        super_user_token_headers (Dict[str, str]): Headers containing the super user's authentication token.
        db (Session): The database session for performing database operations.
    """
    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_project = create_random_project(db)
    t_user = get_test_user(db)
    t_item = create_random_item(db, user=t_user)
    assert t_item not in t_project.bought_items

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.put(
        UPDATE_ITEM_PROJECT.substitute(item_id=t_item.id),
        headers=super_user_token_headers,
        params={"project_number": t_project.number},
    )
    responseSchema = BoughtItemSchema(**response.json())

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 200

    assert responseSchema
    assert responseSchema.project_id == t_project.id


def test_update_item_project__admin_user__of_another_user(
    client: TestClient, admin_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test the update of an item's project by an admin user for another user's item.

    This test performs the following steps:
    1. Preparation:
        - Create a random project.
        - Retrieve a test super user.
        - Create a random item associated with the super user.
        - Ensure the item is not part of the project's bought items.
    2. Methods to Test:
        - Send a PUT request to update the item's project using the admin user's token.
        - Parse the response into a BoughtItemSchema.
    3. Validation:
        - Assert the response is successful (status code 200).
        - Assert the response schema is valid and the project ID matches the expected project.

    Args:
        client (TestClient): The test client to simulate API requests.
        admin_user_token_headers (Dict[str, str]): The headers containing the admin user's authentication token.
        db (Session): The database session for database operations.
    """
    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_project = create_random_project(db)
    t_user = get_test_user(db)
    t_item = create_random_item(db, user=t_user)
    assert t_item not in t_project.bought_items

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.put(
        UPDATE_ITEM_PROJECT.substitute(item_id=t_item.id),
        headers=admin_user_token_headers,
        params={"project_number": t_project.number},
    )
    responseSchema = BoughtItemSchema(**response.json())

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 200

    assert responseSchema
    assert responseSchema.project_id == t_project.id


def test_update_item_project__guest_user(
    client: TestClient, guest_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test the update of an item project by a guest user.

    This test ensures that a guest user does not have permission to update an item project.

    Args:
        client (TestClient): The test client to simulate API requests.
        guest_user_token_headers (Dict[str, str]): The headers containing the guest user's authentication token.
        db (Session): The database session for accessing the database.

    Steps:
        1. Create a random project and a random item.
        2. Ensure the item is not part of the project's bought items.
        3. Attempt to update the item project using the guest user's token.
        4. Validate that the response status code is 403 (Forbidden).
        5. Validate that the response detail message indicates no permission to update.

    Asserts:
        - The response is not None.
        - The response status code is 403.
        - The response JSON detail message matches the expected no permission message.
    """
    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_project = create_random_project(db)
    t_item = create_random_item(db)
    assert t_item not in t_project.bought_items

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.put(
        UPDATE_ITEM_PROJECT.substitute(item_id=t_item.id),
        headers=guest_user_token_headers,
        params={"project_number": t_project.number},
    )

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 403
    assert response.json()["detail"] == lang(get_test_guest_user(db)).API.BOUGHTITEM.UPDATE_NO_PERMISSION
