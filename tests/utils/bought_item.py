import sys

sys.path.append("app")

from api.schemas.bought_item import BoughtItemCreateSchema
from sqlalchemy.orm import Session

from app.config import cfg
from app.crud import crud_bought_item
from tests.utils.user import create_random_user
from tests.utils.utils import random_lower_string
from tests.utils.utils import random_project

# Important note: Throughout the app the BoughtItem model is imported this way, not like
# this: app.db.models.model_bought_item ...
# If you would import the model with `from app.db.models.model_bought_item import BoughtItem`,
# this somehow cause it to be seen as 2 different models, despite being the same file,
# resulting the pytest discovery to fail, and also to mess with the metadata instance.
from db.models.model_bought_item import BoughtItem  # type:ignore isort:skip


def create_random_item(db: Session) -> BoughtItem:
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
    return crud_bought_item.bought_item.create(db=db, db_obj_user=user, obj_in=item_in)
