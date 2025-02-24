"""
    Handles all routes to the login-resource.
"""

from typing import Any

from api.deps import get_current_user
from api.responses import HTTP_401_RESPONSE
from api.responses import ResponseModelDetail
from api.schemas.token import TokenSchema
from api.schemas.user import UserSchema
from config import cfg
from crud.user import crud_user
from db.models import UserModel
from db.session import get_db
from fastapi import status
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends
from fastapi.routing import APIRouter
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from locales import lang
from security import create_access_token
from sqlalchemy.orm import Session

router = APIRouter()


@router.post(
    "/login/access-token",
    response_model=TokenSchema,
    responses={
        **HTTP_401_RESPONSE,
        status.HTTP_403_FORBIDDEN: {"model": ResponseModelDetail, "description": "Account inactive"},
    },
)
def login_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()) -> Any:
    """OAuth2 compatible token login, get an access token for future requests."""
    user = crud_user.authenticate(db, username=form_data.username, password=form_data.password)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=lang(user).API.LOGIN.INCORRECT_CREDS)
    if not crud_user.is_active(user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=lang(user).API.LOGIN.INACTIVE_ACCOUNT)

    return {
        "access_token": create_access_token(user.id, persistent=False),
        "token_type": "bearer",
    }


@router.post(
    "/login/test-token",
    response_model=UserSchema,
    responses={**HTTP_401_RESPONSE},
)
def test_token(current_user: UserModel = Depends(get_current_user)) -> Any:
    """Test access token."""
    return current_user
