"""
    TEST WEB API -- USERS -- READ USERS
"""

from api.schemas.user import UserSchema
from config import cfg
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

READ_USERS_API = f"{cfg.server.api.web}/users"


def test_read_users__unauthorized(client: TestClient) -> None:
    # ----------------------------------------------
    # READ USERS: METHODS TO TEST
    # ----------------------------------------------

    response = client.get(READ_USERS_API, headers={})

    # ----------------------------------------------
    # READ USERS: VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 401


def test_read_users__normal_user(client: TestClient, normal_user_token_headers: dict, db: Session) -> None:
    # ----------------------------------------------
    # READ USERS: METHODS TO TEST
    # ----------------------------------------------

    response = client.get(READ_USERS_API, headers=normal_user_token_headers)
    response_schema = [UserSchema(**item) for item in response.json()]

    # ----------------------------------------------
    # READ USERS: VALIDATION
    # ----------------------------------------------

    assert response_schema
    assert len(response_schema) > 4
    for user in response_schema:
        assert user.email
        assert user.username
        assert user.full_name


def test_read_users__super_user(client: TestClient, super_user_token_headers: dict, db: Session) -> None:
    # ----------------------------------------------
    # READ USERS: METHODS TO TEST
    # ----------------------------------------------

    response = client.get(READ_USERS_API, headers=super_user_token_headers)
    response_schema = [UserSchema(**item) for item in response.json()]

    # ----------------------------------------------
    # READ USERS: VALIDATION
    # ----------------------------------------------

    assert response_schema
    assert len(response_schema) > 4
    for user in response_schema:
        assert user.email
        assert user.username
        assert user.full_name


def test_read_users__admin_user(client: TestClient, admin_user_token_headers: dict, db: Session) -> None:
    # ----------------------------------------------
    # READ USERS: METHODS TO TEST
    # ----------------------------------------------

    response = client.get(READ_USERS_API, headers=admin_user_token_headers)
    response_schema = [UserSchema(**item) for item in response.json()]

    # ----------------------------------------------
    # READ USERS: VALIDATION
    # ----------------------------------------------

    assert response_schema
    assert len(response_schema) > 4
    for user in response_schema:
        assert user.email
        assert user.username
        assert user.full_name


def test_read_users__guest_user(client: TestClient, guest_user_token_headers: dict, db: Session) -> None:
    # ----------------------------------------------
    # READ USERS: METHODS TO TEST
    # ----------------------------------------------

    response = client.get(READ_USERS_API, headers=guest_user_token_headers)
    response_schema = [UserSchema(**item) for item in response.json()]

    # ----------------------------------------------
    # READ USERS: VALIDATION
    # ----------------------------------------------

    assert response_schema
    assert len(response_schema) > 4
    for user in response_schema:
        assert user.email
        assert user.username
        assert user.full_name


def test_read_users__system_user(client: TestClient, systemuser_token_headers: dict, db: Session) -> None:
    # ----------------------------------------------
    # READ USERS: METHODS TO TEST
    # ----------------------------------------------

    response = client.get(READ_USERS_API, headers=systemuser_token_headers)
    response_schema = [UserSchema(**item) for item in response.json()]

    # ----------------------------------------------
    # READ USERS: VALIDATION
    # ----------------------------------------------

    assert response_schema
    assert len(response_schema) > 4
    for user in response_schema:
        assert user.email
        assert user.username
        assert user.full_name
