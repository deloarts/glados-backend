from datetime import UTC
from datetime import datetime
from typing import Dict

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.schemas.user import UserCreateSchema
from app.api.schemas.user import UserUpdateSchema
from app.config import cfg
from app.crud.user import crud_user
from app.db.models import UserModel
from tests.utils.utils import random_email
from tests.utils.utils import random_lower_string
from tests.utils.utils import random_name
from tests.utils.utils import random_username

TEST_PASSWORD = "12345678"  # much safe

TEST_USER_USERNAME = "test"
TEST_USER_MAIL = "test@glados.com"
TEST_USER_FULL_NAME = "Normal User"
TEST_USER_RFID = "1223334444"

TEST_INACTIVE_USERNAME = "inactive"
TEST_INACTIVE_MAIL = "inactive@glados.com"
TEST_INACTIVE_FULL_NAME = "Inactive User"

TEST_SUPER_USERNAME = "super"
TEST_SUPER_MAIL = "super@glados.com"
TEST_SUPER_FULL_NAME = "Super User"

TEST_ADMIN_USERNAME = "admin"
TEST_ADMIN_MAIL = "admin@glados.com"
TEST_ADMIN_FULL_NAME = "Admin User"

TEST_GUEST_USERNAME = "guest"
TEST_GUEST_MAIL = "guest@glados.com"
TEST_GUEST_FULL_NAME = "Guest User"


def user_authentication_headers(*, client: TestClient, username: str, password: str) -> Dict[str, str]:
    data = {"username": username, "password": password}

    r = client.post(f"{cfg.server.api.web}/login/access-token", data=data)
    response = r.json()
    auth_token = response["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}
    return headers


def create_user(
    db: Session,
    username: str,
    email: str,
    full_name: str,
    password: str,
    rfid: str | None = None,
    is_super: bool = False,
    is_admin: bool = False,
    is_guest: bool = False,
) -> UserModel:
    user_in = UserCreateSchema(
        username=username,
        email=email,
        password=password,
        full_name=full_name,
        is_adminuser=is_admin,
        is_superuser=is_super,
        is_guestuser=is_guest,
        rfid=rfid,
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
    user = crud_user.get_by_username(db, username=TEST_USER_USERNAME)
    if not user:
        return create_user(
            db=db,
            email=TEST_USER_MAIL,
            password=TEST_PASSWORD,
            username=TEST_USER_USERNAME,
            full_name=TEST_USER_FULL_NAME,
            rfid=TEST_USER_RFID,
        )
    return user


def get_test_user_inactive(db: Session) -> UserModel:
    """Returns the inactive test user, creates it if doesn't exists."""
    user = crud_user.get_by_username(db, username=TEST_INACTIVE_USERNAME)
    if not user:
        return create_user(
            db=db,
            email=TEST_INACTIVE_MAIL,
            password=TEST_PASSWORD,
            username=TEST_INACTIVE_USERNAME,
            full_name=TEST_INACTIVE_FULL_NAME,
        )
    return user


def get_test_super_user(db: Session) -> UserModel:
    """Returns the test user with superuser privileges, creates it if doesn't exists."""
    user = crud_user.get_by_username(db, username=TEST_SUPER_USERNAME)
    if not user:
        return create_user(
            db=db,
            email=TEST_SUPER_MAIL,
            password=TEST_PASSWORD,
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
            password=TEST_PASSWORD,
            username=TEST_ADMIN_USERNAME,
            full_name=TEST_ADMIN_FULL_NAME,
            is_super=True,
            is_admin=True,
        )
    return user


def get_test_guest_user(db: Session) -> UserModel:
    """Returns the test user with guest privileges, creates it if doesn't exists."""
    user = crud_user.get_by_username(db, username=TEST_GUEST_USERNAME)
    if not user:
        return create_user(
            db=db,
            email=TEST_GUEST_MAIL,
            password=TEST_PASSWORD,
            username=TEST_GUEST_USERNAME,
            full_name=TEST_GUEST_FULL_NAME,
            is_guest=True,
        )
    return user


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
