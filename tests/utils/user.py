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
TEST_PASS = "12345678"  # much safe
TEST_MAIL = "test@glados.com"
TEST_FULL_NAME = "Periclitatio Usor"

TEST_SUPER_USERNAME = "super"
TEST_SUPER_MAIL = "super@glados.com"
TEST_SUPER_FULL_NAME = "Superiorum Usor"

TEST_ADMIN_USERNAME = "admin"
TEST_ADMIN_MAIL = "admin@glados.com"
TEST_ADMIN_FULL_NAME = "Administrator Usor"


def user_authentication_headers(*, client: TestClient, username: str, password: str) -> Dict[str, str]:
    data = {"username": username, "password": password}

    r = client.post(f"{API_WEB_V1}/login/access-token", data=data)
    response = r.json()
    auth_token = response["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}
    return headers


def create_user(
    db: Session,
    email: str,
    password: str,
    username: str,
    full_name: str,
    is_super: bool = False,
    is_admin: bool = False,
) -> UserModel:
    user_in = UserCreateSchema(
        username=username,
        email=email,
        password=password,
        full_name=full_name,
        is_adminuser=is_admin,
        is_superuser=is_super,
        rfid=None,
    )
    user = crud_user.create(db=db, obj_in=user_in, current_user=current_user_adminuser())
    return user


def create_random_user(db: Session) -> UserModel:
    email = random_email()
    password = random_lower_string()
    username = random_username()
    full_name = random_name()

    while crud_user.get_by_email(db, email=email) or crud_user.get_by_username(db, username=username):
        email = random_email()
        username = random_username()

    return create_user(db=db, email=email, password=password, username=username, full_name=full_name)


def get_test_user(db: Session) -> UserModel:
    """Returns the test user, creates it if doesn't exists."""
    user = crud_user.get_by_username(db, username=TEST_USERNAME)
    if not user:
        return create_user(db=db, email=TEST_MAIL, password=TEST_PASS, username=TEST_USERNAME, full_name=TEST_FULL_NAME)
    return user


def get_test_super_user(db: Session) -> UserModel:
    """Returns the test user with superuser privileges, creates it if doesn't exists."""
    user = crud_user.get_by_username(db, username=TEST_SUPER_USERNAME)
    if not user:
        return create_user(
            db=db,
            email=TEST_SUPER_MAIL,
            password=TEST_PASS,
            username=TEST_SUPER_USERNAME,
            full_name=TEST_SUPER_FULL_NAME,
            is_super=True,
            is_admin=False,
        )
    return user


def get_test_admin_user(db: Session) -> UserModel:
    """Returns the test user with admin privileges, creates it if doesn't exists."""
    user = crud_user.get_by_username(db, username=TEST_ADMIN_USERNAME)
    if not user:
        return create_user(
            db=db,
            email=TEST_ADMIN_MAIL,
            password=TEST_PASS,
            username=TEST_ADMIN_USERNAME,
            full_name=TEST_ADMIN_FULL_NAME,
            is_super=True,
            is_admin=True,
        )
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
            username=TEST_USERNAME, email=email, password=password, full_name=TEST_FULL_NAME, rfid=None
        )
        user = crud_user.create(db, obj_in=user_in_create, current_user=current_user_adminuser())
    else:
        user_in_update = UserUpdateSchema(
            username=TEST_USERNAME,
            email=email,
            password=password,
            full_name=TEST_FULL_NAME,
            language="enGB",
            theme="dark",
            rfid=None,
        )
        user = crud_user.update(db, db_obj=user, obj_in=user_in_update, current_user=current_user_adminuser())

    return user_authentication_headers(client=client, username=TEST_USERNAME, password=password)


def current_user_adminuser() -> UserModel:
    return UserModel(
        **{
            "id": 0,
            "created": datetime.now(UTC),
            "personal_access_token": None,
            "username": "temp_admin",
            "full_name": "Temporary Admin",
            "email": "temp-admin@glados.com",
            "hashed_password": "not_really_hashed",
            "is_active": True,
            "is_superuser": True,
            "is_adminuser": True,
            "is_systemuser": False,
            "is_guestuser": False,
            "hashed_rfid": None,
        }
    )
