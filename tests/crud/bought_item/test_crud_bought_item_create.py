"""
    CRUD tests (CREATE ONLY) for the bought item model
"""

from datetime import date

import pytest
from api.schemas.bought_item import BoughtItemCreatePatSchema
from api.schemas.bought_item import BoughtItemCreateWebSchema
from config import cfg
from crud.bought_item import crud_bought_item
from exceptions import ProjectInactiveError
from exceptions import ProjectNotFoundError
from sqlalchemy.orm import Session

from tests.utils.project import create_random_project
from tests.utils.project import get_test_project
from tests.utils.user import get_test_user
from tests.utils.utils import random_bought_item_name
from tests.utils.utils import random_bought_item_order_number
from tests.utils.utils import random_manufacturer
from tests.utils.utils import random_note
from tests.utils.utils import random_supplier


def test_create_item_web(db: Session) -> None:
    """
    Test the creation of a bought item in the database.

    This test performs the following steps:
    1. Preparation: Sets up test data including user, project, and item details.
    2. Methods to Test: Calls the CRUD method to create a bought item.
    3. Validation: Asserts that the created item has the expected attributes and relationships.

    Args:
        db (Session): The database session used for the test.

    Asserts:
        - The created item's attributes match the test data.
        - The created item is associated with the correct user and project.
        - The created item is included in the user's and project's bought items.
    """

    # ----------------------------------------------
    # CREATE ITEM: PREPARATION
    # ----------------------------------------------

    t_user = get_test_user(db)
    t_project = get_test_project(db)

    t_quantity = 1.0
    t_unit = cfg.items.bought.units.default
    t_partnumber = random_bought_item_name()
    t_order_number = random_bought_item_order_number()
    t_manufacturer = random_manufacturer()

    t_supplier = random_supplier()
    t_group_1 = "TEST ITEMS"
    t_weblink = "http://www.glados.com/test"
    t_note_general = f"Test function name: `{test_create_item_web.__name__}`"
    t_note_supplier = random_note()
    t_desired_delivery_date = date.today()
    t_high_priority = True
    t_notify_on_delivery = True

    t_item_in = BoughtItemCreateWebSchema(
        project_id=t_project.id,
        quantity=t_quantity,
        unit=t_unit,
        partnumber=t_partnumber,
        order_number=t_order_number,
        manufacturer=t_manufacturer,
        supplier=t_supplier,
        group_1=t_group_1,
        weblink=t_weblink,
        note_general=t_note_general,
        note_supplier=t_note_supplier,
        desired_delivery_date=t_desired_delivery_date,
        high_priority=t_high_priority,
        notify_on_delivery=t_notify_on_delivery,
    )

    # ----------------------------------------------
    # CREATE ITEM: METHODS TO TEST
    # ----------------------------------------------

    item = crud_bought_item.create(db=db, db_obj_user=t_user, obj_in=t_item_in)

    # ----------------------------------------------
    # CREATE ITEM: VALIDATION
    # ----------------------------------------------

    assert item.project == t_project
    assert item.quantity == t_quantity
    assert item.unit == t_unit
    assert item.partnumber == t_partnumber
    assert item.order_number == t_order_number
    assert item.manufacturer == t_manufacturer

    assert item.supplier == t_supplier
    assert item.group_1 == t_group_1
    assert item.weblink == t_weblink
    assert item.note_general == t_note_general
    assert item.note_supplier == t_note_supplier
    assert item.desired_delivery_date == t_desired_delivery_date
    assert item.high_priority == t_high_priority
    assert item.notify_on_delivery == t_notify_on_delivery

    assert item.creator == t_user
    assert item.creator_id == t_user.id

    assert item.created == date.today()
    assert item.changed == date.today()

    assert item.project == t_project
    assert item.project_number == t_project.number
    assert item.product_number == t_project.product_number

    assert item in t_user.created_bought_items
    assert item in t_project.bought_items


def test_create_item_pat(db: Session) -> None:
    """
    Test the creation of a bought item using the `create` method in the CRUD operations.
    This test performs the following steps:

    1. Preparation: Sets up the necessary test data including user, project, and item details.
    2. Method Execution: Calls the `create` method to create a new bought item.
    3. Validation: Asserts that the created item has the expected attributes and is correctly associated with the user and project.

    Args:
        db (Session): The database session used for the test.

    Asserts:
        The created item has the expected project, quantity, unit, part number, order number, manufacturer, supplier, group, weblink, notes, desired delivery date, priority, and notification settings.
        The created item is associated with the correct user and project.
    """

    # ----------------------------------------------
    # CREATE ITEM: PREPARATION
    # ----------------------------------------------

    t_user = get_test_user(db)
    t_project = get_test_project(db)

    t_quantity = 1.0
    t_unit = cfg.items.bought.units.default
    t_partnumber = random_bought_item_name()
    t_order_number = random_bought_item_order_number()
    t_manufacturer = random_manufacturer()

    t_supplier = random_supplier()
    t_group_1 = "TEST ITEMS"
    t_weblink = "http://www.glados.com/test"
    t_note_general = f"Test function name: `{test_create_item_pat.__name__}`"
    t_note_supplier = random_note()
    t_desired_delivery_date = date.today()
    t_high_priority = True
    t_notify_on_delivery = True

    t_item_in = BoughtItemCreatePatSchema(
        project=t_project.number,
        quantity=t_quantity,
        unit=t_unit,
        partnumber=t_partnumber,
        order_number=t_order_number,
        manufacturer=t_manufacturer,
        supplier=t_supplier,
        group_1=t_group_1,
        weblink=t_weblink,
        note_general=t_note_general,
        note_supplier=t_note_supplier,
        desired_delivery_date=t_desired_delivery_date,
        high_priority=t_high_priority,
        notify_on_delivery=t_notify_on_delivery,
    )

    # ----------------------------------------------
    # CREATE ITEM: METHODS TO TEST
    # ----------------------------------------------

    item = crud_bought_item.create(db=db, db_obj_user=t_user, obj_in=t_item_in)

    # ----------------------------------------------
    # CREATE ITEM: VALIDATION
    # ----------------------------------------------

    assert item.project == t_project
    assert item.quantity == t_quantity
    assert item.unit == t_unit
    assert item.partnumber == t_partnumber
    assert item.order_number == t_order_number
    assert item.manufacturer == t_manufacturer

    assert item.supplier == t_supplier
    assert item.group_1 == t_group_1
    assert item.weblink == t_weblink
    assert item.note_general == t_note_general
    assert item.note_supplier == t_note_supplier
    assert item.desired_delivery_date == t_desired_delivery_date
    assert item.high_priority == t_high_priority
    assert item.notify_on_delivery == t_notify_on_delivery

    assert item.creator == t_user
    assert item.creator_id == t_user.id

    assert item.created == date.today()
    assert item.changed == date.today()

    assert item.project == t_project
    assert item.project_number == t_project.number
    assert item.product_number == t_project.product_number

    assert item in t_user.created_bought_items
    assert item in t_project.bought_items


def test_create_item_wrong_db_in_instance(db: Session) -> None:
    """
    Test the creation of a bought item with an invalid database instance type.
    This test ensures that the `crud_bought_item.create` method raises a `ValueError`
    when provided with an invalid database instance type. The test uses the minimum
    required data for the `BoughtItemCreateWebSchema` to ensure that the exception
    is due to the invalid instance type and not because of missing data.

    Args:
        db (Session): The database session used for the test.

    Raises:
        ValueError: If the `crud_bought_item.create` method is called with an invalid
                    database instance type.
    """

    # ----------------------------------------------
    # CREATE ITEM: PREPARATION
    # ----------------------------------------------

    t_user = get_test_user(db)

    t_quantity = 1.0
    t_unit = cfg.items.bought.units.default
    t_partnumber = random_bought_item_name()
    t_order_number = random_bought_item_order_number()
    t_manufacturer = random_manufacturer()

    t_item_in = BoughtItemCreateWebSchema(
        project_id=9999999,
        quantity=t_quantity,
        unit=t_unit,
        partnumber=t_partnumber,
        order_number=t_order_number,
        manufacturer=t_manufacturer,
    ).model_dump()

    # ----------------------------------------------
    # CREATE ITEM: METHODS TO TEST
    # ----------------------------------------------

    with pytest.raises(ValueError):
        crud_bought_item.create(db=db, db_obj_user=t_user, obj_in=t_item_in)  # type: ignore


def test_create_item_web_no_project(db: Session) -> None:
    """
    Test the creation of a bought item without an associated project using the WEB API.
    This test verifies that attempting to create a bought item with a non-existent
    project ID raises a ProjectNotFoundError.
    Steps:

    1. Prepare test data including a test user and item details.
    2. Attempt to create the item using the CRUD operation.
    3. Assert that a ProjectNotFoundError is raised.

    Args:
        db (Session): The database session used for the test.

    Raises:
        ProjectNotFoundError: If the project ID does not exist.
    """

    # ----------------------------------------------
    # CREATE ITEM: PREPARATION
    # ----------------------------------------------

    t_user = get_test_user(db)

    t_quantity = 1.0
    t_unit = cfg.items.bought.units.default
    t_partnumber = random_bought_item_name()
    t_order_number = random_bought_item_order_number()
    t_manufacturer = random_manufacturer()

    t_item_in = BoughtItemCreateWebSchema(
        project_id=9999999,
        quantity=t_quantity,
        unit=t_unit,
        partnumber=t_partnumber,
        order_number=t_order_number,
        manufacturer=t_manufacturer,
    )

    # ----------------------------------------------
    # CREATE ITEM: METHODS TO TEST
    # ----------------------------------------------

    with pytest.raises(ProjectNotFoundError):
        crud_bought_item.create(db=db, db_obj_user=t_user, obj_in=t_item_in)


def test_create_item_pat_no_project(db: Session) -> None:
    """
    Test the creation of a bought item with a non-existent project using the personal-access-token (PAT) API.
    This test verifies that attempting to create a bought item with a project
    ID that does not exist raises a ProjectNotFoundError.

    Args:
        db (Session): The database session used for the test.

    Raises:
        ProjectNotFoundError: If the project ID does not exist.
    """

    # ----------------------------------------------
    # CREATE ITEM: PREPARATION
    # ----------------------------------------------

    t_user = get_test_user(db)

    t_quantity = 1.0
    t_unit = cfg.items.bought.units.default
    t_partnumber = random_bought_item_name()
    t_order_number = random_bought_item_order_number()
    t_manufacturer = random_manufacturer()

    t_item_in = BoughtItemCreatePatSchema(
        project="9999999",
        quantity=t_quantity,
        unit=t_unit,
        partnumber=t_partnumber,
        order_number=t_order_number,
        manufacturer=t_manufacturer,
    )

    # ----------------------------------------------
    # CREATE ITEM: METHODS TO TEST
    # ----------------------------------------------

    with pytest.raises(ProjectNotFoundError):
        crud_bought_item.create(db=db, db_obj_user=t_user, obj_in=t_item_in)


def test_create_item_web_inactive_project(db: Session) -> None:
    """
    Test case for creating a bought item via the web API when the associated project is inactive.
    This test ensures that attempting to create a bought item for a project that is marked as inactive
    raises a ProjectInactiveError.

    Steps:
        1. Retrieve a test user from the database.
        2. Create a random project and set its status to inactive.
        3. Define the attributes for the bought item to be created.
        4. Attempt to create the bought item using the CRUD operation.
        5. Verify that a ProjectInactiveError is raised.

    Args:
        db (Session): The database session used for the test.

    Raises:
        ProjectInactiveError: If the project associated with the bought item is inactive.
    """

    # ----------------------------------------------
    # CREATE ITEM: PREPARATION
    # ----------------------------------------------

    t_user = get_test_user(db)
    t_project = create_random_project(db)
    t_project.is_active = False

    t_quantity = 1.0
    t_unit = cfg.items.bought.units.default
    t_partnumber = random_bought_item_name()
    t_order_number = random_bought_item_order_number()
    t_manufacturer = random_manufacturer()

    t_item_in = BoughtItemCreateWebSchema(
        project_id=t_project.id,
        quantity=t_quantity,
        unit=t_unit,
        partnumber=t_partnumber,
        order_number=t_order_number,
        manufacturer=t_manufacturer,
    )

    # ----------------------------------------------
    # CREATE ITEM: METHODS TO TEST
    # ----------------------------------------------

    with pytest.raises(ProjectInactiveError):
        crud_bought_item.create(db=db, db_obj_user=t_user, obj_in=t_item_in)


def test_create_item_pat_inactive_project(db: Session) -> None:
    """
    Test case for creating a bought item using the personal-access-token (PAT) API
    when the associated project is inactive.
    This test ensures that attempting to create a bought item for an inactive project
    raises a ProjectInactiveError.

    Steps:
        1. Create a test user.
        2. Create a random project and set its status to inactive.
        3. Define the item details including quantity, unit, part number, order number, and manufacturer.
        4. Attempt to create the bought item using the PAT API.
        5. Verify that a ProjectInactiveError is raised.

    Args:
        db (Session): The database session used for the test.

    Raises:
        ProjectInactiveError: If the project associated with the bought item is inactive.
    """

    # ----------------------------------------------
    # CREATE ITEM: PREPARATION
    # ----------------------------------------------

    t_user = get_test_user(db)
    t_project = create_random_project(db)
    t_project.is_active = False

    t_quantity = 1.0
    t_unit = cfg.items.bought.units.default
    t_partnumber = random_bought_item_name()
    t_order_number = random_bought_item_order_number()
    t_manufacturer = random_manufacturer()

    t_item_in = BoughtItemCreatePatSchema(
        project=t_project.number,
        quantity=t_quantity,
        unit=t_unit,
        partnumber=t_partnumber,
        order_number=t_order_number,
        manufacturer=t_manufacturer,
    )

    # ----------------------------------------------
    # CREATE ITEM: METHODS TO TEST
    # ----------------------------------------------

    with pytest.raises(ProjectInactiveError):
        crud_bought_item.create(db=db, db_obj_user=t_user, obj_in=t_item_in)
