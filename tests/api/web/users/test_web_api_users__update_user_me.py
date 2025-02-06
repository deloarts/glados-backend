"""
    TEST WEB API -- USERS -- UPDATE USER ME
"""

from typing import Dict

from api.schemas.user import UserSchema
from config import cfg
from const import SYSTEM_USER
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.utils.user import TEST_ADMIN_MAIL
from tests.utils.user import TEST_GUEST_MAIL
from tests.utils.user import TEST_MAIL
from tests.utils.user import TEST_SUPER_MAIL
from tests.utils.user import get_test_admin_user
from tests.utils.user import get_test_guest_user
from tests.utils.user import get_test_super_user
from tests.utils.user import get_test_user

UPDATE_USER_ME_API = f"{cfg.server.api.web}/users/me"


def test_update_user_me__unauthorized(client: TestClient) -> None:
    # ----------------------------------------------
    # UPDATE USER ME: METHODS TO TEST
    # ----------------------------------------------

    response = client.put(UPDATE_USER_ME_API, headers={})

    # ----------------------------------------------
    # GET OWN USER: VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 401


def test_update_user_me__normal_user(
    client: TestClient, normal_user_token_headers: Dict[str, str], db: Session
) -> None:
    # ----------------------------------------------
    # UPDATE USER ME: PREPARATION
    # ----------------------------------------------

    t_user = get_test_user(db)
    data = {
        "email": t_user.email,
        "username": t_user.username,
        "full_name": t_user.full_name,
        "is_active": False,
        "is_superuser": True,
        "is_adminuser": True,
        "is_guestuser": True,
        "is_systemuser": True,
    }

    # ----------------------------------------------
    # UPDATE USER ME: METHODS TO TEST
    # ----------------------------------------------

    response = client.put(UPDATE_USER_ME_API, headers=normal_user_token_headers, json=data)
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
    assert response_schema.email == TEST_MAIL


def test_update_user_me__super_user(client: TestClient, super_user_token_headers: Dict[str, str], db: Session) -> None:
    # ----------------------------------------------
    # UPDATE USER ME: PREPARATION
    # ----------------------------------------------

    t_user = get_test_super_user(db)
    data = {
        "email": t_user.email,
        "username": t_user.username,
        "full_name": t_user.full_name,
        "is_active": False,
        "is_superuser": False,
        "is_adminuser": True,
        "is_guestuser": True,
        "is_systemuser": True,
    }

    # ----------------------------------------------
    # UPDATE USER ME: METHODS TO TEST
    # ----------------------------------------------

    response = client.put(UPDATE_USER_ME_API, headers=super_user_token_headers, json=data)
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


def test_update_user_me__admin_user(client: TestClient, admin_user_token_headers: Dict[str, str], db: Session) -> None:
    # ----------------------------------------------
    # UPDATE USER ME: PREPARATION
    # ----------------------------------------------

    t_user = get_test_admin_user(db)
    data = {
        "email": t_user.email,
        "username": t_user.username,
        "full_name": t_user.full_name,
        "is_active": False,
        "is_superuser": False,
        "is_adminuser": False,
        "is_guestuser": True,
        "is_systemuser": True,
    }

    # ----------------------------------------------
    # UPDATE USER ME: METHODS TO TEST
    # ----------------------------------------------

    response = client.put(UPDATE_USER_ME_API, headers=admin_user_token_headers, json=data)
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


def test_update_user_me__guest_user(client: TestClient, guest_user_token_headers: Dict[str, str], db: Session) -> None:
    # ----------------------------------------------
    # UPDATE USER ME: PREPARATION
    # ----------------------------------------------

    t_user = get_test_guest_user(db)
    data = {
        "email": t_user.email,
        "username": t_user.username,
        "full_name": t_user.full_name,
        "is_active": False,
        "is_superuser": True,
        "is_adminuser": True,
        "is_guestuser": True,
        "is_systemuser": True,
    }

    # ----------------------------------------------
    # UPDATE USER ME: METHODS TO TEST
    # ----------------------------------------------

    response = client.put(UPDATE_USER_ME_API, headers=guest_user_token_headers, json=data)
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


def test_update_user_me__system_user(client: TestClient, systemuser_token_headers: Dict[str, str]) -> None:
    # ----------------------------------------------
    # UPDATE USER ME: PREPARATION
    # ----------------------------------------------

    data = {
        "email": cfg.init.mail,
        "username": SYSTEM_USER,
        "full_name": cfg.init.full_name,
        "is_active": False,
        "is_superuser": False,
        "is_adminuser": False,
        "is_guestuser": True,
        "is_systemuser": False,
    }

    # ----------------------------------------------
    # UPDATE USER ME: METHODS TO TEST
    # ----------------------------------------------

    response = client.put(UPDATE_USER_ME_API, headers=systemuser_token_headers, json=data)
    response_schema = UserSchema(**response.json())

    # ----------------------------------------------
    # UPDATE USER ME: VALIDATION
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


def test_update_user_me__normal_user__password_criteria(
    client: TestClient, normal_user_token_headers: Dict[str, str], db: Session
) -> None:
    # ----------------------------------------------
    # UPDATE USER ME: PREPARATION
    # ----------------------------------------------

    t_user = get_test_user(db)
    successful_data = {
        "email": t_user.email,
        "username": t_user.username,
    }
    unsuccessful_data = {
        "email": t_user.email,
        "username": t_user.username,
        "password": "1234567",
    }

    # ----------------------------------------------
    # UPDATE USER ME: METHODS TO TEST
    # ----------------------------------------------

    successful_response = client.put(UPDATE_USER_ME_API, headers=normal_user_token_headers, json=successful_data)
    unsuccessful_response = client.put(UPDATE_USER_ME_API, headers=normal_user_token_headers, json=unsuccessful_data)

    # ----------------------------------------------
    # GET OWN USER: VALIDATION
    # ----------------------------------------------

    assert successful_response
    assert successful_response.status_code == 200

    assert unsuccessful_response
    assert unsuccessful_response.status_code == 422


def test_update_user_me__normal_user__username_exists(
    client: TestClient, normal_user_token_headers: Dict[str, str], db: Session
) -> None:
    # ----------------------------------------------
    # UPDATE USER ME: PREPARATION
    # ----------------------------------------------

    t_user = get_test_user(db)
    t_admin_user = get_test_admin_user(db)

    successful_data = {
        "email": t_user.email,
        "username": t_user.username,
    }
    unsuccessful_data = {
        "email": t_user.email,
        "username": t_admin_user.username,
    }

    # ----------------------------------------------
    # UPDATE USER ME: METHODS TO TEST
    # ----------------------------------------------

    successful_response = client.put(UPDATE_USER_ME_API, headers=normal_user_token_headers, json=successful_data)
    unsuccessful_response = client.put(UPDATE_USER_ME_API, headers=normal_user_token_headers, json=unsuccessful_data)

    # ----------------------------------------------
    # GET OWN USER: VALIDATION
    # ----------------------------------------------

    assert successful_response
    assert successful_response.status_code == 200

    assert unsuccessful_response
    assert unsuccessful_response.status_code == 406


def test_update_user_me__normal_user__email_exists(
    client: TestClient, normal_user_token_headers: Dict[str, str], db: Session
) -> None:
    # ----------------------------------------------
    # UPDATE USER ME: PREPARATION
    # ----------------------------------------------

    t_user = get_test_user(db)
    t_admin_user = get_test_admin_user(db)

    successful_data = {
        "email": t_user.email,
        "username": t_user.username,
    }
    unsuccessful_data = {
        "email": t_admin_user.email,
        "username": t_user.username,
    }

    # ----------------------------------------------
    # UPDATE USER ME: METHODS TO TEST
    # ----------------------------------------------

    successful_response = client.put(UPDATE_USER_ME_API, headers=normal_user_token_headers, json=successful_data)
    unsuccessful_response = client.put(UPDATE_USER_ME_API, headers=normal_user_token_headers, json=unsuccessful_data)

    # ----------------------------------------------
    # GET OWN USER: VALIDATION
    # ----------------------------------------------

    assert successful_response
    assert successful_response.status_code == 200

    assert unsuccessful_response
    assert unsuccessful_response.status_code == 406
