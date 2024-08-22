from sqlalchemy.orm import Session

from app.api.schemas.bought_item import BoughtItemCreateSchema
from app.api.schemas.bought_item import BoughtItemUpdateSchema
from app.config import cfg
from app.crud.bought_item import crud_bought_item
from tests.utils.user import create_random_user
from tests.utils.utils import random_lower_string
from tests.utils.utils import random_project


def test_create_item(db: Session) -> None:
    project = random_project()
    quantity = 1.0
    unit = cfg.items.bought.units.default
    partnumber = random_lower_string()
    definition = random_lower_string()
    manufacturer = random_lower_string()

    item_in = BoughtItemCreateSchema(
        project=project,
        machine=None,
        quantity=quantity,
        unit=unit,
        partnumber=partnumber,
        definition=definition,
        manufacturer=manufacturer,
    )
    user = create_random_user(db)
    item = crud_bought_item.create(db=db, db_obj_user=user, obj_in=item_in)

    assert item.project == project
    assert item.quantity == quantity
    assert item.unit == unit
    assert item.partnumber == partnumber
    assert item.definition == definition
    assert item.manufacturer == manufacturer

    assert item.creator_id == user.id
    assert item.creator == user


def test_get_item(db: Session) -> None:
    project = random_project()
    quantity = 1.0
    unit = cfg.items.bought.units.default
    partnumber = random_lower_string()
    definition = random_lower_string()
    manufacturer = random_lower_string()

    item_in = BoughtItemCreateSchema(
        project=project,
        machine=None,
        quantity=quantity,
        unit=unit,
        partnumber=partnumber,
        definition=definition,
        manufacturer=manufacturer,
    )
    user = create_random_user(db)
    item = crud_bought_item.create(db=db, db_obj_user=user, obj_in=item_in)
    stored_item = crud_bought_item.get(db=db, id=item.id)
    assert stored_item

    assert item.project == stored_item.project
    assert item.quantity == stored_item.quantity
    assert item.unit == stored_item.unit
    assert item.partnumber == stored_item.partnumber
    assert item.definition == stored_item.definition
    assert item.manufacturer == stored_item.manufacturer

    assert item.creator_id == stored_item.creator_id
    assert item.creator == user
    assert stored_item.creator == user


def test_update_item(db: Session) -> None:
    project = random_project()
    quantity = 1.0
    unit = cfg.items.bought.units.default
    partnumber = random_lower_string()
    partnumber_2 = f"{random_lower_string()}_2"
    definition = random_lower_string()
    manufacturer = random_lower_string()

    user = create_random_user(db)

    item_in = BoughtItemCreateSchema(
        project=project,
        machine=None,
        quantity=quantity,
        unit=unit,
        partnumber=partnumber,
        definition=definition,
        manufacturer=manufacturer,
    )
    item = crud_bought_item.create(db=db, db_obj_user=user, obj_in=item_in)

    item_update = BoughtItemUpdateSchema(
        project=project,
        machine=None,
        quantity=quantity,
        unit=unit,
        partnumber=partnumber_2,
        definition=definition,
        manufacturer=manufacturer,
    )
    item2 = crud_bought_item.update(db=db, db_obj_user=user, obj_in=item_update, db_obj_item=item)

    assert item2.id == item.id
    assert item2.project == item.project
    assert item2.quantity == quantity
    assert item2.unit == item.unit
    assert item2.partnumber == partnumber_2
    assert item2.definition == item.definition
    assert item2.manufacturer == item.manufacturer
    assert item2.creator_id == item.creator_id


def test_delete_item(db: Session) -> None:
    project = random_project()
    quantity = 1.0
    unit = cfg.items.bought.units.default
    partnumber = random_lower_string()
    definition = random_lower_string()
    manufacturer = random_lower_string()

    item_in = BoughtItemCreateSchema(
        project=project,
        machine=None,
        quantity=quantity,
        unit=unit,
        partnumber=partnumber,
        definition=definition,
        manufacturer=manufacturer,
    )
    user = create_random_user(db)
    item = crud_bought_item.create(db=db, db_obj_user=user, obj_in=item_in)
    crud_bought_item.delete(db=db, db_obj_user=user, db_obj_item=item)
    item3 = crud_bought_item.get(db=db, id=item.id)
    assert item3
    assert item3.deleted is True
