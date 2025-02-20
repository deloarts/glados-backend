"""
    Handles all routes to the user-time-resource.
"""

from typing import Any

from api.deps import get_current_user_personal_access_token
from api.responses import HTTP_401_RESPONSE
from api.responses import ResponseModelDetail
from api.schemas.user_time import UserTimeNoLogoutSchema
from api.schemas.user_time import UserTimeSchema
from crud.user_time import crud_user_time
from db.models import UserModel
from db.session import get_db
from exceptions import AlreadyLoggedInError
from exceptions import AlreadyLoggedOutError
from fastapi import status
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends
from fastapi.routing import APIRouter
from locales import lang
from sqlalchemy.orm import Session

router = APIRouter()


@router.get(
    "/login",
    response_model=UserTimeNoLogoutSchema,
    responses={
        **HTTP_401_RESPONSE,
        status.HTTP_404_NOT_FOUND: {"model": ResponseModelDetail, "description": "User is logged out"},
    },
)
def read_user_time_login_entry(
    current_user: UserModel = Depends(get_current_user_personal_access_token),
    db: Session = Depends(get_db),
) -> Any:
    """Get the current users login time, if they are logged in."""
    logged_in_entry = crud_user_time.get_last_login(db, db_obj_user=current_user)
    if not logged_in_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=lang(current_user).API.USERTIME.ALREADY_LOGGED_OUT,
        )
    return logged_in_entry


@router.post(
    "/login",
    response_model=UserTimeSchema,
    responses={
        **HTTP_401_RESPONSE,
        status.HTTP_406_NOT_ACCEPTABLE: {"model": ResponseModelDetail, "description": "User is already logged in"},
    },
)
def login_user(
    *,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user_personal_access_token),
) -> Any:
    try:
        return crud_user_time.login(db, db_obj_user=current_user)
    except AlreadyLoggedInError as e:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=lang(current_user).API.USERTIME.ALREADY_LOGGED_IN,
        ) from e


@router.post(
    "/logout",
    response_model=UserTimeSchema,
    responses={
        **HTTP_401_RESPONSE,
        status.HTTP_406_NOT_ACCEPTABLE: {"model": ResponseModelDetail, "description": "User is already logged out"},
    },
)
def logout_user(
    *,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user_personal_access_token),
) -> Any:
    try:
        return crud_user_time.logout(db, db_obj_user=current_user)
    except AlreadyLoggedOutError as e:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=lang(current_user).API.USERTIME.ALREADY_LOGGED_OUT,
        ) from e
