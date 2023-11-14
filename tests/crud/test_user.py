from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.crud import crud_user
from app.schemas.schema_user import UserCreate
from app.schemas.schema_user import UserUpdate
from app.security.pwd import verify_password
from tests.utils.user import current_user_adminuser
from tests.utils.utils import random_email
from tests.utils.utils import random_lower_string
from tests.utils.utils import random_name
from tests.utils.utils import random_username

# Important note: Throughout the app the user model is imported this way, not like
# this: app.models.model_user ...
# If you would import the model with `from app.models.model_user import User`,
# this somehow cause it to be seen as 2 different models, despite being the same file,
# resulting the pytest discovery to fail, and also to mess with the metadata instance.
from models.model_user import User  # type:ignore isort:skip


def test_create_user(db: Session) -> None:
    username = random_username()
    full_name = random_name()
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(username=username, full_name=full_name, email=email, password=password)
    user = crud_user.user.create(db, obj_in=user_in, current_user=current_user_adminuser())
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
    user_in = UserCreate(username=username, full_name=full_name, email=email, password=password)
    user = crud_user.user.create(db, obj_in=user_in, current_user=current_user_adminuser())
    authenticated_user = crud_user.user.authenticate(db, username=username, password=password)
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
    user_in = UserCreate(username=username, full_name=full_name, email=email, password=password)
    user = crud_user.user.create(db, obj_in=user_in, current_user=current_user_adminuser())
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
    user = crud_user.user.create(db, obj_in=user_in, current_user=current_user_adminuser())
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
    user = crud_user.user.create(db, obj_in=user_in, current_user=current_user_adminuser())
    is_superuser = crud_user.user.is_superuser(user)
    is_active = crud_user.user.is_active(user)
    assert is_superuser is True
    assert is_active is True


def test_check_if_user_is_adminuser(db: Session) -> None:
    username = random_username()
    full_name = random_name()
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(
        username=username,
        full_name=full_name,
        email=email,
        password=password,
        is_adminuser=True,
    )
    user = crud_user.user.create(db, obj_in=user_in, current_user=current_user_adminuser())
    is_adminuser = crud_user.user.is_adminuser(user)
    is_superuser = crud_user.user.is_superuser(user)
    is_active = crud_user.user.is_active(user)
    assert is_adminuser is True
    assert is_superuser is True
    assert is_active is True


# def test_check_if_user_is_systemuser(db: Session) -> None:
#     username = random_username()
#     full_name = random_name()
#     email = random_email()
#     password = random_lower_string()
#     user_in = UserCreate(
#         username=username,
#         full_name=full_name,
#         email=email,
#         password=password,
#         is_systemuser=True,
#     )
#     user = crud_user.user.create(db, obj_in=user_in, current_user=current_user_adminuser())
#     is_systemuser = crud_user.user.is_systemuser(user)
#     is_adminuser = crud_user.user.is_adminuser(user)
#     is_superuser = crud_user.user.is_superuser(user)
#     is_active = crud_user.user.is_active(user)
#     assert is_systemuser is True
#     assert is_superuser is True
#     assert is_adminuser is False
#     assert is_active is True


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
    user = crud_user.user.create(db, obj_in=user_in, current_user=current_user_adminuser())
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
    user = crud_user.user.create(db, obj_in=user_in, current_user=current_user_adminuser())
    new_password = random_lower_string()
    user_in_update = UserUpdate(
        username=username,
        full_name=full_name,
        email=email,
        password=new_password,
        is_superuser=True,
    )
    crud_user.user.update(db, db_obj=user, obj_in=user_in_update, current_user=current_user_adminuser())
    user_2 = crud_user.user.get(db, id=user.id)
    assert user_2
    assert user.email == user_2.email
    assert verify_password(new_password, user_2.hashed_password)
