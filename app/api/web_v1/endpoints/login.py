"""
    Handles all routes to the login-resource.
"""

from datetime import timedelta
from typing import Any

from api import deps
from config import cfg
from crud import crud_user
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends
from fastapi.routing import APIRouter
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from models import model_user
from schemas import schema_token, schema_user
from security import create_access_token
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/login/access-token", response_model=schema_token.Token)
def login_access_token(
    db: Session = Depends(deps.get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """OAuth2 compatible token login, get an access token for future requests."""
    user = crud_user.user.authenticate(
        db, username=form_data.username, password=form_data.password
    )

    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password.")
    if not crud_user.user.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user.")

    access_token_expires = timedelta(minutes=cfg.security.expire_minutes)
    return {
        "access_token": create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.post("/login/test-token", response_model=schema_user.User)
def test_token(current_user: model_user.User = Depends(deps.get_current_user)) -> Any:
    """Test access token."""
    return current_user
