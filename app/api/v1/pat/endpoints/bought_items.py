"""
    Handles all routes to the bought-items-resource PAT-API.
"""

# pylint: disable=R0913
# pylint: disable=R0914

from typing import Any

from api.deps import get_current_user_personal_access_token
from api.deps import verify_personal_access_token
from api.schemas.bought_item import BoughtItemCreateSchema
from api.schemas.bought_item import BoughtItemSchema
from crud.bought_item import crud_bought_item
from db.models import UserModel
from db.session import get_db
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/{item_id}", response_model=BoughtItemSchema)
def read_bought_item_by_id(
    item_id: int,
    verified: bool = Depends(verify_personal_access_token),
    db: Session = Depends(get_db),
) -> Any:
    """Get a specific bought item by db id."""
    item = crud_bought_item.get(db, id=item_id)
    if not item:
        raise HTTPException(
            status_code=404,
            detail="The item with this id does not exist.",
        )
    return item


@router.post("/", response_model=BoughtItemSchema)
def create_bought_item(
    *,
    db: Session = Depends(get_db),
    obj_in: BoughtItemCreateSchema,
    current_user: UserModel = Depends(get_current_user_personal_access_token),
) -> Any:
    """Create new bought item."""
    return crud_bought_item.create(db, db_obj_user=current_user, obj_in=obj_in)
