import pytest
from exceptions import InsufficientPermissionsError
from sqlalchemy.orm import Session

from app.api.schemas.project import ProjectCreateSchema
from app.crud.project import crud_project
from tests.utils.project import get_test_project
from tests.utils.user import get_test_admin_user
from tests.utils.user import get_test_super_user
from tests.utils.user import get_test_user
from tests.utils.utils import random_manufacturer
from tests.utils.utils import random_note
from tests.utils.utils import random_product_number
from tests.utils.utils import random_project


def test_create_project_normal_user(db: Session) -> None:
    # ----------------------------------------------
    # CREATE ITEM: PREPARATION
    # ----------------------------------------------

    t_normal_user = get_test_user(db)
    t_number = random_project()
    t_product_number = random_product_number()
    t_customer = random_manufacturer()
    t_description = random_note()

    while crud_project.get_by_number(db, number=t_number):
        t_number = random_project()

    t_project_in = ProjectCreateSchema(
        number=t_number,
        product_number=t_product_number,
        customer=t_customer,
        description=t_description,
        designated_user_id=t_normal_user.id,
        is_active=True,
    )

    # ----------------------------------------------
    # CREATE ITEM: METHODS TO TEST
    # ----------------------------------------------

    project = crud_project.create(db=db, db_obj_user=t_normal_user, obj_in=t_project_in)

    # ----------------------------------------------
    # CREATE ITEM: VALIDATION
    # ----------------------------------------------

    assert project.number == t_number
    assert project.product_number == t_product_number
    assert project.customer == t_customer
    assert project.description == t_description
    assert project.designated_user_id == t_normal_user.id
    assert project.is_active is True

    assert project in t_normal_user.projects


def test_create_project_super_user(db: Session) -> None:
    # ----------------------------------------------
    # CREATE ITEM: PREPARATION
    # ----------------------------------------------

    t_normal_user = get_test_user(db)
    t_super_user = get_test_super_user(db)

    t_number = random_project()
    t_product_number = random_product_number()
    t_customer = random_manufacturer()
    t_description = random_note()

    while crud_project.get_by_number(db, number=t_number):
        t_number = random_project()

    t_project_in = ProjectCreateSchema(
        number=t_number,
        product_number=t_product_number,
        customer=t_customer,
        description=t_description,
        designated_user_id=t_normal_user.id,
        is_active=True,
    )

    # ----------------------------------------------
    # CREATE ITEM: METHODS TO TEST
    # ----------------------------------------------

    project = crud_project.create(db=db, db_obj_user=t_super_user, obj_in=t_project_in)

    # ----------------------------------------------
    # CREATE ITEM: VALIDATION
    # ----------------------------------------------

    assert project.number == t_number
    assert project.product_number == t_product_number
    assert project.customer == t_customer
    assert project.description == t_description
    assert project.designated_user_id == t_normal_user.id
    assert project.is_active is True

    assert project in t_normal_user.projects


def test_create_project_admin_user(db: Session) -> None:
    # ----------------------------------------------
    # CREATE ITEM: PREPARATION
    # ----------------------------------------------

    t_normal_user = get_test_user(db)
    t_admin_user = get_test_admin_user(db)

    t_number = random_project()
    t_product_number = random_product_number()
    t_customer = random_manufacturer()
    t_description = random_note()

    while crud_project.get_by_number(db, number=t_number):
        t_number = random_project()

    t_project_in = ProjectCreateSchema(
        number=t_number,
        product_number=t_product_number,
        customer=t_customer,
        description=t_description,
        designated_user_id=t_normal_user.id,
        is_active=True,
    )

    # ----------------------------------------------
    # CREATE ITEM: METHODS TO TEST
    # ----------------------------------------------

    project = crud_project.create(db=db, db_obj_user=t_admin_user, obj_in=t_project_in)

    # ----------------------------------------------
    # CREATE ITEM: VALIDATION
    # ----------------------------------------------

    assert project.number == t_number
    assert project.product_number == t_product_number
    assert project.customer == t_customer
    assert project.description == t_description
    assert project.designated_user_id == t_normal_user.id
    assert project.is_active is True

    assert project in t_normal_user.projects


def test_get_project(db: Session) -> None:
    # ----------------------------------------------
    # GET PROJECT: PREPARATION
    # ----------------------------------------------

    t_project = get_test_project(db)

    # ----------------------------------------------
    # GET PROJECT: METHODS TO TEST
    # ----------------------------------------------

    project = crud_project.get(db=db, id=t_project.id)

    # ----------------------------------------------
    # GET PROJECT: VALIDATION
    # ----------------------------------------------

    assert project == t_project
