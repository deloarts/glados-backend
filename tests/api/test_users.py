from typing import Dict

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.config import cfg
from app.const import API_WEB_V1
from app.crud import crud_user
from app.schemas.schema_user import UserCreate
from tests.utils.user import TEST_MAIL
from tests.utils.utils import (
    random_email,
    random_lower_string,
    random_name,
    random_username,
)


def test_get_users_superuser_init(
    client: TestClient, superuser_token_headers: Dict[str, str]
) -> None:
    r = client.get(f"{API_WEB_V1}/users/me", headers=superuser_token_headers)
    current_user = r.json()
    assert current_user
    assert current_user["is_active"] is True
    assert current_user["is_superuser"]
    assert current_user["email"] == cfg.init.mail


def test_get_users_normal_user_me(
    client: TestClient, normal_user_token_headers: Dict[str, str]
) -> None:
    r = client.get(f"{API_WEB_V1}/users/me", headers=normal_user_token_headers)
    current_user = r.json()
    assert current_user
    assert current_user["is_active"] is True
    assert current_user["is_superuser"] is False
    assert current_user["email"] == TEST_MAIL


def test_create_user_new_email(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:

    username = random_username()
    email = random_email()
    password = random_lower_string()
    full_name = random_name()
    data = {
        "email": email,
        "password": password,
        "username": username,
        "full_name": full_name,
    }
    r = client.post(
        f"{API_WEB_V1}/users/",
        headers=superuser_token_headers,
        json=data,
    )
    assert 200 <= r.status_code < 300
    created_user = r.json()
    user = crud_user.user.get_by_email(db, email=email)
    assert user
    assert user.email == created_user["email"]
    assert user.username == created_user["username"]
    assert user.full_name == created_user["full_name"]
    assert user.is_active is True


def test_get_existing_user(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    username = random_username()
    email = random_email()
    password = random_lower_string()
    full_name = random_name()
    user_in = UserCreate(
        email=email, password=password, full_name=full_name, username=username
    )
    user = crud_user.user.create(db, obj_in=user_in)
    user_id = user.id
    r = client.get(
        f"{API_WEB_V1}/users/{user_id}",
        headers=superuser_token_headers,
    )
    assert 200 <= r.status_code < 300
    api_user = r.json()
    existing_user = crud_user.user.get_by_email(db, email=email)
    assert existing_user
    assert existing_user.email == api_user["email"]
    assert user.email == api_user["email"]
    assert user.username == api_user["username"]
    assert user.full_name == api_user["full_name"]
    assert user.is_active is True


def test_create_user_existing_username(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    username = random_username()
    email = random_email()
    password = random_lower_string()
    full_name = random_name()
    user_in = UserCreate(
        email=email, password=password, full_name=full_name, username=username
    )
    crud_user.user.create(db, obj_in=user_in)
    data = {
        "email": email,
        "password": password,
        "username": username,
        "full_name": full_name,
    }
    r = client.post(
        f"{API_WEB_V1}/users/",
        headers=superuser_token_headers,
        json=data,
    )
    created_user = r.json()
    assert r.status_code == 406
    assert "_id" not in created_user


def test_create_user_by_normal_user(
    client: TestClient, normal_user_token_headers: Dict[str, str]
) -> None:
    username = random_username()
    email = random_email()
    password = random_lower_string()
    full_name = random_name()
    data = {
        "email": email,
        "password": password,
        "username": username,
        "full_name": full_name,
    }
    r = client.post(
        f"{API_WEB_V1}/users/",
        headers=normal_user_token_headers,
        json=data,
    )
    assert r.status_code == 401


def test_retrieve_users(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    username = random_username()
    email = random_email()
    password = random_lower_string()
    full_name = random_name()
    user_in = UserCreate(
        email=email, password=password, full_name=full_name, username=username
    )
    crud_user.user.create(db, obj_in=user_in)

    username_2 = random_username()
    email_2 = random_email()
    password_2 = random_lower_string()
    full_name_2 = random_name()
    user_in_2 = UserCreate(
        email=email_2, password=password_2, full_name=full_name_2, username=username_2
    )
    crud_user.user.create(db, obj_in=user_in_2)

    r = client.get(f"{API_WEB_V1}/users/", headers=superuser_token_headers)
    all_users = r.json()

    assert len(all_users) > 1
    for item in all_users:
        assert "email" in item