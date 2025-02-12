"""
    TEST WEB API -- BOUGHT ITEMS -- UPDATE UNIT
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

UPDATE_ITEM_UNIT = Template(f"{cfg.server.api.web}/items/bought/$item_id/unit")


def test_update_item_unit__unauthorized(client: TestClient, db: Session) -> None:
    """
    Test the update item unit endpoint for unauthorized access.

    This test ensures that an unauthorized request to update an item unit
    returns a 401 status code with the appropriate error message.

    Args:
        client (TestClient): The test client used to make HTTP requests.
        db (Session): The database session used to create a random item.

    Steps:
        1. Create a random item in the database.
        2. Attempt to update the item unit without providing authorization headers.
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

    response = client.put(UPDATE_ITEM_UNIT.substitute(item_id=t_item.id), headers={})

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid access token"


def test_update_item_unit__normal_user(
    client: TestClient, normal_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test the update of an item's unit by a normal user.

    This test verifies that a normal user can successfully update the unit of an item.

    Args:
        client (TestClient): The test client to simulate API requests.
        normal_user_token_headers (Dict[str, str]): The headers containing the normal user's authentication token.
        db (Session): The database session for interacting with the database.

    Steps:
        1. Create a random item in the database.
        2. Send a PUT request to update the unit of the created item.
        3. Validate the response to ensure the update was successful.

    Asserts:
        - The response is not None.
        - The response status code is 200.
        - The response schema matches the expected item ID and unit.
    """
    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_item = create_random_item(db)

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.put(
        UPDATE_ITEM_UNIT.substitute(item_id=t_item.id),
        headers=normal_user_token_headers,
        params={"unit": cfg.items.bought.units.values[-1]},
    )
    responseScheme = BoughtItemSchema(**response.json())

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 200

    assert responseScheme
    assert responseScheme.id == t_item.id
    assert responseScheme.unit == cfg.items.bought.units.values[-1]


def test_update_item_unit__normal_user__not_found(
    client: TestClient, normal_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test case for updating an item unit with a normal user when the item is not found.

    This test verifies that when a normal user attempts to update the unit of a non-existent item,
    the API responds with a 404 Not Found status code and the appropriate error message.

    Args:
        client (TestClient): The test client to simulate API requests.
        normal_user_token_headers (Dict[str, str]): The headers containing the normal user's authentication token.
        db (Session): The database session for accessing the database.

    Asserts:
        response: The response object from the API request.
        response.status_code: The status code of the response should be 404.
        response.json()["detail"]: The error detail message should indicate that the item was not found.
    """
    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.put(
        UPDATE_ITEM_UNIT.substitute(item_id=9999999),
        headers=normal_user_token_headers,
        params={"unit": cfg.items.bought.units.default},
    )

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 404
    assert response.json()["detail"] == lang(get_test_user(db)).API.BOUGHTITEM.ITEM_NOT_FOUND


def test_update_item_unit__normal_user__invalid_id(
    client: TestClient, normal_user_token_headers: Dict[str, str]
) -> None:
    """
    Test updating an item unit with an invalid item ID for a normal user.

    This test verifies that when a normal user attempts to update an item unit
    with an invalid item ID (non-integer), the API responds with a 422 status code
    and the appropriate error message indicating that the item ID should be a valid integer.

    Args:
        client (TestClient): The test client to simulate API requests.
        normal_user_token_headers (Dict[str, str]): The headers containing the normal user's authentication token.

    Asserts:
        - The response is not None.
        - The response status code is 422.
        - The error location in the response JSON is "path" and "item_id".
        - The error message indicates that the input should be a valid integer.
    """
    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.put(
        UPDATE_ITEM_UNIT.substitute(item_id="A"),
        headers=normal_user_token_headers,
        params={"unit": cfg.items.bought.units.default},
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


def test_update_item_unit__normal_user__unknown_unit(
    client: TestClient, normal_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test updating an item's unit with an unknown unit by a normal user.

    This test performs the following steps:
    1. Preparation: Create a random item in the database.
    2. Methods to Test: Attempt to update the item's unit to an unknown value using a PUT request.
    3. Validation: Verify that the response status code is 422 and the error details indicate
       that the 'unit' query parameter is invalid.

    Args:
        client (TestClient): The test client to simulate API requests.
        normal_user_token_headers (Dict[str, str]): The headers containing the normal user's authentication token.
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
        UPDATE_ITEM_UNIT.substitute(item_id=t_item.id),
        headers=normal_user_token_headers,
        params={"unit": "an_unknown_unit"},
    )

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"][0] == "query"
    assert response.json()["detail"][0]["loc"][1] == "unit"


def test_update_item_unit__normal_user__of_another_user(
    client: TestClient, normal_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test updating an item unit by a normal user who does not own the item.

    This test ensures that a normal user cannot update the unit of an item
    that belongs to another user. The expected behavior is that the request
    is forbidden and returns a 403 status code with an appropriate error message.

    Args:
        client (TestClient): The test client to simulate API requests.
        normal_user_token_headers (Dict[str, str]): The headers containing the normal user's authentication token.
        db (Session): The database session for accessing and manipulating the database.

    Assertions:
        - The response is not None.
        - The response status code is 403 (Forbidden).
        - The response JSON contains the expected error message indicating that the user cannot change another user's item.
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
        UPDATE_ITEM_UNIT.substitute(item_id=t_item.id),
        headers=normal_user_token_headers,
        params={"unit": cfg.items.bought.units.values[-1]},
    )

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 403
    assert response.json()["detail"] == lang(t_user).API.BOUGHTITEM.CANNOT_CHANGE_OTHER_USER_ITEM


def test_update_item_unit__super_user__of_another_user(
    client: TestClient, super_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test the update of an item's unit by a super user on behalf of another user.

    This test performs the following steps:
    1. Preparation:
        - Retrieve a test super user from the database.
        - Create a random item associated with the test super user.
    2. Methods to Test:
        - Send a PUT request to update the unit of the created item using the super user's token headers.
        - Parse the response into a BoughtItemSchema.
    3. Validation:
        - Assert that the response is not None.
        - Assert that the response status code is 200 (OK).
        - Assert that the response schema is not None.
        - Assert that the unit in the response schema matches the expected unit value.

    Args:
        client (TestClient): The test client to send requests.
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
        UPDATE_ITEM_UNIT.substitute(item_id=t_item.id),
        headers=super_user_token_headers,
        params={"unit": cfg.items.bought.units.values[-1]},
    )
    responseSchema = BoughtItemSchema(**response.json())

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 200

    assert responseSchema
    assert responseSchema.unit == cfg.items.bought.units.values[-1]


def test_update_item_unit__admin_user__of_another_user(
    client: TestClient, admin_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test case for updating the unit of an item by an admin user on behalf of another user.

    This test performs the following steps:
    1. Preparation:
        - Retrieves a test super user from the database.
        - Creates a random item associated with the test super user.
    2. Methods to Test:
        - Sends a PUT request to update the unit of the created item using the admin user's token headers.
        - Parses the response into a BoughtItemSchema.
    3. Validation:
        - Asserts that the response is not None.
        - Asserts that the response status code is 200.
        - Asserts that the response schema is not None.
        - Asserts that the unit in the response schema matches the expected unit value.

    Args:
        client (TestClient): The test client to send requests.
        admin_user_token_headers (Dict[str, str]): The headers containing the admin user's authentication token.
        db (Session): The database session.
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
        UPDATE_ITEM_UNIT.substitute(item_id=t_item.id),
        headers=admin_user_token_headers,
        params={"unit": cfg.items.bought.units.values[-1]},
    )
    responseSchema = BoughtItemSchema(**response.json())

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 200

    assert responseSchema
    assert responseSchema.unit == cfg.items.bought.units.values[-1]


def test_update_item_unit__guest_user(
    client: TestClient, guest_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test the update item unit endpoint for a guest user.

    This test verifies that a guest user does not have permission to update the unit of an item.

    Args:
        client (TestClient): The test client to simulate API requests.
        guest_user_token_headers (Dict[str, str]): The headers containing the guest user's authentication token.
        db (Session): The database session for accessing the database.

    Steps:
        1. Create a random item in the database.
        2. Attempt to update the unit of the created item using the guest user's token.
        3. Validate that the response status code is 403 (Forbidden).
        4. Validate that the response contains the appropriate error message indicating no permission.

    Asserts:
        - The response object is not None.
        - The response status code is 403.
        - The response JSON contains the correct error message for no permission.
    """
    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_item = create_random_item(db)

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.put(
        UPDATE_ITEM_UNIT.substitute(item_id=t_item.id),
        headers=guest_user_token_headers,
        params={"unit": cfg.items.bought.units.values[-1]},
    )

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 403
    assert response.json()["detail"] == lang(get_test_guest_user(db)).API.BOUGHTITEM.UPDATE_NO_PERMISSION
