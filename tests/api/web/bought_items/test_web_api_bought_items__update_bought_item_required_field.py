"""
    TEST WEB API -- BOUGHT ITEMS -- UPDATE REQUIRED FIELD
"""

from string import Template
from typing import Dict
from typing import List

from api.schemas.bought_item import BoughtItemSchema
from api.v1.web.endpoints.bought_items import RequiredFieldName
from config import cfg
from fastapi.testclient import TestClient
from httpx import Response
from locales import lang
from sqlalchemy.orm import Session

from tests.utils.bought_item import create_random_item
from tests.utils.user import get_test_super_user
from tests.utils.user import get_test_user
from tests.utils.utils import random_lower_string

UPDATE_ITEM_REQUIRED_FIELD = Template(f"{cfg.server.api.web}/items/bought/$item_id/field/required/$field_name")


def test_update_item_required_field__unauthorized(client: TestClient, db: Session) -> None:
    """
    Test the update item required field endpoint for unauthorized access.
    This test ensures that when an unauthorized request is made to update
    a required field of an item, the response status code is 401 and the
    response contains the appropriate error message.

    Args:
        client (TestClient): The test client used to make HTTP requests.
        db (Session): The database session used to interact with the database.

    Steps:
        1. Create a random item in the database.
        2. Attempt to update each required field of the item without authorization.
        3. Collect the responses for each update attempt.
        4. Validate that each response has a status code of 401 and the error
           message "Invalid access token".

    Asserts:
        - Each response is not None.
        - Each response status code is 401.
        - Each response contains the error message "Invalid access token".
    """

    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_item = create_random_item(db)

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    responses: List[Response] = []
    for field in RequiredFieldName:
        responses.append(
            client.put(UPDATE_ITEM_REQUIRED_FIELD.substitute(item_id=t_item.id, field_name=field.value), headers={})
        )

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    for response in responses:
        assert response
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid access token"


def test_update_item_required_field__normal_user(
    client: TestClient, normal_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test updating a required field of an item as a normal user.
    This test performs the following steps:
    1. Preparation:
        - Create a random item in the database.
        - Generate a random string value to update the item's field.
    2. Methods to Test:
        - Iterate over each required field name.
        - Send a PUT request to update the item's required field with the generated value.
        - Parse the response into a schema.
    3. Validation:
        - Assert that the response is successful.
        - Assert that the status code is 200.
        - Assert that the updated field in the response matches the generated value.
        - Assert that the response schema is valid.

    Args:
        client (TestClient): The test client to send requests.
        normal_user_token_headers (Dict[str, str]): The headers for a normal user's authentication token.
        db (Session): The database session.
    """
    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_item = create_random_item(db)
    t_value = random_lower_string()

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    for field in RequiredFieldName:
        response = client.put(
            UPDATE_ITEM_REQUIRED_FIELD.substitute(item_id=t_item.id, field_name=field.value),
            headers=normal_user_token_headers,
            params={"value": t_value},
        )
        responseSchema = BoughtItemSchema(**response.json())

        # ----------------------------------------------
        # VALIDATION
        # ----------------------------------------------

        assert response
        assert response.status_code == 200
        assert response.json()[str(field.value).replace("-", "_")] == t_value

        assert responseSchema


def test_update_item_required_field__normal_user__value_not_set(
    client: TestClient, normal_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test updating an item with a required field not set for a normal user.
    This test ensures that when a normal user attempts to update an item with a required field
    but does not provide a value, the API responds with a 406 status code and the appropriate
    error message.

    Args:
        client (TestClient): The test client to simulate API requests.
        normal_user_token_headers (Dict[str, str]): The headers containing the normal user's authentication token.
        db (Session): The database session.

    Steps:
        1. Create a random item in the database.
        2. Iterate over each required field.
        3. Attempt to update the item with an empty value for the required field.
        4. Validate that the response status code is 406.
        5. Validate that the response contains the correct error message indicating the value must be set.

    Asserts:
        - The response is not None.
        - The response status code is 406.
        - The response JSON contains the correct error message.
    """
    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_item = create_random_item(db)

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    for field in RequiredFieldName:
        response = client.put(
            UPDATE_ITEM_REQUIRED_FIELD.substitute(item_id=t_item.id, field_name=field.value),
            headers=normal_user_token_headers,
            params={"value": ""},
        )

        # ----------------------------------------------
        # VALIDATION
        # ----------------------------------------------

        assert response
        assert response.status_code == 406
        assert response.json()["detail"] == lang(get_test_user(db)).API.BOUGHTITEM.VALUE_MUST_BE_SET


def test_update_item_required_field__normal_user__unknown_field(
    client: TestClient, normal_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test updating an item with a required field using a normal user and an unknown field name.
    This test ensures that when a normal user attempts to update an item with an unknown field name,
    the API responds with a 422 Unprocessable Entity status code and the appropriate error details.

    Args:
        client (TestClient): The test client to simulate API requests.
        normal_user_token_headers (Dict[str, str]): The headers containing the normal user's authentication token.
        db (Session): The database session for creating and querying items.

    Assertions:
        - The response is not None.
        - The response status code is 422.
        - The error detail in the response JSON indicates that the issue is with the "field_name" in the path.
    """
    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_item = create_random_item(db)

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.put(
        UPDATE_ITEM_REQUIRED_FIELD.substitute(item_id=t_item.id, field_name="unknown-field"),
        headers=normal_user_token_headers,
        params={"value": "Foo Bar"},
    )

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"][0] == "path"
    assert response.json()["detail"][0]["loc"][1] == "field_name"


def test_update_item_required_field__normal_user__of_another_user(
    client: TestClient, normal_user_token_headers: Dict[str, str], db: Session
) -> None:
    """
    Test the update of a required field of an item by a normal user who is not the owner of the item.
    This test ensures that a normal user cannot update a required field of an item that belongs to another user.
    It verifies that the response status code is 403 Forbidden and the response contains the appropriate error message.

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
    t_value = random_lower_string()

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    for field in RequiredFieldName:
        response = client.put(
            UPDATE_ITEM_REQUIRED_FIELD.substitute(item_id=t_item.id, field_name=field.value),
            headers=normal_user_token_headers,
            params={"value": t_value},
        )

        # ----------------------------------------------
        # VALIDATION
        # ----------------------------------------------

        assert response
        assert response.status_code == 403
        assert response.json()["detail"] == lang(t_user).API.BOUGHTITEM.CANNOT_CHANGE_OTHER_USER_ITEM
