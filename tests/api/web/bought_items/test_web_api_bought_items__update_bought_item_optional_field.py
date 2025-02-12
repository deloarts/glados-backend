"""
    TEST WEB API -- BOUGHT ITEMS -- UPDATE OPTIONAL FIELD
"""

from string import Template
from typing import Dict
from typing import List

from api.schemas.bought_item import BoughtItemSchema
from api.v1.web.endpoints.bought_items import OptionalFieldName
from config import cfg
from fastapi.testclient import TestClient
from httpx import Response
from locales import lang
from sqlalchemy.orm import Session

from tests.utils.bought_item import create_random_item
from tests.utils.user import get_test_super_user
from tests.utils.user import get_test_user
from tests.utils.utils import random_lower_string

UPDATE_ITEM_OPTIONAL_FIELD = Template(f"{cfg.server.api.web}/items/bought/$item_id/field/optional/$field_name")


def test_update_item_optional_field__unauthorized(client: TestClient, db: Session) -> None:
    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_item = create_random_item(db)

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    responses: List[Response] = []
    for field in OptionalFieldName:
        responses.append(
            client.put(UPDATE_ITEM_OPTIONAL_FIELD.substitute(item_id=t_item.id, field_name=field.value), headers={})
        )

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    for response in responses:
        assert response
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid access token"


def test_update_item_optional_field__normal_user(
    client: TestClient, normal_user_token_headers: Dict[str, str], db: Session
) -> None:
    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_item = create_random_item(db)
    t_value = random_lower_string()

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    for field in OptionalFieldName:
        response = client.put(
            UPDATE_ITEM_OPTIONAL_FIELD.substitute(item_id=t_item.id, field_name=field.value),
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


def test_update_item_optional_field__normal_user__value_not_set(
    client: TestClient, normal_user_token_headers: Dict[str, str], db: Session
) -> None:
    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_item = create_random_item(db)

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    for field in OptionalFieldName:
        response = client.put(
            UPDATE_ITEM_OPTIONAL_FIELD.substitute(item_id=t_item.id, field_name=field.value),
            headers=normal_user_token_headers,
            params={"value": ""},
        )
        responseSchema = BoughtItemSchema(**response.json())

        # ----------------------------------------------
        # VALIDATION
        # ----------------------------------------------

        assert response
        assert response.status_code == 200
        assert response.json()[str(field.value).replace("-", "_")] == ""

        assert responseSchema


def test_update_item_optional_field__normal_user__unknown_field(
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
        UPDATE_ITEM_OPTIONAL_FIELD.substitute(item_id=t_item.id, field_name="unknown-field"),
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


def test_update_item_optional_field__normal_user__of_another_user(
    client: TestClient, normal_user_token_headers: Dict[str, str], db: Session
) -> None:
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

    for field in OptionalFieldName:
        response = client.put(
            UPDATE_ITEM_OPTIONAL_FIELD.substitute(item_id=t_item.id, field_name=field.value),
            headers=normal_user_token_headers,
            params={"value": t_value},
        )

        # ----------------------------------------------
        # VALIDATION
        # ----------------------------------------------

        assert response
        assert response.status_code == 403
        assert response.json()["detail"] == lang(t_user).API.BOUGHTITEM.CANNOT_CHANGE_OTHER_USER_ITEM
