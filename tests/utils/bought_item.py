from sqlalchemy.orm import Session

from app.api.schemas.bought_item import BoughtItemCreateSchema
from app.config import cfg
from app.crud.bought_item import crud_bought_item
from app.db.models import BoughtItemModel
from tests.utils.project import get_test_project
from tests.utils.user import get_test_user
from tests.utils.utils import random_bought_item_name
from tests.utils.utils import random_bought_item_order_number
from tests.utils.utils import random_manufacturer


def create_random_item(db: Session, test_fn_name: str | None = None) -> BoughtItemModel:
    user = get_test_user(db)
    item_in = BoughtItemCreateSchema(
        project_id=get_test_project(db).id,
        quantity=1,
        unit=cfg.items.bought.units.default,
        partnumber=random_bought_item_name(),
        order_number=random_bought_item_order_number(),
        manufacturer=random_manufacturer(),
        note_general=f"Test function name: `{test_fn_name}`" or "TEST ITEM (UTILS)",
    )
    return crud_bought_item.create(db=db, db_obj_user=user, obj_in=item_in)
