"""
    TEST WEB API -- BOUGHT ITEMS -- READ CHANGELOG
"""

from string import Template
from typing import List

from config import cfg
from fastapi.testclient import TestClient
from locales import lang
from sqlalchemy.orm import Session

from tests.utils.bought_item import create_random_item
from tests.utils.user import get_test_user
from tests.utils.utils import random_bought_item_name
from tests.utils.utils import random_bought_item_order_number
from tests.utils.utils import random_manufacturer

READ_ITEM_CHANGELOG_BY_ID_API = Template(f"{cfg.server.api.web}/items/bought/$item_id/changelog")
JSON_ITEM_DATA = {
    "project_id": None,
    "quantity": 1,
    "unit": cfg.items.bought.units.default,
    "partnumber": random_bought_item_name(),
    "order_number": random_bought_item_order_number(),
    "manufacturer": random_manufacturer(),
}


def test_read_item_changelog_by_id__unauthorized(client: TestClient) -> None:
    """
    Test case for attempting to read an item changelog by ID without authorization.

    This test verifies that an unauthorized request to read an item changelog by ID
    returns a 401 Unauthorized status code and the appropriate error message.

    Args:
        client (TestClient): The test client used to make the request.

    Assertions:
        - The response object is not None.
        - The response status code is 401 Unauthorized.
        - The response JSON contains the detail message "Invalid access token".
    """

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.get(READ_ITEM_CHANGELOG_BY_ID_API.substitute(item_id=1), headers={})

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid access token"


def test_read_item_changelog_by_id__normal_user(
    client: TestClient, normal_user_token_headers: dict, db: Session
) -> None:
    """
    Test the endpoint to read the changelog of an item by its ID for a normal user.
    This test performs the following steps:
    1. Preparation:
        - Create a random item in the database.
    2. Methods to Test:
        - Send a GET request to the endpoint to read the changelog of the created item by its ID.
    3. Validation:
        - Assert that the response is not None.
        - Assert that the response status code is 200 (OK).
        - Assert that the response scheme is not empty.
        - Assert that the first entry in the response scheme contains the message "Item created.".
    Args:
        client (TestClient): The test client to simulate API requests.
        normal_user_token_headers (dict): The headers containing the normal user's authentication token.
        db (Session): The database session for database operations.
    """

    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    item = create_random_item(db)

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.get(READ_ITEM_CHANGELOG_BY_ID_API.substitute(item_id=item.id), headers=normal_user_token_headers)
    responseScheme: List[str] = response.json()

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 200

    assert responseScheme
    assert "Item created." in responseScheme[0]


def test_read_item_changelog_by_id__normal_user__not_found(
    client: TestClient, normal_user_token_headers: dict, db: Session
) -> None:
    """
    Test case for reading item changelog by ID as a normal user when the item is not found.

    This test ensures that when a normal user attempts to read the changelog of an item
    that does not exist, the API responds with a 404 status code and the appropriate error
    message.

    Args:
        client (TestClient): The test client to simulate API requests.
        normal_user_token_headers (dict): The headers containing the normal user's authentication token.
        db (Session): The database session for accessing the database.

    Asserts:
        response.status_code (int): The HTTP status code of the response should be 404.
        response.json()["detail"] (str): The error detail message should indicate that the item was not found.
    """

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.get(READ_ITEM_CHANGELOG_BY_ID_API.substitute(item_id=9999999), headers=normal_user_token_headers)

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response.status_code == 404
    assert response.json()["detail"] == lang(get_test_user(db)).API.BOUGHTITEM.ITEM_NOT_FOUND
