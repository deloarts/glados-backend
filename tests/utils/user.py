import sys

sys.path.append("app")

from datetime import datetime
from typing import Dict

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.schemas.schema_user import UserCreate
from app.api.schemas.schema_user import UserUpdate
from app.const import API_WEB_V1
from app.crud import crud_user
from tests.utils.utils import random_email
from tests.utils.utils import random_lower_string
from tests.utils.utils import random_name
from tests.utils.utils import random_username

# Important note: Throughout the app the user model is imported this way, not like
# this: app.db.models.model_user ...
# If you would import the model with `from app.db.models.model_user import User`,
# this somehow cause it to be seen as 2 different models, despite being the same file,
# resulting the pytest discovery to fail, and also to mess with the metadata instance.
from db.models.model_user import User  # type:ignore isort:skip

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


def create_random_user(db: Session) -> User:
    email = random_email()
    password = random_lower_string()
    username = random_username()
    full_name = random_name()
    user_in = UserCreate(
        username=username,
        email=email,  # type: ignore
        password=password,
        full_name=full_name,
    )
    user = crud_user.user.create(db=db, obj_in=user_in, current_user=current_user_adminuser())
    return user


def authentication_token_from_email(*, client: TestClient, email: str, db: Session) -> Dict[str, str]:
    """
    Return a valid token for the user with given email.

    If the user doesn't exist it is created first.
    """
    password = random_lower_string()
    user = crud_user.user.get_by_email(db, email=email)
    if not user:
        user_in_create = UserCreate(
            username=TEST_USERNAME,
            email=email,
            password=password,
            full_name=TEST_FULL_NAME,
        )
        user = crud_user.user.create(db, obj_in=user_in_create, current_user=current_user_adminuser())
    else:
        user_in_update = UserUpdate(
            username=TEST_USERNAME,
            email=email,
            password=password,
            full_name=TEST_FULL_NAME,
        )
        user = crud_user.user.update(db, db_obj=user, obj_in=user_in_update, current_user=current_user_adminuser())

    return user_authentication_headers(client=client, username=TEST_USERNAME, password=password)


def current_user_adminuser() -> User:
    return User(
        **{
            "id": 0,
            "created": datetime.utcnow(),
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
