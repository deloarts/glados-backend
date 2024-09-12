from typing import Dict

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.const import API_WEB_V1
from app.const import SYSTEM_USER
from app.crud.user import crud_user
from tests.utils.user import TEST_MAIL
from tests.utils.user import get_test_user
from tests.utils.utils import random_email
from tests.utils.utils import random_lower_string
from tests.utils.utils import random_name
from tests.utils.utils import random_username


def test_get_users_systemuser_init(client: TestClient, systemuser_token_headers: Dict[str, str]) -> None:
    # ----------------------------------------------
    # GET SYSTEMUSER: METHODS TO TEST
    # ----------------------------------------------

    r = client.get(f"{API_WEB_V1}/users/me", headers=systemuser_token_headers)

    # ----------------------------------------------
    # GET SYSTEMUSER: VALIDATION
    # ----------------------------------------------

    current_user = r.json()
    assert current_user
    assert current_user["is_active"] is True
    assert current_user["is_superuser"] is True
    assert current_user["is_adminuser"] is True
    assert current_user["is_systemuser"] is True
    assert current_user["is_guestuser"] is False
    assert current_user["username"] == SYSTEM_USER


def test_get_users_normal_user_me(client: TestClient, normal_user_token_headers: Dict[str, str]) -> None:
    # ----------------------------------------------
    # GET SYSTEMUSER: METHODS TO TEST
    # ----------------------------------------------

    r = client.get(f"{API_WEB_V1}/users/me", headers=normal_user_token_headers)

    # ----------------------------------------------
    # GET OWN USER: VALIDATION
    # ----------------------------------------------

    current_user = r.json()
    assert current_user
    assert current_user["is_active"] is True
    assert current_user["is_superuser"] is False
    assert current_user["email"] == TEST_MAIL


def test_create_user_new_email(client: TestClient, systemuser_token_headers: dict, db: Session) -> None:
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

    r = client.post(f"{API_WEB_V1}/users/", headers=systemuser_token_headers, json=t_data)

    # ----------------------------------------------
    # CREATE USER: VALIDATION
    # ----------------------------------------------

    assert 200 <= r.status_code < 300

    created_user = r.json()
    user = crud_user.get_by_email(db, email=t_email)

    assert user
    assert user.email == created_user["email"]
    assert user.username == created_user["username"]
    assert user.full_name == created_user["full_name"]
    assert user.is_active is True


def test_get_existing_user(client: TestClient, systemuser_token_headers: dict, db: Session) -> None:
    # ----------------------------------------------
    # GET USER: PREPARATION
    # ----------------------------------------------

    t_user = get_test_user(db)

    # ----------------------------------------------
    # GET USER: METHODS TO TEST
    # ----------------------------------------------

    r = client.get(f"{API_WEB_V1}/users/{t_user.id}", headers=systemuser_token_headers)

    # ----------------------------------------------
    # GET USER: VALIDATION
    # ----------------------------------------------

    assert 200 <= r.status_code < 300

    api_user = r.json()
    existing_user = crud_user.get_by_email(db, email=t_user.email)

    assert existing_user
    assert existing_user.email == api_user["email"]

    assert t_user.email == api_user["email"]
    assert t_user.username == api_user["username"]
    assert t_user.full_name == api_user["full_name"]
    assert t_user.is_active is True


def test_create_user_existing_username(client: TestClient, systemuser_token_headers: dict, db: Session) -> None:
    # ----------------------------------------------
    # CREATE EXISTING USER: PREPARATION
    # ----------------------------------------------

    t_user = get_test_user(db)
    data = {
        "email": t_user.email,
        "password": random_lower_string(),
        "username": random_username(),
        "full_name": random_name(),
    }

    # ----------------------------------------------
    # CREATE EXISTING USER: METHODS TO TEST
    # ----------------------------------------------

    r = client.post(f"{API_WEB_V1}/users/", headers=systemuser_token_headers, json=data)

    # ----------------------------------------------
    # CREATE EXISTING USER: VALIDATION
    # ----------------------------------------------

    assert r.status_code == 406


def test_create_user_by_normal_user(client: TestClient, normal_user_token_headers: Dict[str, str]) -> None:
    # ----------------------------------------------
    # CREATE BY NORMAL USER: PREPARATION
    # ----------------------------------------------

    username = random_username()
    email = random_email()
    password = random_lower_string()
    full_name = random_name()
    data = {"email": email, "password": password, "username": username, "full_name": full_name}

    # ----------------------------------------------
    # CREATE BY NORMAL USER: METHODS TO TEST
    # ----------------------------------------------

    r = client.post(f"{API_WEB_V1}/users/", headers=normal_user_token_headers, json=data)

    # ----------------------------------------------
    # CREATE BY NORMAL USER: VALIDATION
    # ----------------------------------------------

    assert r.status_code == 403


def test_retrieve_users(client: TestClient, systemuser_token_headers: dict, db: Session) -> None:
    # ----------------------------------------------
    # GET USERS: PREPARATION
    # ----------------------------------------------

    # No prep needed, by the nature of this test setup, multiple users do already exist in the DB.

    # ----------------------------------------------
    # GET USERS: METHODS TO TEST
    # ----------------------------------------------

    r = client.get(f"{API_WEB_V1}/users/", headers=systemuser_token_headers)
    all_users = r.json()

    # ----------------------------------------------
    # GET USERS: VALIDATION
    # ----------------------------------------------

    normal_user = False
    super_user = False
    admin_user = False
    system_user = False

    assert len(all_users) > 4
    for user in all_users:
        assert "email" in user
        assert "username" in user
        assert "full_name" in user
        assert "is_active" in user
        assert "is_superuser" in user
        assert "is_adminuser" in user
        assert "is_systemuser" in user
        if user["is_active"]:
            normal_user = True
        if user["is_superuser"]:
            super_user = True
        if user["is_adminuser"]:
            admin_user = True
        if user["is_systemuser"]:
            system_user = True
    assert normal_user
    assert super_user
    assert admin_user
    assert system_user
