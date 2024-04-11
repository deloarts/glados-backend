import copy

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.config import cfg
from app.const import API_WEB_V1
from tests.utils.bought_item import create_random_item
from tests.utils.utils import random_lower_string
from tests.utils.utils import random_project

item_data = {
    "project": random_project(),
    "machine": None,
    "quantity": 1,
    "unit": cfg.items.bought.units.default,
    "partnumber": random_lower_string(),
    "definition": random_lower_string(),
    "manufacturer": random_lower_string(),
}


def test_create_item(client: TestClient, normal_user_token_headers: dict, db: Session) -> None:
    data = copy.deepcopy(item_data)
    response = client.post(
        f"{API_WEB_V1}/items/bought/",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()

    assert "id" in content
    assert "creator_id" in content

    assert content["project"] == data["project"]
    assert content["quantity"] == data["quantity"]
    assert content["unit"] == data["unit"]
    assert content["partnumber"] == data["partnumber"]
    assert content["definition"] == data["definition"]
    assert content["manufacturer"] == data["manufacturer"]


def test_create_item_missing_project(client: TestClient, normal_user_token_headers: dict, db: Session) -> None:
    data = copy.deepcopy(item_data)
    data.pop("project")
    response = client.post(
        f"{API_WEB_V1}/items/bought/",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == 422


def test_create_item_missing_quantity(client: TestClient, normal_user_token_headers: dict, db: Session) -> None:
    data = copy.deepcopy(item_data)
    data.pop("quantity")
    response = client.post(
        f"{API_WEB_V1}/items/bought/",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == 422


def test_create_item_wrong_quantity(client: TestClient, normal_user_token_headers: dict, db: Session) -> None:
    data = copy.deepcopy(item_data)
    data["quantity"] = -1
    response = client.post(
        f"{API_WEB_V1}/items/bought/",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == 422


def test_create_item_missing_unit(client: TestClient, normal_user_token_headers: dict, db: Session) -> None:
    data = copy.deepcopy(item_data)
    data.pop("unit")
    response = client.post(
        f"{API_WEB_V1}/items/bought/",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == 200
    assert response.json()["unit"] == cfg.items.bought.units.default


def test_create_item_wrong_unit(client: TestClient, normal_user_token_headers: dict, db: Session) -> None:
    data = copy.deepcopy(item_data)
    data["unit"] = "foo"
    response = client.post(
        f"{API_WEB_V1}/items/bought/",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == 422


def test_create_item_missing_partnumber(client: TestClient, normal_user_token_headers: dict, db: Session) -> None:
    data = copy.deepcopy(item_data)
    data.pop("partnumber")
    response = client.post(
        f"{API_WEB_V1}/items/bought/",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == 422


def test_create_item_missing_definition(client: TestClient, normal_user_token_headers: dict, db: Session) -> None:
    data = copy.deepcopy(item_data)
    data.pop("definition")
    response = client.post(
        f"{API_WEB_V1}/items/bought/",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == 422


def test_create_item_missing_manufacturer(client: TestClient, normal_user_token_headers: dict, db: Session) -> None:
    data = copy.deepcopy(item_data)
    data.pop("manufacturer")
    response = client.post(
        f"{API_WEB_V1}/items/bought/",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == 422


def test_create_item_extra_field(client: TestClient, normal_user_token_headers: dict, db: Session) -> None:
    data = copy.deepcopy(item_data)
    data["some_key"] = "some_value"

    response = client.post(
        f"{API_WEB_V1}/items/bought/",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == 200


def test_read_item(client: TestClient, normal_user_token_headers: dict, db: Session) -> None:
    item = create_random_item(db)
    response = client.get(
        f"{API_WEB_V1}/items/bought/{item.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 200
    content = response.json()

    assert content["id"] == item.id
    assert content["creator_id"] == item.creator_id

    assert content["project"] == item.project
    assert content["quantity"] == item.quantity
    assert content["unit"] == item.unit
    assert content["partnumber"] == item.partnumber
    assert content["definition"] == item.definition
    assert content["manufacturer"] == item.manufacturer
