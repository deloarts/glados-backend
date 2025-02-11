"""
    TEST WEB API -- BOUGHT ITEMS -- UPDATE STATUS
"""

from string import Template
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

UPDATE_ITEM_STATUS = Template(f"{cfg.server.api.web}/items/bought/$item_id/status")


def test_update_item_status__unauthorized(client: TestClient, db: Session) -> None:

    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_item = create_random_item(db)

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.put(UPDATE_ITEM_STATUS.substitute(item_id=t_item.id), headers={})

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid access token"


def test_update_item_status__normal_user(
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
        UPDATE_ITEM_STATUS.substitute(item_id=t_item.id),
        headers=normal_user_token_headers,
        params={"status": cfg.items.bought.status.ordered},
    )
    responseScheme = BoughtItemSchema(**response.json())

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 200

    assert responseScheme
    assert responseScheme.id == t_item.id
    assert responseScheme.status == cfg.items.bought.status.ordered


def test_update_item_status__normal_user__unknown_status(
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
        UPDATE_ITEM_STATUS.substitute(item_id=t_item.id),
        headers=normal_user_token_headers,
        params={"status": "an_unknown_status"},
    )

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 403
    assert response.json()["detail"] == lang(get_test_user(db)).API.BOUGHTITEM.UNKNOWN_STATUS


def test_update_item_status__normal_user__back_to_open(
    client: TestClient, normal_user_token_headers: Dict[str, str], db: Session
) -> None:

    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_user = get_test_user(db)
    t_item = create_random_item(db)
    crud_bought_item.update_status(db, db_obj_user=t_user, db_obj_item=t_item, status=cfg.items.bought.status.requested)

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.put(
        UPDATE_ITEM_STATUS.substitute(item_id=t_item.id),
        headers=normal_user_token_headers,
        params={"status": cfg.items.bought.status.open},
    )

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 403
    assert response.json()["detail"] == lang(t_user).API.BOUGHTITEM.CANNOT_CHANGE_TO_OPEN


def test_update_item_status__normal_user__of_another_user(
    client: TestClient, normal_user_token_headers: Dict[str, str], db: Session
) -> None:

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
        UPDATE_ITEM_STATUS.substitute(item_id=t_item.id),
        headers=normal_user_token_headers,
        params={"status": cfg.items.bought.status.requested},
    )

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 403
    assert response.json()["detail"] == lang(t_user).API.BOUGHTITEM.CANNOT_CHANGE_OTHER_USER_ITEM


def test_update_item_status__super_user__of_another_user(
    client: TestClient, super_user_token_headers: Dict[str, str], db: Session
) -> None:

    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_super = get_test_super_user(db)
    t_item = create_random_item(db, user=t_super)

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.put(
        UPDATE_ITEM_STATUS.substitute(item_id=t_item.id),
        headers=super_user_token_headers,
        params={"status": cfg.items.bought.status.requested},
    )
    responseSchema = BoughtItemSchema(**response.json())

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 200

    assert responseSchema
    assert responseSchema.status == cfg.items.bought.status.requested


def test_update_item_status__admin_user__of_another_user(
    client: TestClient, admin_user_token_headers: Dict[str, str], db: Session
) -> None:

    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_super = get_test_super_user(db)
    t_item = create_random_item(db, user=t_super)

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.put(
        UPDATE_ITEM_STATUS.substitute(item_id=t_item.id),
        headers=admin_user_token_headers,
        params={"status": cfg.items.bought.status.requested},
    )
    responseSchema = BoughtItemSchema(**response.json())

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 200

    assert responseSchema
    assert responseSchema.status == cfg.items.bought.status.requested
