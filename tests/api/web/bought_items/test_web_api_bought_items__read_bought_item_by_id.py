"""
    TEST WEB API -- BOUGHT ITEMS -- READ BY ID
"""

from api.schemas.bought_item import BoughtItemSchema
from config import cfg
from fastapi.testclient import TestClient
from locales import lang
from sqlalchemy.orm import Session

from tests.utils.bought_item import create_random_item
from tests.utils.user import get_test_user
from tests.utils.utils import random_bought_item_name
from tests.utils.utils import random_bought_item_order_number
from tests.utils.utils import random_manufacturer

READ_ITEM_BY_ID_API = f"{cfg.server.api.web}/items/bought"
JSON_ITEM_DATA = {
    "project_id": None,
    "quantity": 1,
    "unit": cfg.items.bought.units.default,
    "partnumber": random_bought_item_name(),
    "order_number": random_bought_item_order_number(),
    "manufacturer": random_manufacturer(),
}


def test_read_item_by_id__unauthorized(client: TestClient) -> None:
    """
    Test case for reading an item by ID without authorization.

    This test ensures that an unauthorized request to read an item by its ID
    returns a 401 Unauthorized status code and the appropriate error message.

    Args:
        client (TestClient): The test client used to make the request.

    Asserts:
        - The response is not None.
        - The response status code is 401.
        - The response JSON contains the detail message "Invalid access token".
    """

    # ----------------------------------------------
    # GET USER ME: METHODS TO TEST
    # ----------------------------------------------

    response = client.get(f"{READ_ITEM_BY_ID_API}/1", headers={})

    # ----------------------------------------------
    # GET OWN USER: VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid access token"


def test_read_item_by_id__normal_user(client: TestClient, normal_user_token_headers: dict, db: Session) -> None:
    """
    Test the API endpoint to read a bought item by its ID for a normal user.
    This test performs the following steps:

    1. Preparation: Create a random item in the database.
    2. Methods to Test: Send a GET request to the API endpoint to read the item by its ID.
    3. Validation: Verify that the response status code is 200 and the response data matches the created item.

    Args:
        client (TestClient): The test client to simulate API requests.
        normal_user_token_headers (dict): The headers containing the authentication token for a normal user.
        db (Session): The database session to interact with the database.

    Asserts:
        The response status code is 200.
        The response data matches the created item's ID, creator ID, project ID, project number, quantity, unit, part number, order number, and manufacturer.
    """

    # ----------------------------------------------
    # GET ITEM: PREPARATION
    # ----------------------------------------------

    item = create_random_item(db)

    # ----------------------------------------------
    # GET ITEM: METHODS TO TEST
    # ----------------------------------------------

    response = client.get(f"{READ_ITEM_BY_ID_API}/{item.id}", headers=normal_user_token_headers)
    responseScheme = BoughtItemSchema(**response.json())

    # ----------------------------------------------
    # GET ITEM: VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 200

    assert responseScheme
    assert responseScheme.id == item.id
    assert responseScheme.creator_id == item.creator_id

    assert responseScheme.project_id == item.project_id
    assert responseScheme.project_number == item.project_number

    assert responseScheme.quantity == item.quantity
    assert responseScheme.unit == item.unit
    assert responseScheme.partnumber == item.partnumber
    assert responseScheme.order_number == item.order_number
    assert responseScheme.manufacturer == item.manufacturer


def test_read_item_by_id__super_user(client: TestClient, super_user_token_headers: dict, db: Session) -> None:
    """
    Test the API endpoint to read a bought item by its ID as a super user.

    This test performs the following steps:
    1. Preparation: Create a random item in the database.
    2. Methods to Test: Send a GET request to the API endpoint to read the item by its ID using super user credentials.
    3. Validation: Verify that the response is successful (status code 200) and that the returned item matches the created item.

    Args:
        client (TestClient): The test client to simulate API requests.
        super_user_token_headers (dict): The headers containing the super user authentication token.
        db (Session): The database session to interact with the database.

    Asserts:
        The response is not None.
        The response status code is 200.
        The response schema is valid and the item ID matches the created item ID.
    """

    # ----------------------------------------------
    # GET ITEM: PREPARATION
    # ----------------------------------------------

    item = create_random_item(db)

    # ----------------------------------------------
    # GET ITEM: METHODS TO TEST
    # ----------------------------------------------

    response = client.get(f"{READ_ITEM_BY_ID_API}/{item.id}", headers=super_user_token_headers)
    responseScheme = BoughtItemSchema(**response.json())

    # ----------------------------------------------
    # GET ITEM: VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 200

    assert responseScheme
    assert responseScheme.id == item.id


def test_read_item_by_id__admin_user(client: TestClient, admin_user_token_headers: dict, db: Session) -> None:
    """
    Test the API endpoint to read a bought item by its ID for an admin user.

    This test performs the following steps:
    1. Creates a random item in the database.
    2. Sends a GET request to the API endpoint to read the item by its ID using admin user headers.
    3. Validates the response to ensure the item is correctly retrieved.

    Args:
        client (TestClient): The test client to simulate API requests.
        admin_user_token_headers (dict): The headers containing the admin user's authentication token.
        db (Session): The database session to interact with the database.

    Asserts:
        - The response is not None.
        - The response status code is 200.
        - The response schema is valid and matches the created item's ID.
    """

    # ----------------------------------------------
    # GET ITEM: PREPARATION
    # ----------------------------------------------

    item = create_random_item(db)

    # ----------------------------------------------
    # GET ITEM: METHODS TO TEST
    # ----------------------------------------------

    response = client.get(f"{READ_ITEM_BY_ID_API}/{item.id}", headers=admin_user_token_headers)
    responseScheme = BoughtItemSchema(**response.json())

    # ----------------------------------------------
    # GET ITEM: VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 200

    assert responseScheme
    assert responseScheme.id == item.id


def test_read_item_by_id__guest_user(client: TestClient, guest_user_token_headers: dict, db: Session) -> None:
    """
    Test the 'read item by ID' API endpoint for a guest user.

    This test performs the following steps:
    1. Preparation: Create a random item in the database.
    2. Methods to Test: Send a GET request to the 'read item by ID' API endpoint using the guest user's token headers.
    3. Validation: Verify that the response is successful (status code 200) and that the returned item matches the created item.

    Args:
        client (TestClient): The test client to simulate API requests.
        guest_user_token_headers (dict): The headers containing the guest user's authentication token.
        db (Session): The database session for interacting with the database.
    """

    # ----------------------------------------------
    # GET ITEM: PREPARATION
    # ----------------------------------------------

    item = create_random_item(db)

    # ----------------------------------------------
    # GET ITEM: METHODS TO TEST
    # ----------------------------------------------

    response = client.get(f"{READ_ITEM_BY_ID_API}/{item.id}", headers=guest_user_token_headers)
    responseScheme = BoughtItemSchema(**response.json())

    # ----------------------------------------------
    # GET ITEM: VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 200

    assert responseScheme
    assert responseScheme.id == item.id


def test_read_item_by_id__normal_user__not_found(
    client: TestClient, normal_user_token_headers: dict, db: Session
) -> None:
    """
    Test case for reading a bought item by ID as a normal user when the item is not found.
    This test verifies that when a normal user attempts to read a bought item by an ID that does not exist,
    the API responds with a 404 status code and the appropriate error message.

    Args:
        client (TestClient): The test client to simulate API requests.
        normal_user_token_headers (dict): The authentication headers for a normal user.
        db (Session): The database session for accessing the database.

    Asserts:
        response.status_code (int): The status code of the response should be 404.
        response.json()["detail"] (str): The error message should indicate that the item was not found.
    """

    # ----------------------------------------------
    # GET ITEM: METHODS TO TEST
    # ----------------------------------------------

    response = client.get(f"{READ_ITEM_BY_ID_API}/0", headers=normal_user_token_headers)

    # ----------------------------------------------
    # GET ITEM: VALIDATION
    # ----------------------------------------------

    assert response.status_code == 404
    assert response.json()["detail"] == lang(get_test_user(db)).API.BOUGHTITEM.ITEM_NOT_FOUND


def test_read_item_by_id__normal_user__invalid_query_param(client: TestClient, normal_user_token_headers: dict) -> None:
    """
    Test the read item by ID endpoint with an invalid query parameter for a normal user.
    This test verifies that when a normal user attempts to read an item by ID using an invalid query parameter,
    the API responds with a 422 Unprocessable Entity status code and the appropriate error message.

    Args:
        client (TestClient): The test client used to make requests to the API.
        normal_user_token_headers (dict): The headers containing the normal user's authentication token.

    Asserts:
        - The response status code is 422.
        - The error location in the response JSON is "path" and "item_id".
        - The error message indicates that the input should be a valid integer and the string could not be parsed as an integer.
    """

    # ----------------------------------------------
    # GET ITEM: METHODS TO TEST
    # ----------------------------------------------

    response = client.get(f"{READ_ITEM_BY_ID_API}/A", headers=normal_user_token_headers)

    # ----------------------------------------------
    # GET ITEM: VALIDATION
    # ----------------------------------------------

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"][0] == "path"
    assert response.json()["detail"][0]["loc"][1] == "item_id"
    assert (
        response.json()["detail"][0]["msg"] == "Input should be a valid integer, unable to parse string as an integer"
    )
