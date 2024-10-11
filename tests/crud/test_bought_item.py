from datetime import date

import pytest
from api.schemas.bought_item import BoughtItemCreateWebSchema
from api.schemas.bought_item import BoughtItemUpdateWebSchema
from config import cfg
from crud.bought_item import crud_bought_item
from exceptions import BoughtItemAlreadyPlannedError
from exceptions import BoughtItemCannotChangeToOpenError
from exceptions import BoughtItemOfAnotherUserError
from exceptions import BoughtItemUnknownStatusError
from sqlalchemy.orm import Session

from tests.utils.bought_item import create_random_item
from tests.utils.project import create_random_project
from tests.utils.project import get_test_project
from tests.utils.user import create_random_user
from tests.utils.user import get_test_admin_user
from tests.utils.user import get_test_super_user
from tests.utils.user import get_test_user
from tests.utils.utils import random_bought_item_name
from tests.utils.utils import random_bought_item_order_number
from tests.utils.utils import random_lower_string
from tests.utils.utils import random_manufacturer
from tests.utils.utils import random_note
from tests.utils.utils import random_supplier


def test_create_item(db: Session) -> None:
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


def test_get_item(db: Session) -> None:
    # ----------------------------------------------
    # GET ITEM: PREPARATION
    # ----------------------------------------------

    t_user = get_test_user(db)
    # About t_user:
    #   This is the same user who creates the random item in the utils method below.
    #   It is also the same user, who is the designated user in the test project below.
    t_project = get_test_project(db)
    # About t_project:
    #   This is the same project, that serves as parent project for the create_random_item utils method below.
    t_item = create_random_item(db, test_fn_name=test_get_item.__name__)

    # This assertion is to check if the test utils are correct...
    # If this fails, maybe the test user hasn't been created correctly.
    assert t_item.creator == t_user
    assert t_project.designated_user == t_user

    # ----------------------------------------------
    # GET ITEM: METHODS TO TEST
    # ----------------------------------------------

    item = crud_bought_item.get(db=db, id=t_item.id)

    # ----------------------------------------------
    # GET ITEM: VALIDATION
    # ----------------------------------------------

    assert item

    assert item.project == t_item.project
    assert item.quantity == t_item.quantity
    assert item.unit == t_item.unit
    assert item.partnumber == t_item.partnumber
    assert item.order_number == t_item.order_number
    assert item.manufacturer == t_item.manufacturer

    assert item.creator_id == t_item.creator_id
    assert item.creator == t_user

    assert item.project == t_project
    assert item.project_id == t_project.id

    assert item in t_project.bought_items
    assert item in t_user.created_bought_items


def test_update_item(db: Session) -> None:
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
    # ----------------------------------------------
    # UPDATE ITEM: PREPARATION
    # ----------------------------------------------

    t_item = create_random_item(db, test_fn_name=test_update_item.__name__)
    # About t_item:
    #   This item will be created by the test user (get_test_user utils method) and
    #   it will be assigned to the test project (get_test_project utils method).
    t_normal_user = get_test_user(db)
    t_project = get_test_project(db)
    t_project_new = create_random_project(db)

    item_in = BoughtItemUpdateWebSchema(
        project_id=t_project_new.id,
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

    # ----------------------------------------------
    # UPDATE ITEM: VALIDATION
    # ----------------------------------------------

    assert item_out.id == t_item.id  # must be unchanged
    assert item_out.project == t_project_new
    assert item_out.project_id == t_project_new.id

    assert t_item in t_normal_user.created_bought_items
    assert t_item in t_project_new.bought_items
    assert t_item not in t_project.bought_items


def test_delete_item_same_user(db: Session) -> None:
    # ----------------------------------------------
    # DELETE ITEM (SAME USER): PREPARATION
    # ----------------------------------------------
    t_item = create_random_item(db, test_fn_name=test_delete_item_same_user.__name__)
    # About t_item:
    #   t_item is created by t_normal_user, so t_normal_user can delete the item.
    t_normal_user = get_test_user(db)

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


def test_delete_item_admin_user(db: Session) -> None:
    # ----------------------------------------------
    # DELETE ITEM (ADMIN USER): PREPARATION
    # ----------------------------------------------
    t_item = create_random_item(db, test_fn_name=test_delete_item_admin_user.__name__)
    # About t_item:
    #   t_item is created by t_normal_user, an admin user is allowed to delete it.
    t_normal_user = get_test_user(db)
    t_admin_user = get_test_admin_user(db)

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


def test_delete_item_another_user(db: Session) -> None:
    # ----------------------------------------------
    # DELETE ITEM (ANOTHER USER): PREPARATION
    # ----------------------------------------------
    t_item = create_random_item(db, test_fn_name=test_delete_item_another_user.__name__)
    # About t_item:
    #   t_item is created by t_normal_user, if t_another_normal_user tries to delete the item, an exception is raised.
    t_normal_user = get_test_user(db)
    t_another_normal_user = create_random_user(db)

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
