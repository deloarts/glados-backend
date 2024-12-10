"""
    Handles all routes to the pat-login-resource.
"""

from datetime import timedelta
from typing import Any

from api.deps import get_api_key
from api.schemas.api_key import APIKeySchema
from api.schemas.token import TokenSchema
from config import cfg
from crud.user import crud_user
from db.models import APIKeyModel
from db.session import get_db
from fastapi import status
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends
from fastapi.routing import APIRouter
from locales import lang
from security import create_access_token
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/login/test-api-key", response_model=APIKeySchema)
def test_api_key(api_key: APIKeyModel = Depends(get_api_key)) -> Any:
    """Test api key: This must be provided as api key header."""
    return api_key


@router.post("/login/rfid/{rfid}", response_model=TokenSchema)
def login_rfid(
    db: Session = Depends(get_db),
    api_key: APIKeyModel = Depends(get_api_key),
    rfid: str | None = None,
) -> Any:
    """OAuth2 compatible token login for web api, get an access token for future requests from user rfid."""
    if not cfg.security.allow_rfid_login:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="RFID login is disabled")
    if not rfid:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Invalid value for RFID login")
    user = crud_user.authenticate_rfid(db, rfid=rfid)
    if not user:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=lang(user).API.LOGIN.INCORRECT_CREDS)
    if not crud_user.is_active(user):
        raise HTTPException(status_code=400, detail=lang(user).API.LOGIN.INACTIVE_ACCOUNT)
    access_token_expires = timedelta(minutes=cfg.security.expire_minutes)
    return {
        "access_token": create_access_token(user.id, expires_delta=access_token_expires, persistent=False),
        "token_type": "bearer",
    }
