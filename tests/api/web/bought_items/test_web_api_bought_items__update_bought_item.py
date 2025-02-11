"""
    TEST WEB API -- BOUGHT ITEMS -- UPDATE
"""

from typing import Dict

from api.schemas.bought_item import BoughtItemSchema
from config import cfg
from crud.bought_item import crud_bought_item
from crud.project import crud_project
from fastapi.testclient import TestClient
from locales import lang
from sqlalchemy.orm import Session

from tests.utils.bought_item import create_random_item
from tests.utils.project import create_project
from tests.utils.user import get_test_super_user
from tests.utils.user import get_test_user
from tests.utils.utils import random_lower_string
from tests.utils.utils import random_manufacturer
from tests.utils.utils import random_project

UPDATE_ITEM_BY_ID = f"{cfg.server.api.web}/items/bought"


def test_update_item_by_id__unauthorized(client: TestClient, db: Session) -> None:
    """
    Test the update item by ID endpoint for unauthorized access.
    This test verifies that an unauthorized user (without a valid access token)
    cannot update an item by its ID. The expected response is a 401 Unauthorized
    status code with a specific error message.

    Args:
        client (TestClient): The test client used to make HTTP requests.
        db (Session): The database session used to interact with the test database.

    Assertions:
        - The response object is not None.
        - The response status code is 401 Unauthorized.
        - The response JSON contains a "detail" key with the value "Invalid access token".
    """

    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_user = get_test_user(db)

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.put(f"{UPDATE_ITEM_BY_ID}/{t_user.id}", headers={})

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid access token"


def test_update_item_by_id__normal_user(
    client: TestClient, normal_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test updating an item by ID for a normal user.

    This test verifies that a normal user can successfully update an item by its ID.
    It performs the following steps:

    1. Creates a random item in the database.
    2. Prepares the data for updating the item, including changing the part number.
    3. Sends a PUT request to update the item with the prepared data.
    4. Validates the response to ensure the update was successful and the part number was changed.

    Args:
        client (TestClient): The test client to simulate API requests.
        normal_user_token_headers (Dict[str, str]): The headers containing the normal user's authentication token.
        db (Session): The database session for database operations.

    Asserts:
        The response is not None.
        The response status code is 200.
        The response schema is valid and matches the updated item data.
    """

    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_item = create_random_item(db)
    data = {
        "project_id": t_item.project_id,
        "quantity": t_item.quantity,
        "unit": t_item.unit,
        "partnumber": "TestPartNumber",
        "order_number": t_item.order_number,
        "manufacturer": t_item.manufacturer,
    }

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.put(f"{UPDATE_ITEM_BY_ID}/{t_item.id}", headers=normal_user_token_headers, json=data)
    responseScheme = BoughtItemSchema(**response.json())

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 200

    assert responseScheme
    assert responseScheme.id == t_item.id
    assert responseScheme.partnumber == "TestPartNumber"


def test_update_item_by_id__normal_user__missing_field(
    client: TestClient, normal_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test updating an item by ID with a normal user when a required field is missing.

    This test verifies that the API returns a 422 Unprocessable Entity status code
    when attempting to update an item without providing all required fields.

    Args:
        client (TestClient): The test client to simulate API requests.
        normal_user_token_headers (Dict[str, str]): The authentication headers for a normal user.
        db (Session): The database session for database operations.
    """

    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_item = create_random_item(db)
    data = {
        "project_id": t_item.project_id,
        "quantity": t_item.quantity,
        "unit": t_item.unit,
        "order_number": t_item.order_number,
        "manufacturer": t_item.manufacturer,
    }

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.put(f"{UPDATE_ITEM_BY_ID}/{t_item.id}", headers=normal_user_token_headers, json=data)

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"][0] == "body"
    assert response.json()["detail"][0]["loc"][1] == "partnumber"


def test_update_item_by_id__normal_user__not_found(
    client: TestClient, normal_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test case for updating an item by ID as a normal user where the item is not found.
    This test verifies that when a normal user attempts to update an item with a non-existent ID,
    the API responds with a 404 Not Found status code and the appropriate error message.

    Args:
        client (TestClient): The test client to simulate API requests.
        normal_user_token_headers (Dict[str, str]): The headers containing the normal user's authentication token.
        db (Session): The database session for accessing the database.

    Assertions:
        - The response is not None.
        - The response status code is 404.
        - The response JSON contains the expected "detail" message indicating the item was not found.
    """

    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    data = {
        "project_id": 1,
        "quantity": 1,
        "unit": cfg.items.bought.units.default,
        "partnumber": "TestPartNumber",
        "order_number": "TestOrderNumber",
        "manufacturer": "TestManufacturer",
    }

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.put(f"{UPDATE_ITEM_BY_ID}/9999999", headers=normal_user_token_headers, json=data)

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 404
    assert response.json()["detail"] == lang(get_test_user(db)).API.BOUGHTITEM.ITEM_NOT_FOUND


def test_update_item_by_id__normal_user__project_not_found(
    client: TestClient, normal_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test updating an item by ID for a normal user when the project is not found.
    This test verifies that when a normal user attempts to update an item with a non-existent project ID,
    the API responds with a 404 status code and the appropriate error message.

    Args:
        client (TestClient): The test client to simulate API requests.
        normal_user_token_headers (Dict[str, str]): The authentication headers for a normal user.
        db (Session): The database session for creating test data.

    Assertions:
        - The response is not None.
        - The response status code is 404.
        - The response JSON contains the correct error message indicating the project was not found.
    """

    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_item = create_random_item(db)
    data = {
        "project_id": 9999999,
        "quantity": 1,
        "unit": cfg.items.bought.units.default,
        "partnumber": "TestPartNumber",
        "order_number": "TestOrderNumber",
        "manufacturer": "TestManufacturer",
    }

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.put(f"{UPDATE_ITEM_BY_ID}/{t_item.id}", headers=normal_user_token_headers, json=data)

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 404
    assert response.json()["detail"] == lang(get_test_user(db)).API.BOUGHTITEM.PROJECT_NOT_FOUND


def test_update_item_by_id__normal_user__project_inactive(
    client: TestClient, normal_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test updating an item by ID for a normal user when the project is inactive.
    This test verifies that a normal user cannot update an item if the associated project is inactive.

    It performs the following steps:
    1. Prepares the test environment by creating a test user, project, and item.
    2. Sets the project to inactive.
    3. Attempts to update the item with the provided data.
    4. Validates that the response status code is 403 and the error detail indicates the project is inactive.

    Args:
        client (TestClient): The test client to simulate API requests.
        normal_user_token_headers (Dict[str, str]): The headers containing the normal user's authentication token.
        db (Session): The database session for accessing the database.
    """

    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_user = get_test_user(db)
    t_project = create_project(
        db,
        user=t_user,
        number=random_project(),
        product_number=None,
        customer=random_manufacturer(),
        description=random_lower_string(),
        designated_user_id=t_user.id,
        is_active=True,
    )
    t_item = create_random_item(db, user=t_user, project=t_project)
    crud_project.update(
        db,
        db_obj_user=t_user,
        db_obj=t_project,
        obj_in={"is_active": False, "number": t_project.number, "designated_user_id": t_user.id},
    )

    data = {
        "project_id": t_project.id,
        "quantity": 1,
        "unit": cfg.items.bought.units.default,
        "partnumber": "TestPartNumber",
        "order_number": "TestOrderNumber",
        "manufacturer": "TestManufacturer",
    }

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.put(f"{UPDATE_ITEM_BY_ID}/{t_item.id}", headers=normal_user_token_headers, json=data)

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 403
    assert response.json()["detail"] == lang(t_user).API.BOUGHTITEM.PROJECT_INACTIVE


def test_update_item_by_id__normal_user__of_another_user(
    client: TestClient, normal_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test the update of an item by its ID when performed by a normal user who does not own the item.

    This test ensures that a normal user cannot update an item that belongs to another user.

    Args:
        client (TestClient): The test client to simulate API requests.
        normal_user_token_headers (Dict[str, str]): The headers containing the normal user's authentication token.
        db (Session): The database session for accessing the database.

    Steps:
        1. Prepare the test by creating a test user, a test super user, and a random item associated with the super user.
        2. Define the data to update the item.
        3. Attempt to update the item using the normal user's credentials.
        4. Validate that the response status code is 403 (Forbidden) and the error message indicates that the user cannot change another user's item.

    Asserts:
        - The response is not None.
        - The response status code is 403.
        - The response JSON contains the expected error detail message.
    """

    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_user = get_test_user(db)
    t_super = get_test_super_user(db)
    t_item = create_random_item(db, user=t_super)

    data = {
        "project_id": t_item.project_id,
        "quantity": 1,
        "unit": cfg.items.bought.units.default,
        "partnumber": "TestPartNumber",
        "order_number": "TestOrderNumber",
        "manufacturer": "TestManufacturer",
    }

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.put(f"{UPDATE_ITEM_BY_ID}/{t_item.id}", headers=normal_user_token_headers, json=data)

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 403
    assert response.json()["detail"] == lang(t_user).API.BOUGHTITEM.CANNOT_CHANGE_OTHER_USER_ITEM


def test_update_item_by_id__super_user__of_another_user(
    client: TestClient, super_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test the update of an item by its ID when performed by a super user on behalf of another user.

    This test performs the following steps:
    1. Prepares the test by creating a test user and a random item associated with that user.
    2. Constructs the data payload for updating the item.
    3. Sends a PUT request to update the item using the super user's token headers.
    4. Validates the response to ensure the update was successful and the returned data matches the expected values.

    Args:
        client (TestClient): The test client to simulate API requests.
        super_user_token_headers (Dict[str, str]): The headers containing the super user's authentication token.
        db (Session): The database session for accessing and manipulating the database.

    Asserts:
        The response is not None.
        The response status code is 200 (OK).
        The response schema matches the expected values, including the item ID and part number.
    """

    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_user = get_test_user(db)
    t_item = create_random_item(db, user=t_user)

    data = {
        "project_id": t_item.project_id,
        "quantity": 1,
        "unit": cfg.items.bought.units.default,
        "partnumber": "TestPartNumber",
        "order_number": "TestOrderNumber",
        "manufacturer": "TestManufacturer",
    }

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.put(f"{UPDATE_ITEM_BY_ID}/{t_item.id}", headers=super_user_token_headers, json=data)
    responseSchema = BoughtItemSchema(**response.json())

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 200

    assert responseSchema
    assert responseSchema.id == t_item.id
    assert responseSchema.partnumber == "TestPartNumber"


def test_update_item_by_id__admin_user__of_another_user(
    client: TestClient, admin_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test the update of an item by its ID when performed by an admin user on behalf of another user.

    This test performs the following steps:
    1. Prepares the test environment by creating a test user and a random item associated with that user.
    2. Constructs the data payload required for updating the item.
    3. Sends a PUT request to update the item using the admin user's token headers.
    4. Validates the response to ensure the item was updated correctly.

    Args:
        client (TestClient): The test client to simulate API requests.
        admin_user_token_headers (Dict[str, str]): The headers containing the admin user's authentication token.
        db (Session): The database session used for creating test data.

    Asserts:
        The response is not None.
        The response status code is 200 (OK).
        The response schema matches the expected values, including the item ID and part number.
    """

    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_user = get_test_user(db)
    t_item = create_random_item(db, user=t_user)

    data = {
        "project_id": t_item.project_id,
        "quantity": 1,
        "unit": cfg.items.bought.units.default,
        "partnumber": "TestPartNumber",
        "order_number": "TestOrderNumber",
        "manufacturer": "TestManufacturer",
    }

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.put(f"{UPDATE_ITEM_BY_ID}/{t_item.id}", headers=admin_user_token_headers, json=data)
    responseSchema = BoughtItemSchema(**response.json())

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 200

    assert responseSchema
    assert responseSchema.id == t_item.id
    assert responseSchema.partnumber == "TestPartNumber"


def test_update_item_by_id__normal_user__already_planned(
    client: TestClient, normal_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test the update of an item by its ID for a normal user when the item is already planned.

    This test verifies that a normal user cannot update an item that has already been planned.
    It performs the following steps:
    1. Prepares the test by creating a test user, a test super user, and a random item associated with the super user.
    2. Updates the status of the item to 'ordered'.
    3. Attempts to update the item using the normal user's credentials.
    4. Validates that the response status code is 403 and the error message indicates that the planned item cannot be changed.

    Args:
        client (TestClient): The test client to simulate API requests.
        normal_user_token_headers (Dict[str, str]): The headers containing the normal user's authentication token.
        db (Session): The database session for database operations.
    """

    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_user = get_test_user(db)
    t_super = get_test_super_user(db)
    t_item = create_random_item(db, user=t_super)
    crud_bought_item.update_status(db, db_obj_user=t_super, db_obj_item=t_item, status=cfg.items.bought.status.ordered)

    data = {
        "project_id": t_item.project_id,
        "quantity": 1,
        "unit": cfg.items.bought.units.default,
        "partnumber": "TestPartNumber",
        "order_number": "TestOrderNumber",
        "manufacturer": "TestManufacturer",
    }

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.put(f"{UPDATE_ITEM_BY_ID}/{t_item.id}", headers=normal_user_token_headers, json=data)

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 403
    assert response.json()["detail"] == lang(t_user).API.BOUGHTITEM.CANNOT_CHANGE_PLANNED_ITEM


def test_update_item_by_id__super_user__already_planned(
    client: TestClient, super_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test updating an item by ID as a super user when the item is already planned.

    This test performs the following steps:
    1. Prepares the test by creating a super user and a random item associated with that user.
    2. Updates the status of the item to 'ordered'.
    3. Constructs the data payload for updating the item.
    4. Sends a PUT request to update the item by its ID.
    5. Validates the response to ensure the item was updated correctly.

    Args:
        client (TestClient): The test client to simulate API requests.
        super_user_token_headers (Dict[str, str]): The headers containing the super user token.
        db (Session): The database session for interacting with the database.

    Asserts:
        The response is not None.
        The response status code is 200.
        The response schema matches the expected item ID and status.
    """

    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_super = get_test_super_user(db)
    t_item = create_random_item(db, user=t_super)
    crud_bought_item.update_status(db, db_obj_user=t_super, db_obj_item=t_item, status=cfg.items.bought.status.ordered)

    data = {
        "project_id": t_item.project_id,
        "quantity": 1,
        "unit": cfg.items.bought.units.default,
        "partnumber": "TestPartNumber",
        "order_number": "TestOrderNumber",
        "manufacturer": "TestManufacturer",
    }

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.put(f"{UPDATE_ITEM_BY_ID}/{t_item.id}", headers=super_user_token_headers, json=data)
    responseSchema = BoughtItemSchema(**response.json())

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 200

    assert responseSchema
    assert responseSchema.id == t_item.id
    assert responseSchema.status == cfg.items.bought.status.ordered


def test_update_item_by_id__admin_user__already_planned(
    client: TestClient, admin_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test updating an item by ID for an admin user when the item is already planned.

    This test performs the following steps:
    1. Preparation:
        - Retrieves a test super user.
        - Creates a random item associated with the super user.
        - Updates the status of the created item to 'ordered'.
    2. Methods to Test:
        - Sends a PUT request to update the item with specific data.
        - Parses the response into a BoughtItemSchema.
    3. Validation:
        - Asserts that the response is valid and has a status code of 200.
        - Asserts that the response schema matches the expected item ID and status.

    Args:
        client (TestClient): The test client to send requests.
        admin_user_token_headers (Dict[str, str]): Headers containing the admin user's token.
        db (Session): The database session.
    """

    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_super = get_test_super_user(db)
    t_item = create_random_item(db, user=t_super)
    crud_bought_item.update_status(db, db_obj_user=t_super, db_obj_item=t_item, status=cfg.items.bought.status.ordered)

    data = {
        "project_id": t_item.project_id,
        "quantity": 1,
        "unit": cfg.items.bought.units.default,
        "partnumber": "TestPartNumber",
        "order_number": "TestOrderNumber",
        "manufacturer": "TestManufacturer",
    }

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.put(f"{UPDATE_ITEM_BY_ID}/{t_item.id}", headers=admin_user_token_headers, json=data)
    responseSchema = BoughtItemSchema(**response.json())

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 200

    assert responseSchema
    assert responseSchema.id == t_item.id
    assert responseSchema.status == cfg.items.bought.status.ordered


def test_update_item_by_id__guest_user(
    client: TestClient, guest_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test the update item by ID endpoint for a guest user.

    This test verifies that a guest user does not have permission to update an item by its ID.

    Args:
        client (TestClient): The test client to simulate API requests.
        guest_user_token_headers (Dict[str, str]): The headers containing the guest user's authentication token.
        db (Session): The database session for interacting with the test database.

    Preparation:
        - Create a random item in the database.
        - Define the data to update the item.

    Methods to Test:
        - Send a PUT request to update the item by its ID with the guest user's token.

    Validation:
        - Assert that the response is received.
        - Assert that the status code of the response is 403 (Forbidden).
        - Assert that the response contains the correct error message indicating no permission to update the item.
    """

    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_item = create_random_item(db)
    data = {
        "project_id": 1,
        "quantity": 1,
        "unit": cfg.items.bought.units.default,
        "partnumber": "TestPartNumber",
        "order_number": "TestOrderNumber",
        "manufacturer": "TestManufacturer",
    }

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.put(f"{UPDATE_ITEM_BY_ID}/{t_item.id}", headers=guest_user_token_headers, json=data)

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 403
    assert response.json()["detail"] == lang(get_test_user(db)).API.BOUGHTITEM.UPDATE_NO_PERMISSION
