"""
    Handles all routes to the bought-items-resource PAT-API.
"""

# pylint: disable=R0913
# pylint: disable=R0914

from typing import Any

from api.deps import get_current_user_personal_access_token
from api.deps import verify_personal_access_token
from api.responses import HTTP_401_RESPONSE
from api.responses import ResponseModelDetail
from api.schemas.bought_item import BoughtItemCreatePatSchema
from api.schemas.bought_item import BoughtItemSchema
from crud.bought_item import crud_bought_item
from db.models import UserModel
from db.session import get_db
from exceptions import InsufficientPermissionsError
from exceptions import ProjectInactiveError
from exceptions import ProjectNotFoundError
from fastapi import status
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends
from fastapi.routing import APIRouter
from locales import lang
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
    current_user: UserModel = Depends(get_current_user_personal_access_token),
    db: Session = Depends(get_db),
) -> Any:
    """Get a specific bought item by db id."""
    item = crud_bought_item.get(db, id=item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=lang(current_user).API.BOUGHTITEM.ITEM_NOT_FOUND,
        )
    return item


@router.post(
    "/",
    response_model=BoughtItemSchema,
    responses={
        **HTTP_401_RESPONSE,
        status.HTTP_403_FORBIDDEN: {
            "model": ResponseModelDetail,
            "description": "User has no permission or project is inactive",
        },
        status.HTTP_404_NOT_FOUND: {"model": ResponseModelDetail, "description": "Project not found"},
    },
)
def create_bought_item(
    *,
    db: Session = Depends(get_db),
    obj_in: BoughtItemCreatePatSchema,
    current_user: UserModel = Depends(get_current_user_personal_access_token),
) -> Any:
    """Create new bought item."""
    try:
        item = crud_bought_item.create(db, db_obj_user=current_user, obj_in=obj_in)
    except InsufficientPermissionsError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.CREATE_NO_PERMISSION
        ) from e
    except ProjectInactiveError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.PROJECT_INACTIVE
        ) from e
    except ProjectNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=lang(current_user).API.BOUGHTITEM.PROJECT_NOT_FOUND
        ) from e
    return item
