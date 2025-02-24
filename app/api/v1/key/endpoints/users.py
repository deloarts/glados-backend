"""
    Handles all routes to the users-resource PAT-API.
"""

# pylint: disable=R0913
# pylint: disable=R0914

from typing import Any

from api.deps import verify_api_key
from api.responses import HTTP_401_RESPONSE
from api.responses import ResponseModelDetail
from api.schemas.user import UserSchema
from crud.user import crud_user
from db.session import get_db
from fastapi import status
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends
from fastapi.routing import APIRouter
from locales import lang
from sqlalchemy.orm import Session

router = APIRouter()


@router.get(
    "/rfid/{rfid}",
    response_model=UserSchema,
    responses={
        **HTTP_401_RESPONSE,
        status.HTTP_403_FORBIDDEN: {"model": ResponseModelDetail, "description": "Account inactive"},
        status.HTTP_404_NOT_FOUND: {"model": ResponseModelDetail, "description": "User not found"},
    },
)
def read_user_by_rfid(
    rfid: str,
    verified: bool = Depends(verify_api_key),
    db: Session = Depends(get_db),
) -> Any:
    """Get a specific user by id."""
    user = crud_user.authenticate_rfid(db, rfid=rfid)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=lang(user).API.USER.NOT_FOUND)
    if not crud_user.is_active(user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=lang(user).API.LOGIN.INACTIVE_ACCOUNT)
    return user
