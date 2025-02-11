"""
    TEST WEB API -- BOUGHT ITEMS -- CREATE
"""

import copy

from config import cfg
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.utils.project import get_test_project
from tests.utils.utils import random_bought_item_name
from tests.utils.utils import random_bought_item_order_number
from tests.utils.utils import random_manufacturer

CREATE_ITEM_API = f"{cfg.server.api.web}/items/bought"
JSON_ITEM_DATA = {
    "project_id": None,
    "quantity": 1,
    "unit": cfg.items.bought.units.default,
    "partnumber": random_bought_item_name(),
    "order_number": random_bought_item_order_number(),
    "manufacturer": random_manufacturer(),
}


def test_create_item__unauthorized(client: TestClient) -> None:
    """
    Test the creation of an item without authorization.
    This test verifies that attempting to create an item without providing
    the necessary authorization headers results in a 401 Unauthorized response.
    Steps:

    1. Send a POST request to the CREATE_ITEM_API endpoint without headers.
    2. Validate that the response status code is 401.
    3. Validate that the response JSON contains the detail message "Invalid access token".

    Args:
        client (TestClient): The test client used to make requests to the API.
    """

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.post(CREATE_ITEM_API, headers={})

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid access token"


def test_create_item__normal_user(client: TestClient, normal_user_token_headers: dict, db: Session) -> None:
    """
    Test the creation of an item by a normal user.
    This test performs the following steps:

    1. Prepares the item data by copying a predefined JSON structure and setting the project ID.
    2. Sends a POST request to create the item using the provided client and headers.
    3. Validates the response by checking the status code and the presence of expected fields in the response content.
    4. Asserts that the values of certain fields in the response match the expected values.

    Args:
        client (TestClient): The test client to send requests.
        normal_user_token_headers (dict): The headers containing the normal user's authentication token.
        db (Session): The database session for accessing the test database.
    """

    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_data = copy.deepcopy(JSON_ITEM_DATA)
    t_data["project_id"] = get_test_project(db).id

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.post(CREATE_ITEM_API, headers=normal_user_token_headers, json=t_data)

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response.status_code == 200
    content = response.json()

    assert "id" in content
    assert "status" in content
    assert "created" in content
    assert "creator_id" in content

    assert "project_id" in content
    assert "project_number" in content
    assert "project_is_active" in content
    assert "product_number" in content

    assert "high_priority" in content
    assert "notify_on_delivery" in content
    assert "quantity" in content
    assert "unit" in content
    assert "partnumber" in content
    assert "order_number" in content
    assert "manufacturer" in content
    assert "supplier" in content
    assert "weblink" in content
    assert "group_1" in content
    assert "note_general" in content
    assert "note_supplier" in content
    assert "desired_delivery_date" in content
    assert "creator_full_name" in content
    assert "requester_id" in content
    assert "requester_full_name" in content
    assert "requested_date" in content
    assert "orderer_id" in content
    assert "orderer_full_name" in content
    assert "ordered_date" in content
    assert "expected_delivery_date" in content
    assert "receiver_id" in content
    assert "receiver_full_name" in content
    assert "delivery_date" in content
    assert "storage_place" in content

    assert content["id"]
    assert content["status"] == cfg.items.bought.status.default
    assert content["project_id"] == t_data["project_id"]
    assert content["quantity"] == t_data["quantity"]
    assert content["unit"] == t_data["unit"]
    assert content["partnumber"] == t_data["partnumber"]
    assert content["order_number"] == t_data["order_number"]
    assert content["manufacturer"] == t_data["manufacturer"]


def test_create_item__normal_user__missing_project(client: TestClient, normal_user_token_headers: dict) -> None:
    """
    Test the creation of an item by a normal user when the project is missing or invalid.
    This test verifies the behavior of the API when attempting to create an item without a valid project ID.
    It performs the following checks:

    1. Attempts to create an item with the 'project_id' field missing from the request data.
    2. Attempts to create an item with an invalid 'project_id' (non-existent project).

    The expected outcomes are:
    - A 422 Unprocessable Entity status code when the 'project_id' is missing.
    - A 404 Not Found status code when the 'project_id' is invalid.

    Args:
        client (TestClient): The test client used to make HTTP requests to the API.
        normal_user_token_headers (dict): The headers containing the authentication token for a normal user.
    """

    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_data_1 = copy.deepcopy(JSON_ITEM_DATA)
    t_data_1.pop("project_id")

    t_data_2 = copy.deepcopy(JSON_ITEM_DATA)
    t_data_2["project_id"] = 999999999

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response_1 = client.post(f"{cfg.server.api.web}/items/bought/", headers=normal_user_token_headers, json=t_data_1)
    response_2 = client.post(f"{cfg.server.api.web}/items/bought/", headers=normal_user_token_headers, json=t_data_2)

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response_1.status_code == 422
    assert response_2.status_code == 404


def test_create_item__normal_user__missing_quantity(
    client: TestClient, normal_user_token_headers: dict, db: Session
) -> None:
    """
    Test the creation of an item with missing or invalid quantity by a normal user.
    This test verifies that the API returns a 422 Unprocessable Entity status code
    when attempting to create an item with either a missing quantity field or an
    invalid quantity value.

    Args:
        client (TestClient): The test client used to make API requests.
        normal_user_token_headers (dict): The headers containing the normal user's authentication token.
        db (Session): The database session used to interact with the test database.

    Preparation:
        - Create a copy of the JSON_ITEM_DATA and remove the "quantity" field.
        - Create another copy of the JSON_ITEM_DATA and set the "quantity" field to an invalid value ("no a number").

    Methods to Test:
        - POST request to create an item with missing quantity.
        - POST request to create an item with invalid quantity.

    Validation:
        - Assert that both responses return a 422 status code, indicating that the input data was unprocessable.
    """

    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_data_1 = copy.deepcopy(JSON_ITEM_DATA)
    t_data_1["project_id"] = get_test_project(db).id
    t_data_1.pop("quantity")

    t_data_2 = copy.deepcopy(JSON_ITEM_DATA)
    t_data_2["project_id"] = get_test_project(db).id
    t_data_2["quantity"] = "no a number"

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response_1 = client.post(CREATE_ITEM_API, headers=normal_user_token_headers, json=t_data_1)
    response_2 = client.post(CREATE_ITEM_API, headers=normal_user_token_headers, json=t_data_2)

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response_1.status_code == 422
    assert response_2.status_code == 422


def test_create_item__normal_user__missing_unit(
    client: TestClient, normal_user_token_headers: dict, db: Session
) -> None:
    """
    Test the creation of an item by a normal user when the unit is missing or invalid.
    This test performs the following steps:

    1. Prepares test data with a missing unit and an invalid unit.
    2. Sends POST requests to create items with the prepared data.
    3. Validates the responses to ensure correct handling of missing and invalid units.

    Args:
        client (TestClient): The test client to simulate API requests.
        normal_user_token_headers (dict): The headers containing the normal user's authentication token.
        db (Session): The database session for accessing test data.

    Asserts:
        - The response status code is 200 when the unit is missing (default unit is used).
        - The response status code is 422 when the unit is invalid.
    """

    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_data_1 = copy.deepcopy(JSON_ITEM_DATA)
    t_data_1["project_id"] = get_test_project(db).id
    t_data_1.pop("unit")

    t_data_2 = copy.deepcopy(JSON_ITEM_DATA)
    t_data_2["project_id"] = get_test_project(db).id
    t_data_2["unit"] = "no a valid unit"

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response_1 = client.post(CREATE_ITEM_API, headers=normal_user_token_headers, json=t_data_1)
    response_2 = client.post(CREATE_ITEM_API, headers=normal_user_token_headers, json=t_data_2)

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response_1.status_code == 200  # Missing unit will be replaced with default unit
    assert response_2.status_code == 422


def test_create_item__normal_user__missing_partnumber(
    client: TestClient, normal_user_token_headers: dict, db: Session
) -> None:
    """
    Test the creation of an item by a normal user when the 'partnumber' field is missing.
    This test performs the following steps:

    1. Prepares the test data by copying a predefined JSON item data and removing the 'partnumber' field.
    2. Sends a POST request to create the item using the prepared data.
    3. Validates that the response status code is 422, indicating a validation error due to the missing 'partnumber' field.

    Args:
        client (TestClient): The test client to simulate API requests.
        normal_user_token_headers (dict): The headers containing the normal user's authentication token.
        db (Session): The database session for accessing the test database.
    """

    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_data_1 = copy.deepcopy(JSON_ITEM_DATA)
    t_data_1["project_id"] = get_test_project(db).id
    t_data_1.pop("partnumber")

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response_1 = client.post(CREATE_ITEM_API, headers=normal_user_token_headers, json=t_data_1)

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response_1.status_code == 422


def test_create_item__normal_user__missing_order_number(
    client: TestClient, normal_user_token_headers: dict, db: Session
) -> None:
    """
    Test the creation of an item by a normal user when the order number is missing.
    This test performs the following steps:

    1. Prepares the item data with a missing order number.
    2. Sends a POST request to create the item using the provided client and headers.
    3. Validates that the response status code is 422, indicating a validation error.

    Args:
        client (TestClient): The test client to simulate API requests.
        normal_user_token_headers (dict): The headers containing the normal user's authentication token.
        db (Session): The database session for accessing test data.
    """

    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_data_1 = copy.deepcopy(JSON_ITEM_DATA)
    t_data_1["project_id"] = get_test_project(db).id
    t_data_1.pop("order_number")

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response_1 = client.post(CREATE_ITEM_API, headers=normal_user_token_headers, json=t_data_1)

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response_1.status_code == 422


def test_create_item__normal_user__missing_manufacturer(
    client: TestClient, normal_user_token_headers: dict, db: Session
) -> None:
    """
    Test case for creating an item with a normal user when the manufacturer field is missing.
    This test ensures that attempting to create an item without specifying the manufacturer
    results in a 422 Unprocessable Entity status code.

    Args:
        client (TestClient): The test client to simulate API requests.
        normal_user_token_headers (dict): The headers containing the normal user's authentication token.
        db (Session): The database session for accessing the test database.
    """

    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_data_1 = copy.deepcopy(JSON_ITEM_DATA)
    t_data_1["project_id"] = get_test_project(db).id
    t_data_1.pop("manufacturer")

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response_1 = client.post(CREATE_ITEM_API, headers=normal_user_token_headers, json=t_data_1)

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response_1.status_code == 422


def test_create_item__normal_user__extra_field(
    client: TestClient, normal_user_token_headers: dict, db: Session
) -> None:
    """
    Test creating an item with an extra field for a normal user.
    This test verifies that when a normal user attempts to create an item with an extra field
    that is not part of the database schema, the extra field is ignored and does not appear
    in the response.

    Args:
        client (TestClient): The test client to simulate API requests.
        normal_user_token_headers (dict): The headers containing the normal user's authentication token.
        db (Session): The database session for accessing the test database.

    Steps:
        1. Prepare the item data with an extra field that is not part of the database schema.
        2. Send a POST request to create the item with the prepared data.
        3. Validate that the response status code is 200 (OK).
        4. Validate that the extra field is not present in the response JSON.

    Asserts:
        - The response status code is 200.
        - The extra field is not present in the response JSON.
    """

    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_data_1 = copy.deepcopy(JSON_ITEM_DATA)
    t_data_1["project_id"] = get_test_project(db).id
    t_data_1["some_non_db_field"] = "some_value"

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response_1 = client.post(CREATE_ITEM_API, headers=normal_user_token_headers, json=t_data_1)

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response_1.status_code == 200
    assert "some_value" not in response_1.json()
