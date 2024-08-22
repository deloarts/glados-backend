"""
    Authentication & Security.
"""

from datetime import UTC
from datetime import datetime
from datetime import timedelta
from typing import Any
from typing import Optional

from api.schemas.token import TokenPayloadSchema
from config import cfg
from const import SECRET_KEY
from crud import crud_api_key
from crud.crud_user import crud_user
from db.session import get_db
from fastapi.param_functions import Depends
from fastapi.param_functions import Security
from fastapi.security.api_key import APIKeyHeader
from fastapi.security.http import HTTPBasic
from fastapi.security.oauth2 import OAuth2PasswordBearer
from jose import jwt
from multilog import log
from pydantic import ValidationError
from sqlalchemy.orm import Session

basic_auth = HTTPBasic(auto_error=False)
api_key_header = APIKeyHeader(name="api_key_header", auto_error=False)
reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=cfg.security.token_url, auto_error=False)


def get_secret_key() -> str:
    """
    Returns the secret key. Return the key from the config file if the app runs in
    debug mode, creates a new key otherwise.
    """
    if cfg.debug and cfg.security.debug_secret_key:
        log.debug("Using debug secret key from config-file.")
        return cfg.security.debug_secret_key
    log.debug("Using generated secret key.")
    return SECRET_KEY


def create_access_token(subject: str | Any, expires_delta: Optional[timedelta] = None) -> str:
    """Creates and returns a new reusable OAuth2 access token.

    Args:
        subject (str | Any): The subject to encode (most times the user ID).
        expires_delta (Optional[timedelta], optional): The expiration time in minutes. \
            Defaults to None. If None, the value from the config file is used.

    Returns:
        str: A jwt encoded access token.
    """
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=cfg.security.expire_minutes)

    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, get_secret_key(), algorithm=cfg.security.algorithm)
    return encoded_jwt


def get_id_from_access_token(token: str) -> Optional[int]:
    """Extracts the subject from the access token.

    Args:
        token (_type_): A jwt access token.

    Returns:
        Optional[int]: The subject (user id) from the given token.
    """
    if not token:
        return None
    try:
        payload = jwt.decode(token, get_secret_key(), algorithms=[cfg.security.algorithm])
        token_data = TokenPayloadSchema(**payload)
    except (ValidationError, Exception):
        return None
    return token_data.sub  # a.k.a the id


def validate_api_key(api_key: str = Security(api_key_header), db: Session = Depends(get_db)) -> bool:
    """Validates the api key."""
    if cfg.debug and api_key == cfg.security.debug_api_key:
        log.warning("Authorized using debug api key")
        return True

    key_in_db = crud_api_key.api_key.get_by_api_key(db, key=api_key)
    return bool(key_in_db)


def validate_personal_access_token(
    db: Session = Depends(get_db),
    token: str = Security(api_key_header),
) -> bool:
    """
    Validates the personal access token. Validation requires: The token must be
    valid (the secret key must match), the encoded user ID must be present in the DB,
    the user must be active, and the token must be stored in the user's account.

    Note:
        - A user can only have one personal access token at a time.
        - The token will be invalid as soon as the server restarts (the secret key is
            created new with every restart).
        - This is not the OAuth2 token! This is the personal access token.

    Args:
        db (Session, optional): The DB session.
        token (str, optional): The token, provided by the client in the API key header.

    Returns:
        bool: True if the validation was successful, otherwise False.
    """
    user_id = get_id_from_access_token(token)
    if user_id is not None:
        user = crud_user.get(db, id=user_id)
        return bool(user is not None and user.is_active and user.personal_access_token == token)
    return False


def validate_access_token(db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)) -> bool:
    """
    Validates the access token for active users. Validation requires: The token must be
    valid (the secret key must match), the encoded user ID must be present in the DB and
    the user must be active.

    Args:
        db (Session, optional): The DB session.
        token (str, optional): The token OAuth2 token, provided by the client.

    Returns:
        bool: True if the validation was successful, otherwise False.
    """
    user_id = get_id_from_access_token(token)
    if user_id is not None:
        user = crud_user.get(db, id=user_id)
        return bool(user is not None and user.is_active)
    return False


def validate_access_token_superuser(db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)) -> bool:
    """
    Validates the access token for active superusers. Same as 'validate_access_token',
    but the user must also be a superuser.
    """
    user_id = get_id_from_access_token(token)
    if user_id is not None:
        user = crud_user.get(db, id=user_id)
        if user is not None:
            if crud_user.is_active(user) and crud_user.is_superuser(user):
                return True
    return False


def validate_access_token_adminuser(db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)) -> bool:
    """
    Validates the access token for active adminusers. Same as 'validate_access_token',
    but the user must also be a adminuser.
    """
    user_id = get_id_from_access_token(token)
    if user_id is not None:
        user = crud_user.get(db, id=user_id)
        if user is not None:
            if crud_user.is_active(user) and crud_user.is_adminuser(user):
                return True
    return False


def validate_access_token_guestuser(db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)) -> bool:
    """
    Validates the access token for active guestusers. Same as 'validate_access_token',
    but the user must also be a guestuser.
    """
    user_id = get_id_from_access_token(token)
    if user_id is not None:
        user = crud_user.get(db, id=user_id)
        if user is not None:
            if crud_user.is_active(user) and crud_user.is_guestuser(user):
                return True
    return False
