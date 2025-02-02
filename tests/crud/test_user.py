import pytest
from api.schemas.user import UserCreateSchema
from api.schemas.user import UserUpdateSchema
from crud.user import crud_user
from exceptions import UserAlreadyExistsError
from fastapi.encoders import jsonable_encoder
from security.pwd import verify_hash
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from tests.utils.user import TEST_PASS
from tests.utils.user import current_user_adminuser
from tests.utils.user import get_test_admin_user
from tests.utils.user import get_test_super_user
from tests.utils.user import get_test_user
from tests.utils.utils import random_email
from tests.utils.utils import random_lower_string
from tests.utils.utils import random_name
from tests.utils.utils import random_username


def test_create_user(db: Session) -> None:
    # ----------------------------------------------
    # CREATE USER: PREPARATION
    # ----------------------------------------------

    t_username = random_username()
    t_full_name = random_name()
    t_email = random_email()
    t_password = random_lower_string()

    while crud_user.get_by_username(db, username=t_username) or crud_user.get_by_email(db, email=t_email):
        t_username = random_username()
        t_email = random_email()

    t_user_in = UserCreateSchema(
        username=t_username,
        full_name=t_full_name,
        email=t_email,
        password=t_password,
        rfid=None,
    )

    # ----------------------------------------------
    # CREATE USER: METHODS TO TEST
    # ----------------------------------------------

    user = crud_user.create(db, obj_in=t_user_in, current_user=current_user_adminuser())

    # ----------------------------------------------
    # CREATE USER: VALIDATION
    # ----------------------------------------------

    assert user.username == t_username
    assert user.email == t_email
    assert user.full_name == t_full_name
    assert user.language == "enGB"
    assert user.is_active is True
    assert user.is_superuser is False
    assert user.is_adminuser is False
    assert user.is_systemuser is False
    assert hasattr(user, "hashed_password")

    with pytest.raises(UserAlreadyExistsError):
        # Cannot create same user twice
        crud_user.create(db, obj_in=t_user_in, current_user=current_user_adminuser())


def test_authenticate_user(db: Session) -> None:
    # ----------------------------------------------
    # AUTH USER: PREPARATION
    # ----------------------------------------------

    t_user = get_test_user(db)
    t_super = get_test_super_user(db)
    t_admin = get_test_admin_user(db)

    # Some tests update the password, make sure to authenticate the user to their current pw
    crud_user.update(db, current_user=t_admin, db_obj=t_user, obj_in={"password": TEST_PASS})
    crud_user.update(db, current_user=t_admin, db_obj=t_super, obj_in={"password": TEST_PASS})
    crud_user.update(db, current_user=t_admin, db_obj=t_admin, obj_in={"password": TEST_PASS})

    # ----------------------------------------------
    # AUTH USER: METHODS TO TEST
    # ----------------------------------------------

    authenticated_user = crud_user.authenticate(db, username=t_user.username, password=TEST_PASS)
    authenticated_super_user = crud_user.authenticate(db, username=t_super.username, password=TEST_PASS)
    authenticated_admin_user = crud_user.authenticate(db, username=t_admin.username, password=TEST_PASS)
    unauthenticated_user = crud_user.authenticate(db, username=t_user.username, password="definitely not the password")

    # ----------------------------------------------
    # AUTH USER: VALIDATION
    # ----------------------------------------------

    assert authenticated_user
    assert authenticated_super_user
    assert authenticated_admin_user
    assert not unauthenticated_user


def test_check_if_user_is_active(db: Session) -> None:
    # ----------------------------------------------
    # ACTIVE USER: PREPARATION
    # ----------------------------------------------

    t_user_in = UserCreateSchema(
        username=random_username(),
        full_name=random_name(),
        email=random_email(),
        password=random_lower_string(),
        rfid=None,
    )
    t_user = crud_user.create(db, obj_in=t_user_in, current_user=current_user_adminuser())

    # ----------------------------------------------
    # ACTIVE USER: METHODS TO TEST
    # ----------------------------------------------

    is_active = crud_user.is_active(t_user)

    # ----------------------------------------------
    # ACTIVE USER: VALIDATION
    # ----------------------------------------------

    assert is_active is True


def test_check_if_user_is_inactive(db: Session) -> None:
    # ----------------------------------------------
    # INACTIVE USER: PREPARATION
    # ----------------------------------------------

    t_user_in = UserCreateSchema(
        username=random_username(),
        full_name=random_name(),
        email=random_email(),
        password=random_lower_string(),
        is_active=False,
        rfid=None,
    )
    t_user = crud_user.create(db, obj_in=t_user_in, current_user=current_user_adminuser())

    # ----------------------------------------------
    # INACTIVE USER: METHODS TO TEST
    # ----------------------------------------------

    is_active = crud_user.is_active(t_user)

    # ----------------------------------------------
    # INACTIVE USER: VALIDATION
    # ----------------------------------------------

    assert is_active is False


def test_check_if_user_is_superuser(db: Session) -> None:
    # ----------------------------------------------
    # SUPER USER: PREPARATION
    # ----------------------------------------------

    t_user_in = UserCreateSchema(
        username=random_username(),
        full_name=random_name(),
        email=random_email(),
        password=random_lower_string(),
        is_superuser=True,
        rfid=None,
    )
    t_user = crud_user.create(db, obj_in=t_user_in, current_user=current_user_adminuser())

    # ----------------------------------------------
    # SUPER USER: METHODS TO TEST
    # ----------------------------------------------

    is_active = crud_user.is_active(t_user)
    is_superuser = crud_user.is_superuser(t_user)
    is_adminuser = crud_user.is_adminuser(t_user)

    # ----------------------------------------------
    # SUPER USER: VALIDATION
    # ----------------------------------------------

    assert is_active is True
    assert is_superuser is True
    assert is_adminuser is False


def test_check_if_user_is_adminuser(db: Session) -> None:
    # ----------------------------------------------
    # ADMIN USER: PREPARATION
    # ----------------------------------------------

    t_user_in = UserCreateSchema(
        username=random_username(),
        full_name=random_name(),
        email=random_email(),
        password=random_lower_string(),
        is_superuser=False,  # Even if set to false, when is_adminuser is set True, this will become True
        is_adminuser=True,
        rfid=None,
    )
    t_user = crud_user.create(db, obj_in=t_user_in, current_user=current_user_adminuser())

    # ----------------------------------------------
    # ADMIN USER: METHODS TO TEST
    # ----------------------------------------------

    is_active = crud_user.is_active(t_user)
    is_superuser = crud_user.is_superuser(t_user)
    is_adminuser = crud_user.is_adminuser(t_user)

    # ----------------------------------------------
    # ADMIN USER: VALIDATION
    # ----------------------------------------------

    assert is_active is True
    assert is_superuser is True
    assert is_adminuser is True


def test_get_user(db: Session) -> None:
    # ----------------------------------------------
    # GET USER: PREPARATION
    # ----------------------------------------------

    t_user_in = UserCreateSchema(
        username=random_username(),
        full_name=random_name(),
        email=random_email(),
        password=random_lower_string(),
        is_superuser=False,  # Even if set to false, when is_adminuser is set True, this will become True
        is_adminuser=True,
        rfid=None,
    )
    t_user = crud_user.create(db, obj_in=t_user_in, current_user=current_user_adminuser())

    # ----------------------------------------------
    # GET USER: METHODS TO TEST
    # ----------------------------------------------

    user_2 = crud_user.get(db, id=t_user.id)

    # ----------------------------------------------
    # GET USER: VALIDATION
    # ----------------------------------------------

    assert user_2
    assert user_2 is t_user
    assert user_2.email == t_user.email
    assert jsonable_encoder(t_user) == jsonable_encoder(user_2)


def test_update_user(db: Session) -> None:
    # ----------------------------------------------
    # UPDATE USER: PREPARATION
    # ----------------------------------------------

    t_user_in = UserCreateSchema(
        username=random_username(),
        full_name=random_name(),
        email=random_email(),
        password=random_lower_string(),
        rfid=None,
    )
    t_user = crud_user.create(db, obj_in=t_user_in, current_user=current_user_adminuser())
    t_new_pass = random_lower_string()
    t_user_in_update = UserUpdateSchema(
        username=t_user_in.username,
        full_name=t_user.full_name,
        email=t_user.email,
        password=t_new_pass,
        language="deAT",
        theme="dark",
        rfid=None,
    )

    # ----------------------------------------------
    # UPDATE USER: METHODS TO TEST
    # ----------------------------------------------

    crud_user.update(db, db_obj=t_user, obj_in=t_user_in_update, current_user=current_user_adminuser())

    # ----------------------------------------------
    # UPDATE USER: VALIDATION
    # ----------------------------------------------

    user_2 = crud_user.get(db, id=t_user.id)
    assert user_2
    assert t_user.email == user_2.email
    assert verify_hash(t_new_pass, user_2.hashed_password)
    assert user_2.language == "deAT"
