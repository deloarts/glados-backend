from datetime import UTC
from datetime import datetime
from typing import Dict

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.schemas.user import UserCreateSchema
from app.api.schemas.user import UserUpdateSchema
from app.const import API_WEB_V1
from app.crud.user import crud_user
from app.db.models import UserModel
from tests.utils.utils import random_email
from tests.utils.utils import random_lower_string
from tests.utils.utils import random_name
from tests.utils.utils import random_username

TEST_USERNAME = "test"
TEST_MAIL = "test@glados.com"
TEST_FULL_NAME = "Pytest User"


def user_authentication_headers(*, client: TestClient, username: str, password: str) -> Dict[str, str]:
    data = {"username": username, "password": password}

    r = client.post(f"{API_WEB_V1}/login/access-token", data=data)
    response = r.json()
    auth_token = response["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}
    return headers


def create_random_user(db: Session) -> UserModel:
    email = random_email()
    password = random_lower_string()
    username = random_username()
    full_name = random_name()
    user_in = UserCreateSchema(
        username=username,
        email=email,  # type: ignore
        password=password,
        full_name=full_name,
    )
    user = crud_user.create(db=db, obj_in=user_in, current_user=current_user_adminuser())
    return user


def authentication_token_from_email(*, client: TestClient, email: str, db: Session) -> Dict[str, str]:
    """
    Return a valid token for the user with given email.

    If the user doesn't exist it is created first.
    """
    password = random_lower_string()
    user = crud_user.get_by_email(db, email=email)
    if not user:
        user_in_create = UserCreateSchema(
            username=TEST_USERNAME,
            email=email,
            password=password,
            full_name=TEST_FULL_NAME,
        )
        user = crud_user.create(db, obj_in=user_in_create, current_user=current_user_adminuser())
    else:
        user_in_update = UserUpdateSchema(
            username=TEST_USERNAME,
            email=email,
            password=password,
            full_name=TEST_FULL_NAME,
        )
        user = crud_user.update(db, db_obj=user, obj_in=user_in_update, current_user=current_user_adminuser())

    return user_authentication_headers(client=client, username=TEST_USERNAME, password=password)


def current_user_adminuser() -> UserModel:
    return UserModel(
        **{
            "id": 0,
            "created": datetime.now(UTC),
            "personal_access_token": None,
            "username": "test",
            "full_name": "Glados Test",
            "email": "test@glados.com",
            "hashed_password": "not_really_hashed",
            "is_active": True,
            "is_superuser": True,
            "is_adminuser": True,
            "is_systemuser": False,
            "is_guestuser": False,
        }
    )
