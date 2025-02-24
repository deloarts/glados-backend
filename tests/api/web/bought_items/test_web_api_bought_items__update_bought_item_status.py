"""
    TEST WEB API -- BOUGHT ITEMS -- UPDATE STATUS
"""

from string import Template
from typing import Dict

from api.schemas.bought_item import BoughtItemSchema
from config import cfg
from crud.bought_item import crud_bought_item
from fastapi.testclient import TestClient
from locales import lang
from sqlalchemy.orm import Session

from tests.utils.bought_item import create_random_item
from tests.utils.user import get_test_guest_user
from tests.utils.user import get_test_super_user
from tests.utils.user import get_test_user

UPDATE_ITEM_STATUS = Template(f"{cfg.server.api.web}/items/bought/$item_id/status")


def test_update_item_status__unauthorized(client: TestClient, db: Session) -> None:
    """
    Test the update item status endpoint for unauthorized access.

    This test verifies that an unauthorized user (without a valid access token)
    cannot update the status of an item. It ensures that the API returns a 401
    status code and the appropriate error message.

    Args:
        client (TestClient): The test client to simulate API requests.
        db (Session): The database session for creating test data.

    Steps:
        1. Create a random item in the database.
        2. Attempt to update the status of the created item without providing
           authorization headers.
        3. Validate that the response status code is 401 (Unauthorized).
        4. Validate that the response contains the expected error message.

    Asserts:
        - The response object is not None.
        - The response status code is 401.
        - The response JSON contains the detail message "Invalid access token".
    """

    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_item = create_random_item(db)

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.put(UPDATE_ITEM_STATUS.substitute(item_id=t_item.id), headers={})

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid access token"


def test_update_item_status__normal_user(
    client: TestClient, normal_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test the update of an item's status by a normal user.

    This test performs the following steps:
    1. Preparation: Create a random item in the database.
    2. Methods to Test: Send a PUT request to update the item's status.
    3. Validation: Verify the response and ensure the item's status is updated correctly.

    Args:
        client (TestClient): The test client to simulate API requests.
        normal_user_token_headers (Dict[str, str]): The headers containing the normal user's authentication token.
        db (Session): The database session.

    Asserts:
        The response is not None.
        The response status code is 200.
        The response schema is valid and matches the expected item ID and status.
    """

    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_item = create_random_item(db)

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.put(
        UPDATE_ITEM_STATUS.substitute(item_id=t_item.id),
        headers=normal_user_token_headers,
        params={"status": cfg.items.bought.status.ordered},
    )
    responseScheme = BoughtItemSchema(**response.json())

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 200

    assert responseScheme
    assert responseScheme.id == t_item.id
    assert responseScheme.status == cfg.items.bought.status.ordered


def test_update_item_status__normal_user__not_found(
    client: TestClient, normal_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test case for updating the status of a bought item by a normal user when the item is not found.

    This test verifies that when a normal user attempts to update the status of a non-existent bought item,
    the API responds with a 404 Not Found status code and the appropriate error message.

    Args:
        client (TestClient): The test client to simulate API requests.
        normal_user_token_headers (Dict[str, str]): The headers containing the normal user's authentication token.
        db (Session): The database session for accessing the database.

    Assertions:
        - The response is not None.
        - The response status code is 404.
        - The response JSON contains the expected error message indicating that the item was not found.
    """

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.put(
        UPDATE_ITEM_STATUS.substitute(item_id=9999999),
        headers=normal_user_token_headers,
        params={"status": cfg.items.bought.status.ordered},
    )

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 404
    assert response.json()["detail"] == lang(get_test_user(db)).API.BOUGHTITEM.ITEM_NOT_FOUND


def test_update_item_status__normal_user__invalid_id(
    client: TestClient, normal_user_token_headers: Dict[str, str]
) -> None:
    """
    Test updating item status with an invalid item ID for a normal user.
    This test verifies that when a normal user attempts to update the status of an item
    using an invalid item ID (non-integer), the API responds with a 422 Unprocessable Entity
    status code and the appropriate error message indicating that the item ID should be a valid integer.

    Args:
        client (TestClient): The test client to simulate API requests.
        normal_user_token_headers (Dict[str, str]): The headers containing the normal user's authentication token.

    Asserts:
        - The response object is not None.
        - The response status code is 422.
        - The error location in the response JSON is "path" and "item_id".
        - The error message indicates that the item ID should be a valid integer.
    """

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.put(
        UPDATE_ITEM_STATUS.substitute(item_id="A"),
        headers=normal_user_token_headers,
        params={"status": cfg.items.bought.status.ordered},
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


def test_update_item_status__normal_user__unknown_status(
    client: TestClient, normal_user_token_headers: Dict[str, str], db: Session
) -> None:
    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_item = create_random_item(db)

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.put(
        UPDATE_ITEM_STATUS.substitute(item_id=t_item.id),
        headers=normal_user_token_headers,
        params={"status": "an_unknown_status"},
    )

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"][0] == "query"
    assert response.json()["detail"][0]["loc"][1] == "status"


def test_update_item_status__normal_user__back_to_open(
    client: TestClient, normal_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test case for updating the status of a bought item by a normal user back to 'open'.

    This test verifies that a normal user is not allowed to change the status of a bought item
    back to 'open' and receives a 403 Forbidden response with the appropriate error message.

    Args:
        client (TestClient): The test client for making HTTP requests.
        normal_user_token_headers (Dict[str, str]): The authentication headers for a normal user.
        db (Session): The database session for accessing the database.

    Steps:
        1. Prepare the test data by creating a test user and a random item.
        2. Update the status of the item to 'requested' for the test user.
        3. Attempt to update the status of the item back to 'open' using the normal user's token.
        4. Validate that the response status code is 403 Forbidden.
        5. Validate that the response contains the appropriate error message indicating that the
           status cannot be changed to 'open' by a normal user.

    Asserts:
        - The response object is not None.
        - The response status code is 403 Forbidden.
        - The response JSON contains the expected error message.
    """

    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_user = get_test_user(db)
    t_item = create_random_item(db)
    crud_bought_item.update_status(db, db_obj_user=t_user, db_obj_item=t_item, status=cfg.items.bought.status.requested)

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.put(
        UPDATE_ITEM_STATUS.substitute(item_id=t_item.id),
        headers=normal_user_token_headers,
        params={"status": cfg.items.bought.status.open},
    )

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 403
    assert response.json()["detail"] == lang(t_user).API.BOUGHTITEM.CANNOT_CHANGE_TO_OPEN


def test_update_item_status__normal_user__of_another_user(
    client: TestClient, normal_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test the update item status endpoint for a normal user attempting to update
    the status of an item belonging to another user.

    This test ensures that a normal user cannot change the status of an item
    that belongs to another user and receives a 403 Forbidden response.

    Args:
        client (TestClient): The test client to simulate API requests.
        normal_user_token_headers (Dict[str, str]): The headers containing the
            normal user's authentication token.
        db (Session): The database session for accessing the database.

    Steps:
        1. Prepare test data by creating a test user, a test super user, and a
           random item associated with the super user.
        2. Attempt to update the status of the item using the normal user's
           token.
        3. Validate that the response status code is 403 Forbidden and the
           response detail message indicates that the user cannot change the
           status of another user's item.
    """

    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_user = get_test_user(db)
    t_super = get_test_super_user(db)
    t_item = create_random_item(db, user=t_super)

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.put(
        UPDATE_ITEM_STATUS.substitute(item_id=t_item.id),
        headers=normal_user_token_headers,
        params={"status": cfg.items.bought.status.requested},
    )

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 403
    assert response.json()["detail"] == lang(t_user).API.BOUGHTITEM.CANNOT_CHANGE_OTHER_USER_ITEM


def test_update_item_status__super_user__of_another_user(
    client: TestClient, super_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test the update of an item status by a super user for an item belonging to another user.
    This test performs the following steps:
    1. Preparation:
        - Retrieve a test super user from the database.
        - Create a random item associated with the test super user.
    2. Methods to Test:
        - Send a PUT request to update the status of the created item using the super user's token headers.
        - Parse the response into a schema.
    3. Validation:
        - Assert that the response is valid and has a status code of 200.
        - Assert that the response schema is valid and the status is updated to the requested status.
    Args:
        client (TestClient): The test client to send requests.
        super_user_token_headers (Dict[str, str]): The headers containing the super user's authentication token.
        db (Session): The database session for accessing the database.
    """

    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_user = get_test_user(db)
    t_item = create_random_item(db, user=t_user)

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.put(
        UPDATE_ITEM_STATUS.substitute(item_id=t_item.id),
        headers=super_user_token_headers,
        params={"status": cfg.items.bought.status.requested},
    )
    responseSchema = BoughtItemSchema(**response.json())

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 200

    assert responseSchema
    assert responseSchema.status == cfg.items.bought.status.requested


def test_update_item_status__admin_user__of_another_user(
    client: TestClient, admin_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test the update of an item status by an admin user for another user's item.

    This test performs the following steps:
    1. Preparation:
        - Retrieve a test super user from the database.
        - Create a random item associated with the test super user.
    2. Methods to Test:
        - Send a PUT request to update the status of the created item using the admin user's token headers.
        - Parse the response into a BoughtItemSchema.
    3. Validation:
        - Assert that the response is not None.
        - Assert that the response status code is 200.
        - Assert that the response schema is not None.
        - Assert that the status in the response schema matches the requested status.

    Args:
        client (TestClient): The test client to send requests.
        admin_user_token_headers (Dict[str, str]): The headers containing the admin user's authentication token.
        db (Session): The database session.
    """

    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_user = get_test_user(db)
    t_item = create_random_item(db, user=t_user)

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.put(
        UPDATE_ITEM_STATUS.substitute(item_id=t_item.id),
        headers=admin_user_token_headers,
        params={"status": cfg.items.bought.status.requested},
    )
    responseSchema = BoughtItemSchema(**response.json())

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 200

    assert responseSchema
    assert responseSchema.status == cfg.items.bought.status.requested


def test_update_item_status__guest_user(
    client: TestClient, guest_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test the update item status endpoint for a guest user.

    This test verifies that a guest user is not allowed to update the status of an item.
    It performs the following steps:

    1. Preparation: Create a random item in the database.
    2. Methods to Test: Attempt to update the status of the created item using a PUT request.
    3. Validation: Assert that the response status code is 403 (Forbidden) and the response
       contains the appropriate error message indicating no permission.

    Args:
        client (TestClient): The test client to simulate API requests.
        guest_user_token_headers (Dict[str, str]): The headers containing the guest user's token.
        db (Session): The database session for database operations.
    """

    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_item = create_random_item(db)

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.put(
        UPDATE_ITEM_STATUS.substitute(item_id=t_item.id),
        headers=guest_user_token_headers,
        params={"status": cfg.items.bought.status.ordered},
    )

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 403
    assert response.json()["detail"] == lang(get_test_guest_user(db)).API.BOUGHTITEM.UPDATE_NO_PERMISSION
