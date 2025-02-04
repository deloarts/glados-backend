"""
    CRUD tests (UPDATE ONLY) for the bought item model
"""

import pytest
from api.schemas.bought_item import BoughtItemUpdateWebSchema
from config import cfg
from crud.bought_item import crud_bought_item
from exceptions import BoughtItemAlreadyPlannedError
from exceptions import BoughtItemCannotChangeToOpenError
from exceptions import BoughtItemOfAnotherUserError
from exceptions import BoughtItemUnknownStatusError
from exceptions import ProjectInactiveError
from exceptions import ProjectNotFoundError
from sqlalchemy.orm import Session

from tests.utils.bought_item import create_random_item
from tests.utils.project import create_random_project
from tests.utils.project import get_test_project
from tests.utils.user import create_random_user
from tests.utils.user import get_test_super_user
from tests.utils.user import get_test_user
from tests.utils.utils import random_bought_item_name
from tests.utils.utils import random_bought_item_order_number
from tests.utils.utils import random_manufacturer


def test_update_item(db: Session) -> None:
    """
    Test the update functionality of a bought item in the database.
    This test performs the following steps:

    1. Preparation:
        - Create a random item using the `create_random_item` utility method.
        - Retrieve a test user using the `get_test_user` utility method.
        - Retrieve a test project using the `get_test_project` utility method.
        - Define the new attributes for the item to be updated.
    2. Methods to Test:
        - Call the `crud_bought_item.update` method to update the item with the new attributes.
    3. Validation:
        - Assert that the item's ID and project remain unchanged.
        - Assert that the item's quantity, unit, part number, order number, and manufacturer are updated correctly.
        - Assert that the item's creator ID remains unchanged.
        - Assert that the updated item is present in the test user's created bought items.
        - Assert that the updated item is present in the test project's bought items.

    Args:
        db (Session): The database session used for the test.
    """

    # ----------------------------------------------
    # UPDATE ITEM: PREPARATION
    # ----------------------------------------------

    t_item = create_random_item(db, test_fn_name=test_update_item.__name__)
    # About t_item:
    #   This item will be created by the test user (get_test_user utils method) and
    #   it will be assigned to the test project (get_test_project utils method)
    t_user = get_test_user(db)
    t_project = get_test_project(db)

    t_qty = 10
    t_unit = cfg.items.bought.units.values[-1]
    t_partnumber = random_bought_item_name()
    t_order_number = random_bought_item_order_number()
    t_manufacturer = random_manufacturer()

    item_in = BoughtItemUpdateWebSchema(
        project_id=t_project.id,  # A normal user (t_user in this case) can only assign the same or their project
        quantity=t_qty,
        unit=t_unit,
        partnumber=t_partnumber,
        order_number=t_order_number,
        manufacturer=t_manufacturer,
    )

    # ----------------------------------------------
    # UPDATE ITEM: METHODS TO TEST
    # ----------------------------------------------

    item_out = crud_bought_item.update(db=db, db_obj_user=t_user, obj_in=item_in, db_obj_item=t_item)

    # ----------------------------------------------
    # UPDATE ITEM: VALIDATION
    # ----------------------------------------------

    assert item_out.id == t_item.id  # must be unchanged
    assert item_out.project == t_item.project  # must be unchanged
    assert item_out.quantity == t_qty
    assert item_out.unit == t_unit
    assert item_out.partnumber == t_partnumber
    assert item_out.order_number == t_order_number
    assert item_out.manufacturer == t_manufacturer
    assert item_out.creator_id == t_item.creator_id  # mus be unchanged

    assert item_out in t_user.created_bought_items
    assert item_out in t_project.bought_items


def test_update_item_status(db: Session) -> None:
    """
    Test the update of an item's status in the database.
    This test performs the following steps:

    1. Creates a random item and several users (normal, another normal, and super user).
    2. Attempts to update the item's status using different users and checks for expected exceptions.
    3. Validates the final state of the item and its associations with users.

    The test ensures:
    - Only the super user can update the item's status to requested, ordered, and delivered.
    - Normal users cannot update the status of items created by other users.
    - Invalid status updates raise the appropriate exceptions.
    - The final state of the item is correctly reflected in the database.

    Args:
        db (Session): The database session used for the test.
    """

    # ----------------------------------------------
    # UPDATE ITEM: PREPARATION
    # ----------------------------------------------

    t_item = create_random_item(db, test_fn_name=test_update_item.__name__)
    # About t_item:
    #   This item will be created by the test user (get_test_user utils method)
    t_normal_user = get_test_user(db)
    t_another_normal_user = create_random_user(db)
    t_super_user = get_test_super_user(db)

    # ----------------------------------------------
    # UPDATE ITEM: METHODS TO TEST
    # ----------------------------------------------

    with pytest.raises(BoughtItemOfAnotherUserError):
        crud_bought_item.update_status(
            db=db, db_obj_user=t_another_normal_user, db_obj_item=t_item, status=cfg.items.bought.status.canceled
        )

    crud_bought_item.update_status(
        db=db, db_obj_user=t_super_user, db_obj_item=t_item, status=cfg.items.bought.status.requested
    )
    crud_bought_item.update_status(
        db=db, db_obj_user=t_super_user, db_obj_item=t_item, status=cfg.items.bought.status.ordered
    )
    crud_bought_item.update_status(
        db=db, db_obj_user=t_super_user, db_obj_item=t_item, status=cfg.items.bought.status.delivered
    )

    with pytest.raises(BoughtItemCannotChangeToOpenError):
        crud_bought_item.update_status(
            db=db, db_obj_user=t_super_user, db_obj_item=t_item, status=cfg.items.bought.status.open
        )

    with pytest.raises(BoughtItemUnknownStatusError):
        crud_bought_item.update_status(
            db=db, db_obj_user=t_super_user, db_obj_item=t_item, status="definitely_not_a_valid_status"
        )

    with pytest.raises(BoughtItemAlreadyPlannedError):
        crud_bought_item.update_status(
            db=db, db_obj_user=t_normal_user, db_obj_item=t_item, status=cfg.items.bought.status.lost
        )

    # ----------------------------------------------
    # UPDATE ITEM: VALIDATION
    # ----------------------------------------------

    item_out = crud_bought_item.get(db, id=t_item.id)

    assert item_out
    assert item_out.id == t_item.id  # must be unchanged

    assert item_out in t_normal_user.created_bought_items
    assert item_out not in t_normal_user.requested_bought_items
    assert item_out not in t_normal_user.ordered_bought_items

    assert item_out not in t_super_user.created_bought_items
    assert item_out in t_super_user.requested_bought_items
    assert item_out in t_super_user.ordered_bought_items


def test_update_item_assign_new_project(db: Session) -> None:
    """
    Test the update functionality of a bought item by assigning it to a new project.
    This test performs the following steps:

    1. Preparation:
       - Create a test user.
       - Create a test project.
       - Create a random item assigned to the test user and project.
       - Create a new active project and a new inactive project.
       - Prepare update schemas for assigning the item to the new active project, inactive project, and a non-existing project.
    2. Methods to Test:
       - Update the item to be assigned to the new active project.
       - Ensure updating the item to a non-existing project raises ProjectNotFoundError.
       - Ensure updating the item to an inactive project raises ProjectInactiveError.
    3. Validation:
       - Verify the item's ID remains unchanged.
       - Verify the item is assigned to the new active project.
       - Verify the item is no longer assigned to the original project.
       - Verify the item is in the user's created bought items.
       - Verify the item is in the new active project's bought items.
       - Verify the item is not in the original project's bought items.

    Args:
        db (Session): The database session used for the test.
    """

    # ----------------------------------------------
    # UPDATE ITEM: PREPARATION
    # ----------------------------------------------

    t_normal_user = get_test_user(db)
    t_project = get_test_project(db)
    t_item = create_random_item(db, test_fn_name=test_update_item.__name__, user=t_normal_user, project=t_project)
    # About t_item:
    #   This item will be created by the test user (get_test_user utils method) and
    #   it will be assigned to the test project (get_test_project utils method).

    t_project_new = create_random_project(db)
    t_project_new_inactive = create_random_project(db)
    t_project_new_inactive.is_active = False

    item_in = BoughtItemUpdateWebSchema(
        project_id=t_project_new.id,
        quantity=t_item.quantity,
        unit=t_item.unit,
        partnumber=t_item.partnumber,
        order_number=t_item.order_number,
        manufacturer=t_item.manufacturer,
    )
    item_in_inactive_project = BoughtItemUpdateWebSchema(
        project_id=t_project_new_inactive.id,
        quantity=t_item.quantity,
        unit=t_item.unit,
        partnumber=t_item.partnumber,
        order_number=t_item.order_number,
        manufacturer=t_item.manufacturer,
    )
    item_in_non_existing_project = BoughtItemUpdateWebSchema(
        project_id=9999999,
        quantity=t_item.quantity,
        unit=t_item.unit,
        partnumber=t_item.partnumber,
        order_number=t_item.order_number,
        manufacturer=t_item.manufacturer,
    )

    # ----------------------------------------------
    # UPDATE ITEM: METHODS TO TEST
    # ----------------------------------------------

    item_out = crud_bought_item.update(db=db, db_obj_user=t_normal_user, obj_in=item_in, db_obj_item=t_item)

    with pytest.raises(ProjectNotFoundError):
        crud_bought_item.update(
            db=db, db_obj_user=t_normal_user, obj_in=item_in_non_existing_project, db_obj_item=t_item
        )

    with pytest.raises(ProjectInactiveError):
        crud_bought_item.update(db=db, db_obj_user=t_normal_user, obj_in=item_in_inactive_project, db_obj_item=t_item)

    # ----------------------------------------------
    # UPDATE ITEM: VALIDATION
    # ----------------------------------------------

    assert item_out.id == t_item.id  # must be unchanged
    assert item_out.project == t_project_new
    assert item_out.project_id == t_project_new.id

    assert t_item in t_normal_user.created_bought_items
    assert t_item in t_project_new.bought_items
    assert t_item not in t_project.bought_items
