"""
    TEST WEB API -- USERS -- READ USER ME
"""

from typing import Dict

from api.schemas.user import UserSchema
from config import cfg
from const import SYSTEM_USER
from fastapi.testclient import TestClient

from tests.utils.user import TEST_ADMIN_MAIL
from tests.utils.user import TEST_GUEST_MAIL
from tests.utils.user import TEST_SUPER_MAIL
from tests.utils.user import TEST_USER_MAIL

READ_USER_ME_API = f"{cfg.server.api.web}/users/me"


def test_read_user_me__unauthorized(client: TestClient) -> None:
    # ----------------------------------------------
    # GET USER ME: METHODS TO TEST
    # ----------------------------------------------

    response = client.get(READ_USER_ME_API, headers={})

    # ----------------------------------------------
    # GET OWN USER: VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 401


def test_read_user_me__normal_user(client: TestClient, normal_user_token_headers: Dict[str, str]) -> None:
    # ----------------------------------------------
    # GET USER ME: METHODS TO TEST
    # ----------------------------------------------

    response = client.get(READ_USER_ME_API, headers=normal_user_token_headers)
    response_schema = UserSchema(**response.json())

    # ----------------------------------------------
    # GET OWN USER: VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 200

    assert response_schema
    assert response_schema.is_active is True
    assert response_schema.is_superuser is False
    assert response_schema.is_adminuser is False
    assert response_schema.is_systemuser is False
    assert response_schema.is_guestuser is False
    assert response_schema.email == TEST_USER_MAIL


def test_read_user_me__super_user(client: TestClient, super_user_token_headers: Dict[str, str]) -> None:
    # ----------------------------------------------
    # GET USER ME: METHODS TO TEST
    # ----------------------------------------------

    response = client.get(READ_USER_ME_API, headers=super_user_token_headers)
    response_schema = UserSchema(**response.json())

    # ----------------------------------------------
    # GET OWN USER: VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 200

    assert response_schema
    assert response_schema.is_active is True
    assert response_schema.is_superuser is True
    assert response_schema.is_adminuser is False
    assert response_schema.is_systemuser is False
    assert response_schema.is_guestuser is False
    assert response_schema.email == TEST_SUPER_MAIL


def test_read_user_me__admin_user(client: TestClient, admin_user_token_headers: Dict[str, str]) -> None:
    # ----------------------------------------------
    # GET USER ME: METHODS TO TEST
    # ----------------------------------------------

    response = client.get(READ_USER_ME_API, headers=admin_user_token_headers)
    response_schema = UserSchema(**response.json())

    # ----------------------------------------------
    # GET OWN USER: VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 200

    assert response_schema
    assert response_schema.is_active is True
    assert response_schema.is_superuser is True
    assert response_schema.is_adminuser is True
    assert response_schema.is_systemuser is False
    assert response_schema.is_guestuser is False
    assert response_schema.email == TEST_ADMIN_MAIL


def test_read_user_me__guest_user(client: TestClient, guest_user_token_headers: Dict[str, str]) -> None:
    # ----------------------------------------------
    # GET USER ME: METHODS TO TEST
    # ----------------------------------------------

    response = client.get(READ_USER_ME_API, headers=guest_user_token_headers)
    response_schema = UserSchema(**response.json())

    # ----------------------------------------------
    # GET OWN USER: VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 200

    assert response_schema
    assert response_schema.is_active is True
    assert response_schema.is_superuser is False
    assert response_schema.is_adminuser is False
    assert response_schema.is_systemuser is False
    assert response_schema.is_guestuser is True
    assert response_schema.email == TEST_GUEST_MAIL


def test_read_user_me__system_user(client: TestClient, systemuser_token_headers: Dict[str, str]) -> None:
    # ----------------------------------------------
    # GET USER ME: METHODS TO TEST
    # ----------------------------------------------

    response = client.get(READ_USER_ME_API, headers=systemuser_token_headers)
    response_schema = UserSchema(**response.json())

    # ----------------------------------------------
    # GET USER ME: VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 200

    assert response_schema
    assert response_schema.is_active is True
    assert response_schema.is_superuser is True
    assert response_schema.is_adminuser is True
    assert response_schema.is_systemuser is True
    assert response_schema.is_guestuser is False
    assert response_schema.username == SYSTEM_USER
