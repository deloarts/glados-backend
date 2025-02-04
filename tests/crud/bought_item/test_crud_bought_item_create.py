"""
    CRUD tests (CREATE ONLY) for the bought item model
"""

from datetime import date

from api.schemas.bought_item import BoughtItemCreateWebSchema
from config import cfg
from crud.bought_item import crud_bought_item
from sqlalchemy.orm import Session

from tests.utils.project import get_test_project
from tests.utils.user import get_test_user
from tests.utils.utils import random_bought_item_name
from tests.utils.utils import random_bought_item_order_number
from tests.utils.utils import random_manufacturer
from tests.utils.utils import random_note
from tests.utils.utils import random_supplier


def test_create_item(db: Session) -> None:
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
    t_note_general = f"Test function name: `{test_create_item.__name__}`"
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

    assert item.project == t_project
    assert item.project_number == t_project.number
    assert item.product_number == t_project.product_number

    assert item in t_user.created_bought_items
    assert item in t_project.bought_items
