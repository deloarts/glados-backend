"""
    CRUD tests (DELETE ONLY) for the project model
"""

from typing import List

import pytest
from crud.bought_item import crud_bought_item
from crud.project import crud_project
from db.models import BoughtItemModel
from exceptions import InsufficientPermissionsError
from sqlalchemy.orm import Session

from tests.utils.bought_item import create_random_item
from tests.utils.project import create_random_project
from tests.utils.user import get_test_admin_user
from tests.utils.user import get_test_super_user
from tests.utils.user import get_test_user


def test_delete_project_as_normal_user(db: Session) -> None:
    """
    Test the deletion of a project by a normal user.
    This test ensures that a normal user does not have the necessary permissions
    to delete a project. It verifies that an InsufficientPermissionsError is raised
    when a normal user attempts to delete a project and that the project still exists
    in the database after the deletion attempt.

    Args:
        db (Session): The database session used for the test.

    Raises:
        InsufficientPermissionsError: If the normal user does not have permission to delete the project.
    """

    # ----------------------------------------------
    # DELETE PROJECT: PREPARATION
    # ----------------------------------------------

    t_normal_user = get_test_user(db)
    t_project = create_random_project(db)

    # ----------------------------------------------
    # DELETE PROJECT: METHODS TO TEST
    # ----------------------------------------------

    with pytest.raises(InsufficientPermissionsError):
        crud_project.delete(db=db, db_obj_user=t_normal_user, db_obj_project=t_project)

    # ----------------------------------------------
    # DELETE PROJECT: VALIDATION
    # ----------------------------------------------

    assert t_project == crud_project.get(db=db, id=t_project.id)


def test_delete_project_as_super_user(db: Session) -> None:
    """
    Test the deletion of a project by a super user.
    This test performs the following steps:
    1. Preparation:
        - Retrieve a test super user.
        - Create a random project.
        - Verify that the project exists in the database.
    2. Methods to Test:
        - Delete the project using the super user.
    3. Validation:
        - Ensure the project is marked as deleted.
        - Verify that the project no longer exists in the database.

    Args:
        db (Session): The database session used for the test.
    """

    # ----------------------------------------------
    # DELETE PROJECT: PREPARATION
    # ----------------------------------------------

    t_super_user = get_test_super_user(db)
    t_project = create_random_project(db)

    count, projects = crud_project.get_multi(db=db, number=t_project.number)
    assert count > 0
    assert t_project in projects

    # ----------------------------------------------
    # DELETE PROJECT: METHODS TO TEST
    # ----------------------------------------------

    project = crud_project.delete(db=db, db_obj_user=t_super_user, db_obj_project=t_project)

    # ----------------------------------------------
    # DELETE PROJECT: VALIDATION
    # ----------------------------------------------

    assert project
    assert project.deleted is True
    assert crud_project.get(db=db, id=t_project.id)

    count, projects = crud_project.get_multi(db=db, number=t_project.number)
    assert count == 0
    assert projects == []


def test_delete_project_as_admin_user(db: Session) -> None:
    """
    Test the deletion of a project by an admin user.
    This test performs the following steps:
    1. Preparation:
        - Retrieve a test admin user.
        - Create a random project.
        - Verify that the project exists in the database.
    2. Methods to Test:
        - Delete the project using the CRUD operation.
    3. Validation:
        - Ensure the project is marked as deleted.
        - Verify that the project no longer exists in the database.

    Args:
        db (Session): The database session used for the test.

    Asserts:
        - The project exists before deletion.
        - The project is successfully deleted.
        - The project is marked as deleted.
        - The project no longer exists in the database after deletion.
    """

    # ----------------------------------------------
    # DELETE PROJECT: PREPARATION
    # ----------------------------------------------

    t_admin_user = get_test_admin_user(db)
    t_project = create_random_project(db)

    count, projects = crud_project.get_multi(db=db, number=t_project.number)
    assert count > 0
    assert t_project in projects

    # ----------------------------------------------
    # DELETE PROJECT: METHODS TO TEST
    # ----------------------------------------------

    project = crud_project.delete(db=db, db_obj_user=t_admin_user, db_obj_project=t_project)

    # ----------------------------------------------
    # DELETE PROJECT: VALIDATION
    # ----------------------------------------------

    assert project
    assert project.deleted is True
    assert crud_project.get(db=db, id=t_project.id)

    count, projects = crud_project.get_multi(db=db, number=t_project.number)
    assert count == 0
    assert projects == []


def test_delete_project_items_are_deleted_as_well(db: Session) -> None:
    """
    Test that deleting a project also deletes its associated items.
    This test performs the following steps:
    1. Preparation:
        - Creates a test super user.
        - Creates a random project.
        - Creates 10 random items associated with the project.
        - Asserts that the project exists in the database.
    2. Methods to Test:
        - Deletes the project using the CRUD operation.
    3. Validation:
        - Asserts that the project is marked as deleted.
        - Asserts that each associated item is marked as deleted.

    Args:
        db (Session): The database session used for the test.
    """

    # ----------------------------------------------
    # DELETE PROJECT: PREPARATION
    # ----------------------------------------------

    t_super_user = get_test_super_user(db)
    t_project = create_random_project(db)
    items: List[BoughtItemModel] = []
    for _ in range(10):
        items.append(
            create_random_item(
                db,
                test_fn_name=test_delete_project_items_are_deleted_as_well.__name__,
                user=t_super_user,
                project=t_project,
            )
        )

    count, projects = crud_project.get_multi(db=db, number=t_project.number)
    assert count > 0
    assert t_project in projects

    # ----------------------------------------------
    # DELETE PROJECT: METHODS TO TEST
    # ----------------------------------------------

    project = crud_project.delete(db=db, db_obj_user=t_super_user, db_obj_project=t_project)

    # ----------------------------------------------
    # DELETE PROJECT: VALIDATION
    # ----------------------------------------------

    assert project
    assert project.deleted is True

    for item in items:
        i = crud_bought_item.get(db, id=item.id)
        assert i
        assert i.deleted is True
