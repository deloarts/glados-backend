"""
    TEST WEB API -- BOUGHT ITEMS -- UPDATE QUANTITY
"""

from string import Template
from typing import Dict

from api.schemas.bought_item import BoughtItemSchema
from config import cfg
from fastapi.testclient import TestClient
from locales import lang
from sqlalchemy.orm import Session

from tests.utils.bought_item import create_random_item
from tests.utils.user import get_test_guest_user
from tests.utils.user import get_test_super_user
from tests.utils.user import get_test_user

UPDATE_ITEM_QUANTITY = Template(f"{cfg.server.api.web}/items/bought/$item_id/quantity")


def test_update_item_quantity__unauthorized(client: TestClient, db: Session) -> None:
    """
    Test the update item quantity endpoint for unauthorized access.
    This test verifies that an unauthorized user (without a valid access token)
    cannot update the quantity of an item.

    Steps:
    1. Create a random item in the database.
    2. Attempt to update the quantity of the created item without providing authorization headers.
    3. Validate that the response status code is 401 (Unauthorized).
    4. Validate that the response contains the appropriate error message indicating an invalid access token.

    Args:
        client (TestClient): The test client used to make HTTP requests.
        db (Session): The database session used to interact with the database.
    """

    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_item = create_random_item(db)

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.put(UPDATE_ITEM_QUANTITY.substitute(item_id=t_item.id), headers={})

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid access token"


def test_update_item_quantity__normal_user(
    client: TestClient, normal_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test the update of an item's quantity by a normal user.
    This test performs the following steps:
    1. Preparation: Create a random item in the database.
    2. Methods to Test: Send a PUT request to update the item's quantity.
    3. Validation: Verify that the response is successful and the item's quantity is updated correctly.

    Args:
        client (TestClient): The test client to simulate API requests.
        normal_user_token_headers (Dict[str, str]): The headers containing the normal user's authentication token.
        db (Session): The database session for database operations.

    Asserts:
        The response is successful (status code 200).
        The response schema matches the expected item ID and updated quantity.
    """
    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_item = create_random_item(db)

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.put(
        UPDATE_ITEM_QUANTITY.substitute(item_id=t_item.id),
        headers=normal_user_token_headers,
        params={"quantity": 100},
    )
    responseScheme = BoughtItemSchema(**response.json())

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 200

    assert responseScheme
    assert responseScheme.id == t_item.id
    assert responseScheme.quantity == 100


def test_update_item_quantity__normal_user__not_found(
    client: TestClient, normal_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test case for updating the quantity of a bought item by a normal user when the item is not found.
    This test ensures that when a normal user attempts to update the quantity of a bought item
    that does not exist, the API responds with a 404 Not Found status code and the appropriate
    error message.

    Args:
        client (TestClient): The test client to simulate API requests.
        normal_user_token_headers (Dict[str, str]): The headers containing the normal user's authentication token.
        db (Session): The database session for accessing the database.

    Asserts:
        response: The response object from the API request.
        response.status_code == 404: The status code should be 404 Not Found.
        response.json()["detail"] == lang(get_test_user(db)).API.BOUGHTITEM.ITEM_NOT_FOUND: The error message should indicate that the item was not found.
    """
    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.put(
        UPDATE_ITEM_QUANTITY.substitute(item_id=9999999),
        headers=normal_user_token_headers,
        params={"quantity": 100},
    )

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 404
    assert response.json()["detail"] == lang(get_test_user(db)).API.BOUGHTITEM.ITEM_NOT_FOUND


def test_update_item_quantity__normal_user__invalid_id(
    client: TestClient, normal_user_token_headers: Dict[str, str]
) -> None:
    """
    Test updating item quantity with an invalid item ID for a normal user.

    This test verifies that when a normal user attempts to update the quantity
    of an item using an invalid item ID, the API responds with a 422 Unprocessable
    Entity status code and the appropriate error message indicating that the item ID
    should be a valid integer.

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
        UPDATE_ITEM_QUANTITY.substitute(item_id="A"),
        headers=normal_user_token_headers,
        params={"quantity": 100},
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


def test_update_item_quantity__normal_user__invalid_quantity(
    client: TestClient, normal_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test updating the quantity of an item with an invalid quantity value by a normal user.
    This test verifies that when a normal user attempts to update the quantity of an item
    with an invalid quantity value (non-integer), the API responds with a 422 Unprocessable Entity status code
    and the appropriate error message indicating that the input should be a valid integer.

    Args:
        client (TestClient): The test client to simulate API requests.
        normal_user_token_headers (Dict[str, str]): The authentication headers for a normal user.
        db (Session): The database session for creating test data.
    """
    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_item = create_random_item(db)

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.put(
        UPDATE_ITEM_QUANTITY.substitute(item_id=t_item.id),
        headers=normal_user_token_headers,
        params={"quantity": "A"},
    )

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"][0] == "query"
    assert response.json()["detail"][0]["loc"][1] == "quantity"
    assert (
        response.json()["detail"][0]["msg"] == "Input should be a valid integer, unable to parse string as an integer"
    )


def test_update_item_quantity__normal_user__of_another_user(
    client: TestClient, normal_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test updating the quantity of an item by a normal user who does not own the item.
    This test ensures that a normal user cannot update the quantity of an item that belongs to another user.
    It performs the following steps:

    1. Preparation:
        - Retrieve a test user and a test super user from the database.
        - Create a random item associated with the test super user.
    2. Methods to Test:
        - Attempt to update the quantity of the created item using the normal user's token headers.
    3. Validation:
        - Assert that the response is received.
        - Assert that the status code of the response is 403 (Forbidden).
        - Assert that the response JSON contains the appropriate error message indicating that the user cannot change another user's item.

    Args:
        client (TestClient): The test client to simulate API requests.
        normal_user_token_headers (Dict[str, str]): The headers containing the normal user's authentication token.
        db (Session): The database session for accessing the database.
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
        UPDATE_ITEM_QUANTITY.substitute(item_id=t_item.id),
        headers=normal_user_token_headers,
        params={"quantity": 100},
    )

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 403
    assert response.json()["detail"] == lang(t_user).API.BOUGHTITEM.CANNOT_CHANGE_OTHER_USER_ITEM


def test_update_item_quantity__super_user__of_another_user(
    client: TestClient, super_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test the update of an item's quantity by a super user on behalf of another user.

    This test performs the following steps:
    1. Preparation:
        - Retrieve a test super user from the database.
        - Create a random item associated with the test super user.
    2. Methods to Test:
        - Send a PUT request to update the quantity of the created item using the super user's token headers.
        - Parse the response into a BoughtItemSchema.
    3. Validation:
        - Assert that the response is not None.
        - Assert that the response status code is 200 (OK).
        - Assert that the response schema is not None.
        - Assert that the quantity in the response schema is updated to 100.

    Args:
        client (TestClient): The test client to simulate HTTP requests.
        super_user_token_headers (Dict[str, str]): The headers containing the super user's authentication token.
        db (Session): The database session for accessing the database.
    """
    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_super = get_test_super_user(db)
    t_item = create_random_item(db, user=t_super)

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.put(
        UPDATE_ITEM_QUANTITY.substitute(item_id=t_item.id),
        headers=super_user_token_headers,
        params={"quantity": 100},
    )
    responseSchema = BoughtItemSchema(**response.json())

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 200

    assert responseSchema
    assert responseSchema.quantity == 100


def test_update_item_quantity__admin_user__of_another_user(
    client: TestClient, admin_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test the update of an item's quantity by an admin user on behalf of another user.
    This test performs the following steps:

    1. Preparation:
        - Retrieve a test super user from the database.
        - Create a random item associated with the test super user.
    2. Methods to Test:
        - Send a PUT request to update the quantity of the created item using admin user token headers.
        - Parse the response into a BoughtItemSchema.
    3. Validation:
        - Assert that the response is not None.
        - Assert that the response status code is 200 (OK).
        - Assert that the response schema is not None.
        - Assert that the quantity in the response schema is updated to 100.

    Args:
        client (TestClient): The test client to send requests.
        admin_user_token_headers (Dict[str, str]): The headers containing the admin user's authentication token.
        db (Session): The database session for database operations.
    """
    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_super = get_test_super_user(db)
    t_item = create_random_item(db, user=t_super)

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.put(
        UPDATE_ITEM_QUANTITY.substitute(item_id=t_item.id),
        headers=admin_user_token_headers,
        params={"quantity": 100},
    )
    responseSchema = BoughtItemSchema(**response.json())

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 200

    assert responseSchema
    assert responseSchema.quantity == 100


def test_update_item_quantity__guest_user(
    client: TestClient, guest_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test the update of an item's quantity by a guest user.
    This test ensures that a guest user does not have permission to update the quantity of an item.
    It verifies that the response status code is 403 and the appropriate error message is returned.

    Args:
        client (TestClient): The test client to simulate API requests.
        guest_user_token_headers (Dict[str, str]): The headers containing the guest user's authentication token.
        db (Session): The database session for creating and querying data.
    """
    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_item = create_random_item(db)

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.put(
        UPDATE_ITEM_QUANTITY.substitute(item_id=t_item.id),
        headers=guest_user_token_headers,
        params={"quantity": 100},
    )

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 403
    assert response.json()["detail"] == lang(get_test_guest_user(db)).API.BOUGHTITEM.UPDATE_NO_PERMISSION
