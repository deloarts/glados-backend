"""
    Authentication & Security.
"""

from typing import Optional

from config import cfg
from crud.api_key import crud_api_key
from crud.user import crud_user
from db.session import get_db
from fastapi.param_functions import Depends
from fastapi.param_functions import Security
from fastapi.security.api_key import APIKeyHeader
from fastapi.security.http import HTTPBasic
from fastapi.security.oauth2 import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.security import get_subject_from_access_token

basic_auth = HTTPBasic(auto_error=False)
api_key_header = APIKeyHeader(name="api_key_header", auto_error=False)
reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=cfg.security.token_url, auto_error=False)


def get_user_id_from_access_token(token: str) -> Optional[int]:
    """Returns the user id from the given token."""
    user_id = get_subject_from_access_token(token=token, persistent=False)
    if user_id is not None:
        return int(user_id)
    return None


def get_key_id_from_access_token(token: str) -> Optional[int]:
    """Returns the api key from the given token."""
    key_id = get_subject_from_access_token(token=token, persistent=True)
    if key_id is not None:
        return int(key_id)
    return None


def validate_api_key(db: Session = Depends(get_db), token: str = Security(api_key_header)) -> bool:
    """Validates the api key."""
    key_id = get_key_id_from_access_token(token)
    if key_id is not None:
        key = crud_api_key.get(db, id=key_id)
    return bool(key is not None and not key.deleted and key.api_key == token)


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
    user_id = get_user_id_from_access_token(token)
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
    user_id = get_user_id_from_access_token(token)
    if user_id is not None:
        user = crud_user.get(db, id=user_id)
        return bool(user is not None and user.is_active)
    return False


def validate_access_token_superuser(db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)) -> bool:
    """
    Validates the access token for active superusers. Same as 'validate_access_token',
    but the user must also be a superuser.
    """
    user_id = get_user_id_from_access_token(token)
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
    user_id = get_user_id_from_access_token(token)
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
    user_id = get_user_id_from_access_token(token)
    if user_id is not None:
        user = crud_user.get(db, id=user_id)
        if user is not None:
            if crud_user.is_active(user) and crud_user.is_guestuser(user):
                return True
    return False
