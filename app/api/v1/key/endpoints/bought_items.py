"""
    Handles all routes to the bought-items-resource PAT-API.
"""

# pylint: disable=R0913
# pylint: disable=R0914

from typing import Any

from api.deps import verify_api_key
from api.responses import HTTP_401_RESPONSE
from api.responses import ResponseModelDetail
from api.schemas.bought_item import BoughtItemSchema
from crud.bought_item import crud_bought_item
from db.session import get_db
from fastapi import status
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

router = APIRouter()


@router.get(
    "/{item_id}",
    response_model=BoughtItemSchema,
    responses={
        **HTTP_401_RESPONSE,
        status.HTTP_404_NOT_FOUND: {"model": ResponseModelDetail, "description": "Item not found"},
    },
)
def read_bought_item_by_id(
    item_id: int,
    verified: bool = Depends(verify_api_key),
    db: Session = Depends(get_db),
) -> Any:
    """Get a specific bought item by db id."""
    item = crud_bought_item.get(db, id=item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The item with this id does not exist.")
    return item
