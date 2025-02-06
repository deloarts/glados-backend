"""
    TEST WEB API -- USERS -- READ USER BY ID
"""

from api.schemas.user import UserSchema
from config import cfg
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.utils.user import get_test_user

READ_USER_BY_ID_API = f"{cfg.server.api.web}/users"


def test_read_user_by_id__unauthorized(client: TestClient, db: Session) -> None:
    # ----------------------------------------------
    # READ USER BY ID: PREPARATION
    # ----------------------------------------------

    t_user = get_test_user(db)

    # ----------------------------------------------
    # READ USER BY ID: METHODS TO TEST
    # ----------------------------------------------

    response = client.get(f"{READ_USER_BY_ID_API}/{t_user.id}", headers={})

    # ----------------------------------------------
    # READ USER BY ID: VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 401


def test_read_user_by_id__normal_user(client: TestClient, normal_user_token_headers: dict, db: Session) -> None:
    # ----------------------------------------------
    # READ USER BY ID: PREPARATION
    # ----------------------------------------------

    t_user = get_test_user(db)

    # ----------------------------------------------
    # READ USER BY ID: METHODS TO TEST
    # ----------------------------------------------

    response = client.get(f"{READ_USER_BY_ID_API}/{t_user.id}", headers=normal_user_token_headers)
    response_schema = UserSchema(**response.json())

    # ----------------------------------------------
    # READ USER BY ID: VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 200

    assert response_schema
    assert response_schema.id == t_user.id
    assert response_schema.email == t_user.email
    assert response_schema.username == t_user.username


def test_read_user_by_id__super_user(client: TestClient, super_user_token_headers: dict, db: Session) -> None:
    # ----------------------------------------------
    # READ USER BY ID: PREPARATION
    # ----------------------------------------------

    t_user = get_test_user(db)

    # ----------------------------------------------
    # READ USER BY ID: METHODS TO TEST
    # ----------------------------------------------

    response = client.get(f"{READ_USER_BY_ID_API}/{t_user.id}", headers=super_user_token_headers)
    response_schema = UserSchema(**response.json())

    # ----------------------------------------------
    # READ USER BY ID: VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 200

    assert response_schema
    assert response_schema.id == t_user.id
    assert response_schema.email == t_user.email
    assert response_schema.username == t_user.username


def test_read_user_by_id__admin_user(client: TestClient, admin_user_token_headers: dict, db: Session) -> None:
    # ----------------------------------------------
    # READ USER BY ID: PREPARATION
    # ----------------------------------------------

    t_user = get_test_user(db)

    # ----------------------------------------------
    # READ USER BY ID: METHODS TO TEST
    # ----------------------------------------------

    response = client.get(f"{READ_USER_BY_ID_API}/{t_user.id}", headers=admin_user_token_headers)
    response_schema = UserSchema(**response.json())

    # ----------------------------------------------
    # READ USER BY ID: VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 200

    assert response_schema
    assert response_schema.id == t_user.id
    assert response_schema.email == t_user.email
    assert response_schema.username == t_user.username


def test_read_user_by_id__guest_user(client: TestClient, guest_user_token_headers: dict, db: Session) -> None:
    # ----------------------------------------------
    # READ USER BY ID: PREPARATION
    # ----------------------------------------------

    t_user = get_test_user(db)

    # ----------------------------------------------
    # READ USER BY ID: METHODS TO TEST
    # ----------------------------------------------

    response = client.get(f"{READ_USER_BY_ID_API}/{t_user.id}", headers=guest_user_token_headers)
    response_schema = UserSchema(**response.json())

    # ----------------------------------------------
    # READ USER BY ID: VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 200

    assert response_schema
    assert response_schema.id == t_user.id
    assert response_schema.email == t_user.email
    assert response_schema.username == t_user.username


def test_read_user_by_id__system_user(client: TestClient, systemuser_token_headers: dict, db: Session) -> None:
    # ----------------------------------------------
    # READ USER BY ID: PREPARATION
    # ----------------------------------------------

    t_user = get_test_user(db)

    # ----------------------------------------------
    # READ USER BY ID: METHODS TO TEST
    # ----------------------------------------------

    response = client.get(f"{READ_USER_BY_ID_API}/{t_user.id}", headers=systemuser_token_headers)
    response_schema = UserSchema(**response.json())

    # ----------------------------------------------
    # READ USER BY ID: VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 200

    assert response_schema
    assert response_schema.id == t_user.id
    assert response_schema.email == t_user.email
    assert response_schema.username == t_user.username
