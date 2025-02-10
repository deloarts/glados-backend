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

    assert response.status_code == 200

    assert responseScheme.id == item.id
    assert responseScheme.creator_id == item.creator_id

    assert responseScheme.project_id == item.project_id
    assert responseScheme.project_number == item.project_number

    assert responseScheme.quantity == item.quantity
    assert responseScheme.unit == item.unit
    assert responseScheme.partnumber == item.partnumber
    assert responseScheme.order_number == item.order_number
    assert responseScheme.manufacturer == item.manufacturer


def test_read_item_by_id__normal_user__not_found(
    client: TestClient, normal_user_token_headers: dict, db: Session
) -> None:

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
