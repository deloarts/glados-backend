from sqlalchemy.orm import Session

from app.api.schemas.bought_item import BoughtItemCreateSchema
from app.config import cfg
from app.crud.bought_item import crud_bought_item
from app.db.models import BoughtItemModel
from tests.utils.user import create_random_user
from tests.utils.utils import random_lower_string
from tests.utils.utils import random_project


def create_random_item(db: Session) -> BoughtItemModel:
    user = create_random_user(db)
    item_in = BoughtItemCreateSchema(
        project=random_project(),
        machine=None,
        quantity=1,
        unit=cfg.items.bought.units.default,
        partnumber=random_lower_string(),
        definition=random_lower_string(),
        manufacturer=random_lower_string(),
    )
    return crud_bought_item.create(db=db, db_obj_user=user, obj_in=item_in)
