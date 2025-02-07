"""
    TEST WEB API -- USERS -- CREATE USER
"""

from typing import Dict

from api.schemas.user import UserSchema
from config import cfg
from crud.user import crud_user
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.utils.user import TEST_USER_MAIL
from tests.utils.user import TEST_USER_USERNAME
from tests.utils.utils import random_email
from tests.utils.utils import random_lower_string
from tests.utils.utils import random_name
from tests.utils.utils import random_username

CREATE_USER_API = f"{cfg.server.api.web}/users"


def test_create_user__unauthorized(client: TestClient) -> None:
    # ----------------------------------------------
    # GET USER ME: METHODS TO TEST
    # ----------------------------------------------

    response = client.post(CREATE_USER_API, headers={})

    # ----------------------------------------------
    # GET OWN USER: VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 401


def test_create_user__normal_user(client: TestClient, normal_user_token_headers: Dict[str, str]) -> None:
    # ----------------------------------------------
    # GET USER ME: METHODS TO TEST
    # ----------------------------------------------

    response = client.post(CREATE_USER_API, headers=normal_user_token_headers)

    # ----------------------------------------------
    # GET OWN USER: VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 403


def test_create_user__super_user(client: TestClient, super_user_token_headers: Dict[str, str]) -> None:
    # ----------------------------------------------
    # GET USER ME: METHODS TO TEST
    # ----------------------------------------------

    response = client.post(CREATE_USER_API, headers=super_user_token_headers)

    # ----------------------------------------------
    # GET OWN USER: VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 403


def test_create_user__admin_user(client: TestClient, admin_user_token_headers: dict, db: Session) -> None:
    # ----------------------------------------------
    # CREATE USER: PREPARATION
    # ----------------------------------------------

    t_username = random_username()
    t_email = random_email()
    t_password = random_lower_string()
    t_full_name = random_name()
    t_data = {"email": t_email, "password": t_password, "username": t_username, "full_name": t_full_name}

    # ----------------------------------------------
    # CREATE USER: METHODS TO TEST
    # ----------------------------------------------

    response = client.post(CREATE_USER_API, headers=admin_user_token_headers, json=t_data)
    created_user = UserSchema(**response.json())

    # ----------------------------------------------
    # CREATE USER: VALIDATION
    # ----------------------------------------------

    db_user = crud_user.get_by_email(db, email=t_email)
    assert db_user

    assert response.status_code == 200

    assert created_user
    assert created_user.is_active == True
    assert created_user.id == db_user.id
    assert created_user.username == db_user.username == t_username
    assert created_user.email == db_user.email == t_email
    assert created_user.full_name == db_user.full_name == t_full_name


def test_create_user__system_user(client: TestClient, systemuser_token_headers: dict, db: Session) -> None:
    # ----------------------------------------------
    # CREATE USER: PREPARATION
    # ----------------------------------------------

    t_username = random_username()
    t_email = random_email()
    t_password = random_lower_string()
    t_full_name = random_name()
    t_data = {"email": t_email, "password": t_password, "username": t_username, "full_name": t_full_name}

    # ----------------------------------------------
    # CREATE USER: METHODS TO TEST
    # ----------------------------------------------

    response = client.post(CREATE_USER_API, headers=systemuser_token_headers, json=t_data)
    created_user = UserSchema(**response.json())

    # ----------------------------------------------
    # CREATE USER: VALIDATION
    # ----------------------------------------------

    db_user = crud_user.get_by_email(db, email=t_email)
    assert db_user

    assert response.status_code == 200

    assert created_user
    assert created_user.is_active == True
    assert created_user.id == db_user.id
    assert created_user.username == db_user.username == t_username
    assert created_user.email == db_user.email == t_email
    assert created_user.full_name == db_user.full_name == t_full_name


def test_create_user__admin_user__existing_username(client: TestClient, admin_user_token_headers: dict) -> None:
    # ----------------------------------------------
    # CREATE EXISTING USER: PREPARATION
    # ----------------------------------------------

    data = {
        "email": random_email(),
        "password": random_lower_string(),
        "username": TEST_USER_USERNAME,
        "full_name": random_name(),
    }

    # ----------------------------------------------
    # CREATE EXISTING USER: METHODS TO TEST
    # ----------------------------------------------

    response = client.post(CREATE_USER_API, headers=admin_user_token_headers, json=data)

    # ----------------------------------------------
    # CREATE EXISTING USER: VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 406


def test_create_user__admin_user__existing_mail(client: TestClient, admin_user_token_headers: dict) -> None:
    # ----------------------------------------------
    # CREATE EXISTING USER: PREPARATION
    # ----------------------------------------------

    data = {
        "email": TEST_USER_MAIL,
        "password": random_lower_string(),
        "username": random_username(),
        "full_name": random_name(),
    }

    # ----------------------------------------------
    # CREATE EXISTING USER: METHODS TO TEST
    # ----------------------------------------------

    response = client.post(CREATE_USER_API, headers=admin_user_token_headers, json=data)

    # ----------------------------------------------
    # CREATE EXISTING USER: VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 406


def test_create_user__admin_user__missing_data(client: TestClient, admin_user_token_headers: dict) -> None:
    # ----------------------------------------------
    # CREATE EXISTING USER: PREPARATION
    # ----------------------------------------------

    data = {
        "email": random_email(),
        "password": random_lower_string(),
        "full_name": random_name(),
    }

    # ----------------------------------------------
    # CREATE EXISTING USER: METHODS TO TEST
    # ----------------------------------------------

    response = client.post(CREATE_USER_API, headers=admin_user_token_headers, json=data)

    # ----------------------------------------------
    # CREATE EXISTING USER: VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 422
