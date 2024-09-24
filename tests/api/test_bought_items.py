import copy

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.config import cfg
from app.const import API_WEB_V1
from tests.utils.bought_item import create_random_item
from tests.utils.project import get_test_project
from tests.utils.utils import random_bought_item_name
from tests.utils.utils import random_bought_item_order_number
from tests.utils.utils import random_manufacturer

JSON_ITEM_DATA = {
    "project_id": None,
    "quantity": 1,
    "unit": cfg.items.bought.units.default,
    "partnumber": random_bought_item_name(),
    "order_number": random_bought_item_order_number(),
    "manufacturer": random_manufacturer(),
}


def test_create_item(client: TestClient, normal_user_token_headers: dict, db: Session) -> None:
    # ----------------------------------------------
    # CREATE ITEM: PREPARATION
    # ----------------------------------------------

    t_data = copy.deepcopy(JSON_ITEM_DATA)
    t_data["project_id"] = get_test_project(db).id

    # ----------------------------------------------
    # CREATE ITEM: METHODS TO TEST
    # ----------------------------------------------

    response = client.post(f"{API_WEB_V1}/items/bought/", headers=normal_user_token_headers, json=t_data)

    # ----------------------------------------------
    # CREATE ITEM: VALIDATION
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
    assert "machine" in content

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


def test_create_item_missing_project(client: TestClient, normal_user_token_headers: dict, db: Session) -> None:
    # ----------------------------------------------
    # CREATE ITEM MISSING PROJECT: PREPARATION
    # ----------------------------------------------

    t_data_1 = copy.deepcopy(JSON_ITEM_DATA)
    t_data_1.pop("project_id")

    t_data_2 = copy.deepcopy(JSON_ITEM_DATA)
    t_data_2["project_id"] = 999999999

    # ----------------------------------------------
    # CREATE ITEM MISSING PROJECT: METHODS TO TEST
    # ----------------------------------------------

    response_1 = client.post(f"{API_WEB_V1}/items/bought/", headers=normal_user_token_headers, json=t_data_1)
    response_2 = client.post(f"{API_WEB_V1}/items/bought/", headers=normal_user_token_headers, json=t_data_2)

    # ----------------------------------------------
    # CREATE ITEM MISSING PROJECT: VALIDATION
    # ----------------------------------------------

    assert response_1.status_code == 422
    assert response_2.status_code == 404


def test_create_item_missing_quantity(client: TestClient, normal_user_token_headers: dict, db: Session) -> None:
    # ----------------------------------------------
    # CREATE ITEM MISSING QTY: PREPARATION
    # ----------------------------------------------

    t_data_1 = copy.deepcopy(JSON_ITEM_DATA)
    t_data_1["project_id"] = get_test_project(db).id
    t_data_1.pop("quantity")

    t_data_2 = copy.deepcopy(JSON_ITEM_DATA)
    t_data_2["project_id"] = get_test_project(db).id
    t_data_2["quantity"] = "no a number"

    # ----------------------------------------------
    # CREATE ITEM MISSING QTY: METHODS TO TEST
    # ----------------------------------------------

    response_1 = client.post(f"{API_WEB_V1}/items/bought/", headers=normal_user_token_headers, json=t_data_1)
    response_2 = client.post(f"{API_WEB_V1}/items/bought/", headers=normal_user_token_headers, json=t_data_2)

    # ----------------------------------------------
    # CREATE ITEM MISSING QTY: VALIDATION
    # ----------------------------------------------

    assert response_1.status_code == 422
    assert response_2.status_code == 422


def test_create_item_missing_unit(client: TestClient, normal_user_token_headers: dict, db: Session) -> None:
    # ----------------------------------------------
    # CREATE ITEM MISSING UNIT: PREPARATION
    # ----------------------------------------------

    t_data_1 = copy.deepcopy(JSON_ITEM_DATA)
    t_data_1["project_id"] = get_test_project(db).id
    t_data_1.pop("unit")

    t_data_2 = copy.deepcopy(JSON_ITEM_DATA)
    t_data_2["project_id"] = get_test_project(db).id
    t_data_2["unit"] = "no a valid unit"

    # ----------------------------------------------
    # CREATE ITEM MISSING UNIT: METHODS TO TEST
    # ----------------------------------------------

    response_1 = client.post(f"{API_WEB_V1}/items/bought/", headers=normal_user_token_headers, json=t_data_1)
    response_2 = client.post(f"{API_WEB_V1}/items/bought/", headers=normal_user_token_headers, json=t_data_2)

    # ----------------------------------------------
    # CREATE ITEM MISSING UNIT: VALIDATION
    # ----------------------------------------------

    assert response_1.status_code == 200  # Missing unit will be replaced with default unit
    assert response_2.status_code == 422


def test_create_item_missing_partnumber(client: TestClient, normal_user_token_headers: dict, db: Session) -> None:
    # ----------------------------------------------
    # CREATE ITEM MISSING PARTNUMBER: PREPARATION
    # ----------------------------------------------

    t_data_1 = copy.deepcopy(JSON_ITEM_DATA)
    t_data_1["project_id"] = get_test_project(db).id
    t_data_1.pop("partnumber")

    # ----------------------------------------------
    # CREATE ITEM MISSING PARTNUMBER: METHODS TO TEST
    # ----------------------------------------------

    response_1 = client.post(f"{API_WEB_V1}/items/bought/", headers=normal_user_token_headers, json=t_data_1)

    # ----------------------------------------------
    # CREATE ITEM MISSING PARTNUMBER: VALIDATION
    # ----------------------------------------------

    assert response_1.status_code == 422


def test_create_item_missing_order_number(client: TestClient, normal_user_token_headers: dict, db: Session) -> None:
    # ----------------------------------------------
    # CREATE ITEM MISSING ORDER NUMBER: PREPARATION
    # ----------------------------------------------

    t_data_1 = copy.deepcopy(JSON_ITEM_DATA)
    t_data_1["project_id"] = get_test_project(db).id
    t_data_1.pop("order_number")

    # ----------------------------------------------
    # CREATE ITEM MISSING ORDER NUMBER: METHODS TO TEST
    # ----------------------------------------------

    response_1 = client.post(f"{API_WEB_V1}/items/bought/", headers=normal_user_token_headers, json=t_data_1)

    # ----------------------------------------------
    # CREATE ITEM MISSING ORDER NUMBER: VALIDATION
    # ----------------------------------------------

    assert response_1.status_code == 422


def test_create_item_missing_manufacturer(client: TestClient, normal_user_token_headers: dict, db: Session) -> None:
    # ----------------------------------------------
    # CREATE ITEM MISSING MANUFACTURER: PREPARATION
    # ----------------------------------------------

    t_data_1 = copy.deepcopy(JSON_ITEM_DATA)
    t_data_1["project_id"] = get_test_project(db).id
    t_data_1.pop("manufacturer")

    # ----------------------------------------------
    # CREATE ITEM MISSING MANUFACTURER: METHODS TO TEST
    # ----------------------------------------------

    response_1 = client.post(f"{API_WEB_V1}/items/bought/", headers=normal_user_token_headers, json=t_data_1)

    # ----------------------------------------------
    # CREATE ITEM MISSING MANUFACTURER: VALIDATION
    # ----------------------------------------------

    assert response_1.status_code == 422


def test_create_item_extra_field(client: TestClient, normal_user_token_headers: dict, db: Session) -> None:
    # ----------------------------------------------
    # CREATE ITEM EXTRA FIELD: PREPARATION
    # ----------------------------------------------

    t_data_1 = copy.deepcopy(JSON_ITEM_DATA)
    t_data_1["project_id"] = get_test_project(db).id
    t_data_1["some_non_db_field"] = "some_value"

    # ----------------------------------------------
    # CREATE ITEM EXTRA FIELD: METHODS TO TEST
    # ----------------------------------------------

    response_1 = client.post(f"{API_WEB_V1}/items/bought/", headers=normal_user_token_headers, json=t_data_1)

    # ----------------------------------------------
    # CREATE ITEM EXTRA FIELD: VALIDATION
    # ----------------------------------------------

    assert response_1.status_code == 200


def test_read_item(client: TestClient, normal_user_token_headers: dict, db: Session) -> None:
    # ----------------------------------------------
    # GET ITEM: PREPARATION
    # ----------------------------------------------

    item = create_random_item(db)

    # ----------------------------------------------
    # GET ITEM: METHODS TO TEST
    # ----------------------------------------------

    response = client.get(f"{API_WEB_V1}/items/bought/{item.id}", headers=normal_user_token_headers)

    # ----------------------------------------------
    # GET ITEM: VALIDATION
    # ----------------------------------------------

    assert response.status_code == 200
    content = response.json()

    assert content["id"] == item.id
    assert content["creator_id"] == item.creator_id

    assert content["project_id"] == item.project_id
    assert content["project_number"] == item.project_number

    assert content["quantity"] == item.quantity
    assert content["unit"] == item.unit
    assert content["partnumber"] == item.partnumber
    assert content["order_number"] == item.order_number
    assert content["manufacturer"] == item.manufacturer
