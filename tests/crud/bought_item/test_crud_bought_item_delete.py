"""
    CRUD tests (DELETE ONLY) for the bought item model
"""

import pytest
from config import cfg
from crud.bought_item import crud_bought_item
from exceptions import BoughtItemAlreadyPlannedError
from exceptions import BoughtItemOfAnotherUserError
from exceptions import InsufficientPermissionsError
from sqlalchemy.orm import Session

from tests.utils.bought_item import create_random_item
from tests.utils.user import create_random_user
from tests.utils.user import get_test_admin_user
from tests.utils.user import get_test_guest_user
from tests.utils.user import get_test_super_user
from tests.utils.user import get_test_user


def test_delete_item_same_user(db: Session) -> None:
    """
    Test case for deleting an item by the same user who created it.
    This test performs the following steps:

    1. Preparation:
       - Retrieve a test user from the database.
       - Create a random item associated with the test user.
    2. Methods to Test:
       - Delete the item using the CRUD operation with the same user who created it.
    3. Validation:
       - Retrieve the item from the database.
       - Assert that the item exists and is marked as deleted.
       - Assert that the item is still associated with the user's created items.

    Args:
        db (Session): The database session used for the test.
    """

    # ----------------------------------------------
    # DELETE ITEM (SAME USER): PREPARATION
    # ----------------------------------------------
    t_normal_user = get_test_user(db)
    t_item = create_random_item(db, test_fn_name=test_delete_item_same_user.__name__, user=t_normal_user)
    # About t_item:
    #   t_item is created by t_normal_user, so t_normal_user can delete the item.

    # ----------------------------------------------
    # DELETE ITEM (SAME USER): METHODS TO TEST
    # ----------------------------------------------

    # Let the user who created the item delete it
    crud_bought_item.delete(db=db, db_obj_user=t_normal_user, db_obj_item=t_item)

    # ----------------------------------------------
    # DELETE ITEM (SAME USER): VALIDATION
    # ----------------------------------------------

    item = crud_bought_item.get(db=db, id=t_item.id)
    assert item
    assert item.deleted is True
    assert item in t_normal_user.created_bought_items


def test_delete_planned_item_same_user(db: Session) -> None:
    """
    Test case for deleting a planned item by the same user who created it.
    This test verifies that a user cannot delete an item if its status is not 'open'.
    Specifically, it checks that attempting to delete an item with a 'requested' status
    raises a BoughtItemAlreadyPlannedError.

    Steps:
    1. Preparation:
       - Create a test user.
       - Create a random item associated with the test user.
       - Update the item's status to 'requested'.
    2. Methods to Test:
       - Attempt to delete the item using the same user who created it.
       - Verify that a BoughtItemAlreadyPlannedError is raised.
    3. Validation:
       - Retrieve the item from the database.
       - Assert that the item still exists and has not been deleted.
       - Assert that the item is still associated with the user who created it.

    Args:
        db (Session): The database session used for the test.

    Raises:
        BoughtItemAlreadyPlannedError: If the item is already planned and cannot be deleted.
    """

    # ----------------------------------------------
    # DELETE PLANNED ITEM (SAME USER): PREPARATION
    # ----------------------------------------------
    t_normal_user = get_test_user(db)
    t_item = create_random_item(db, test_fn_name=test_delete_planned_item_same_user.__name__, user=t_normal_user)
    # About t_item:
    #   t_item is created by t_normal_user, so t_normal_user cannot delete it if it's planned (status != 'open').
    crud_bought_item.update_status(
        db=db, db_obj_user=t_normal_user, db_obj_item=t_item, status=cfg.items.bought.status.requested
    )

    # ----------------------------------------------
    # DELETE PLANNED ITEM (SAME USER): METHODS TO TEST
    # ----------------------------------------------

    # Let the user who created the item delete it
    with pytest.raises(BoughtItemAlreadyPlannedError):
        crud_bought_item.delete(db=db, db_obj_user=t_normal_user, db_obj_item=t_item)

    # ----------------------------------------------
    # DELETE PLANNED ITEM (SAME USER): VALIDATION
    # ----------------------------------------------

    item = crud_bought_item.get(db=db, id=t_item.id)
    assert item
    assert item.deleted is False
    assert item in t_normal_user.created_bought_items


def test_delete_item_super_user(db: Session) -> None:
    """
    Test case for deleting an item by a super user.
    This test ensures that a super user can delete an item created by a normal user.

    Steps:
    1. Preparation:
        - Retrieve a test normal user and a test super user from the database.
        - Create a random item associated with the normal user.
    2. Methods to Test:
        - Use the super user to delete the item created by the normal user.
    3. Validation:
        - Retrieve the item from the database and verify that it is marked as deleted.
        - Ensure the item is still associated with the normal user's created items.

    Args:
        db (Session): The database session used for the test.

    Returns:
        None
    """

    # ----------------------------------------------
    # DELETE ITEM (SUPER USER): PREPARATION
    # ----------------------------------------------
    t_normal_user = get_test_user(db)
    t_super_user = get_test_super_user(db)
    t_item = create_random_item(db, test_fn_name=test_delete_item_super_user.__name__, user=t_normal_user)
    # About t_item:
    #   t_item is created by t_normal_user, an super user is allowed to delete it.

    # ----------------------------------------------
    # DELETE ITEM (SUPER USER): METHODS TO TEST
    # ----------------------------------------------

    # Let the super user delete the item of the normal user
    crud_bought_item.delete(db=db, db_obj_user=t_super_user, db_obj_item=t_item)

    # ----------------------------------------------
    # DELETE ITEM (SUPER USER): VALIDATION
    # ----------------------------------------------

    item = crud_bought_item.get(db=db, id=t_item.id)
    assert item
    assert item.deleted is True
    assert item in t_normal_user.created_bought_items


def test_delete_planned_item_super_user(db: Session) -> None:
    """
    Test the deletion of a planned item by a super user.
    This test verifies that a super user can delete an item that was created by a normal user,
    even if the item is in a planned status.

    Steps:
    1. Preparation:
        - Create a test normal user and a test super user.
        - Create a random item associated with the normal user.
        - Update the status of the item to 'requested'.
    2. Methods to Test:
        - Attempt to delete the item using the super user.
    3. Validation:
        - Verify that the item is marked as deleted.
        - Ensure the item is still associated with the normal user's created bought items.

    Args:
        db (Session): The database session used for the test.

    Asserts:
        - The item exists in the database.
        - The item is marked as deleted.
        - The item is in the normal user's created bought items.
    """

    # ----------------------------------------------
    # DELETE PLANNED ITEM (SUPER USER): PREPARATION
    # ----------------------------------------------
    t_normal_user = get_test_user(db)
    t_super_user = get_test_super_user(db)
    t_item = create_random_item(db, test_fn_name=test_delete_planned_item_super_user.__name__, user=t_normal_user)
    # About t_item:
    #   t_item is created by t_normal_user, an super user is allowed to delete it (even if it's planned)
    crud_bought_item.update_status(
        db=db, db_obj_user=t_normal_user, db_obj_item=t_item, status=cfg.items.bought.status.requested
    )

    # ----------------------------------------------
    # DELETE PLANNED ITEM (SUPER USER): METHODS TO TEST
    # ----------------------------------------------

    # Let the super user delete the item of the normal user
    crud_bought_item.delete(db=db, db_obj_user=t_super_user, db_obj_item=t_item)

    # ----------------------------------------------
    # DELETE PLANNED ITEM (SUPER USER): VALIDATION
    # ----------------------------------------------

    item = crud_bought_item.get(db=db, id=t_item.id)
    assert item
    assert item.deleted is True
    assert item in t_normal_user.created_bought_items


def test_delete_item_admin_user(db: Session) -> None:
    """
    Test case for deleting an item by an admin user.
    This test verifies that an admin user can delete an item created by a normal user.

    Steps:
    1. Preparation:
        - Create a normal user.
        - Create an admin user.
        - Create a random item associated with the normal user.
    2. Methods to Test:
        - Use the admin user to delete the item created by the normal user.
    3. Validation:
        - Ensure the item is marked as deleted.
        - Ensure the item is still associated with the normal user's created items.

    Args:
        db (Session): The database session used for the test.
    """

    # ----------------------------------------------
    # DELETE ITEM (ADMIN USER): PREPARATION
    # ----------------------------------------------
    t_normal_user = get_test_user(db)
    t_admin_user = get_test_admin_user(db)
    t_item = create_random_item(db, test_fn_name=test_delete_item_admin_user.__name__, user=t_normal_user)
    # About t_item:
    #   t_item is created by t_normal_user, an admin user is allowed to delete it.

    # ----------------------------------------------
    # DELETE ITEM (ADMIN USER): METHODS TO TEST
    # ----------------------------------------------

    # Let the admin user delete the item of the normal user
    crud_bought_item.delete(db=db, db_obj_user=t_admin_user, db_obj_item=t_item)

    # ----------------------------------------------
    # DELETE ITEM (ADMIN USER): VALIDATION
    # ----------------------------------------------

    item = crud_bought_item.get(db=db, id=t_item.id)
    assert item
    assert item.deleted is True
    assert item in t_normal_user.created_bought_items


def test_delete_planned_item_admin_user(db: Session) -> None:
    """
    Test the deletion of a planned item by an admin user.
    This test verifies that an admin user can delete a planned item created by a normal user.

    Steps:
    1. Preparation:
        - Create a test normal user.
        - Create a test admin user.
        - Create a random item associated with the normal user.
        - Update the status of the item to 'requested'.
    2. Methods to Test:
        - Delete the item using the admin user.
    3. Validation:
        - Retrieve the item and check if it is marked as deleted.
        - Ensure the item is still associated with the normal user's created bought items.

    Args:
        db (Session): The database session used for the test.
    """

    # ----------------------------------------------
    # DELETE PLANNED ITEM (ADMIN USER): PREPARATION
    # ----------------------------------------------
    t_normal_user = get_test_user(db)
    t_admin_user = get_test_admin_user(db)
    t_item = create_random_item(db, test_fn_name=test_delete_planned_item_admin_user.__name__, user=t_normal_user)
    # About t_item:
    #   t_item is created by t_normal_user, an admin user is allowed to delete it (even if it's planned)
    crud_bought_item.update_status(
        db=db, db_obj_user=t_normal_user, db_obj_item=t_item, status=cfg.items.bought.status.requested
    )

    # ----------------------------------------------
    # DELETE PLANNED ITEM (ADMIN USER): METHODS TO TEST
    # ----------------------------------------------

    # Let the admin user delete the item of the normal user
    crud_bought_item.delete(db=db, db_obj_user=t_admin_user, db_obj_item=t_item)

    # ----------------------------------------------
    # DELETE PLANNED ITEM (ADMIN USER): VALIDATION
    # ----------------------------------------------

    item = crud_bought_item.get(db=db, id=t_item.id)
    assert item
    assert item.deleted is True
    assert item in t_normal_user.created_bought_items


def test_delete_item_another_user(db: Session) -> None:
    """
    Test the deletion of an item by another user.
    This test ensures that a user cannot delete an item that was created by another user.
    It performs the following steps:

    1. Preparation:
        - Create a normal user (`t_normal_user`).
        - Create another normal user (`t_another_normal_user`).
        - Create a random item (`t_item`) associated with `t_normal_user`.
    2. Methods to Test:
        - Attempt to delete the item (`t_item`) using `t_another_normal_user`.
        - Verify that a `BoughtItemOfAnotherUserError` exception is raised.
    3. Validation:
        - Retrieve the item (`t_item`) from the database.
        - Assert that the item still exists and has not been deleted.
        - Assert that the item is still associated with `t_normal_user`.

    Args:
        db (Session): The database session used for the test.
    """

    # ----------------------------------------------
    # DELETE ITEM (ANOTHER USER): PREPARATION
    # ----------------------------------------------
    t_normal_user = get_test_user(db)
    t_another_normal_user = create_random_user(db)
    t_item = create_random_item(db, test_fn_name=test_delete_item_another_user.__name__, user=t_normal_user)
    # About t_item:
    #   t_item is created by t_normal_user, if t_another_normal_user tries to delete the item, an exception is raised.

    # ----------------------------------------------
    # DELETE ITEM (ANOTHER USER): METHODS TO TEST
    # ----------------------------------------------

    # Let the another_user delete the item of the normal user. This is not allowed.
    with pytest.raises(BoughtItemOfAnotherUserError):
        crud_bought_item.delete(db=db, db_obj_user=t_another_normal_user, db_obj_item=t_item)

    # ----------------------------------------------
    # DELETE ITEM (ANOTHER USER): VALIDATION
    # ----------------------------------------------

    item = crud_bought_item.get(db=db, id=t_item.id)
    assert item
    assert item.deleted is False
    assert item in t_normal_user.created_bought_items


def test_delete_item_guest_user(db: Session) -> None:
    """
    Test the deletion of an item by a guest user.
    This test verifies that a guest user is not allowed to delete an item created by a normal user.
    It performs the following steps:

    1. Preparation:
        - Create a normal user and a guest user.
        - Create a random item associated with the normal user.
    2. Methods to Test:
        - Attempt to delete the item using the guest user's credentials.
        - Expect an InsufficientPermissionsError to be raised.
    3. Validation:
        - Ensure the item still exists in the database.
        - Verify that the item is not marked as deleted.
        - Confirm that the item is still associated with the normal user.

    Args:
        db (Session): The database session used for the test.

    Raises:
        InsufficientPermissionsError: If the guest user attempts to delete the item.
    """

    # ----------------------------------------------
    # DELETE ITEM (GUEST USER): PREPARATION
    # ----------------------------------------------
    t_normal_user = get_test_user(db)
    t_guest_user = get_test_guest_user(db)
    t_item = create_random_item(db, test_fn_name=test_delete_item_guest_user.__name__, user=t_normal_user)
    # About t_item:
    #   t_item is created by t_normal_user, if t_guest_user tries to delete the item, an exception is raised.

    # ----------------------------------------------
    # DELETE ITEM (GUEST USER): METHODS TO TEST
    # ----------------------------------------------

    # Let the t_guest_user delete the item of the normal user. This is not allowed.
    with pytest.raises(InsufficientPermissionsError):
        crud_bought_item.delete(db=db, db_obj_user=t_guest_user, db_obj_item=t_item)

    # ----------------------------------------------
    # DELETE ITEM (GUEST USER): VALIDATION
    # ----------------------------------------------

    item = crud_bought_item.get(db=db, id=t_item.id)
    assert item
    assert item.deleted is False
    assert item in t_normal_user.created_bought_items
