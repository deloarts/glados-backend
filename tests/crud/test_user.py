from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.crud import crud_user
from app.schemas.schema_user import UserCreate, UserUpdate
from app.security import verify_password
from tests.utils.utils import (
    random_email,
    random_lower_string,
    random_name,
    random_username,
)


def test_create_user(db: Session) -> None:
    username = random_username()
    full_name = random_name()
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(
        username=username, full_name=full_name, email=email, password=password
    )
    user = crud_user.user.create(db, obj_in=user_in)
    assert user.email == email
    assert user.username == username
    assert user.full_name == full_name
    assert user.is_active is True
    assert user.is_superuser is False
    assert user.is_systemuser is False
    assert hasattr(user, "hashed_password")


def test_authenticate_user(db: Session) -> None:
    username = random_username()
    full_name = random_name()
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(
        username=username, full_name=full_name, email=email, password=password
    )
    user = crud_user.user.create(db, obj_in=user_in)
    authenticated_user = crud_user.user.authenticate(
        db, username=username, password=password
    )
    assert authenticated_user
    assert user.email == authenticated_user.email


def test_not_authenticate_user(db: Session) -> None:
    username = random_username()
    password = random_lower_string()
    user = crud_user.user.authenticate(db, username=username, password=password)
    assert user is None


def test_check_if_user_is_active(db: Session) -> None:
    username = random_username()
    full_name = random_name()
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(
        username=username, full_name=full_name, email=email, password=password
    )
    user = crud_user.user.create(db, obj_in=user_in)
    is_active = crud_user.user.is_active(user)
    assert is_active is True


def test_check_if_user_is_inactive(db: Session) -> None:
    username = random_username()
    full_name = random_name()
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(
        username=username,
        full_name=full_name,
        email=email,
        password=password,
        is_active=False,
    )
    user = crud_user.user.create(db, obj_in=user_in)
    is_active = crud_user.user.is_active(user)
    assert is_active is False


def test_check_if_user_is_superuser(db: Session) -> None:
    username = random_username()
    full_name = random_name()
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(
        username=username,
        full_name=full_name,
        email=email,
        password=password,
        is_superuser=True,
    )
    user = crud_user.user.create(db, obj_in=user_in)
    is_superuser = crud_user.user.is_superuser(user)
    assert is_superuser is True


def test_check_if_user_is_systemuser(db: Session) -> None:
    username = random_username()
    full_name = random_name()
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(
        username=username,
        full_name=full_name,
        email=email,
        password=password,
        is_systemuser=True,
    )
    user = crud_user.user.create(db, obj_in=user_in)
    is_systemuser = crud_user.user.is_systemuser(user)
    is_superuser = crud_user.user.is_superuser(user)
    is_active = crud_user.user.is_active(user)
    assert is_systemuser is True
    assert is_superuser is True
    assert is_active is True


def test_get_user(db: Session) -> None:
    username = random_username()
    full_name = random_name()
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(
        username=username,
        full_name=full_name,
        email=email,
        password=password,
        is_superuser=True,
    )
    user = crud_user.user.create(db, obj_in=user_in)
    user_2 = crud_user.user.get(db, id=user.id)
    assert user_2
    assert user.email == user_2.email
    assert jsonable_encoder(user) == jsonable_encoder(user_2)


def test_update_user(db: Session) -> None:
    username = random_username()
    full_name = random_name()
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(
        username=username,
        full_name=full_name,
        email=email,
        password=password,
        is_superuser=True,
    )
    user = crud_user.user.create(db, obj_in=user_in)
    new_password = random_lower_string()
    user_in_update = UserUpdate(
        username=username,
        full_name=full_name,
        email=email,
        password=new_password,
        is_superuser=True,
    )
    crud_user.user.update(db, db_obj=user, obj_in=user_in_update)
    user_2 = crud_user.user.get(db, id=user.id)
    assert user_2
    assert user.email == user_2.email
    assert verify_password(new_password, user_2.hashed_password)
