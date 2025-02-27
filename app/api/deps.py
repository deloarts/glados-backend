"""
    API dependencies.
"""

from crud.api_key import crud_api_key
from crud.user import crud_user
from db.models import APIKeyModel
from db.models import UserModel
from db.session import get_db
from fastapi import status
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends
from fastapi.param_functions import Security
from locales import lang
from security.access import api_key_header
from security.access import get_key_id_from_access_token
from security.access import get_user_id_from_access_token
from security.access import reusable_oauth2
from security.access import validate_access_token
from security.access import validate_access_token_adminuser
from security.access import validate_access_token_guestuser
from security.access import validate_access_token_superuser
from security.access import validate_api_key
from security.access import validate_personal_access_token
from sqlalchemy.orm import Session


def verify_token(access_token_valid: bool = Depends(validate_access_token)) -> bool:
    """
    Verifies the access token for active users.
    Returns True is valid, raises a http exception if not.
    """
    if access_token_valid:
        return True
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access token not valid")


def verify_token_superuser(access_token_valid: bool = Depends(validate_access_token_superuser)) -> bool:
    """
    Verifies the access token for active superusers.
    Returns True is valid, raises a http exception if not.
    """
    if access_token_valid:
        return True
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Access token not valid or not enough permissions",
    )


def verify_token_adminuser(access_token_valid: bool = Depends(validate_access_token_adminuser)) -> bool:
    """
    Verifies the access token for active adminusers.
    Returns True is valid, raises a http exception if not.
    """
    if access_token_valid:
        return True
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Access token not valid or not enough permissions",
    )


def verify_token_guestuser(access_token_valid: bool = Depends(validate_access_token_guestuser)) -> bool:
    """
    Verifies the access token for active guestusers.
    Returns True is valid, raises a http exception if not.
    """
    if access_token_valid:
        return True
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Access token not valid or not enough permissions",
    )


def verify_personal_access_token(access_token_valid: bool = Depends(validate_personal_access_token)) -> bool:
    """
    Verifies the personal access token for active users.
    Returns True is valid, raises a http exception if not.
    """
    if access_token_valid:
        return True
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Personal access token not valid",
    )


def verify_api_key(api_key_valid: bool = Depends(validate_api_key)) -> bool:
    """
    Verifies the api-key for writing.
    Returns True if valid, raises a HTTP exception if not.
    """
    if api_key_valid:
        return True
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="API key not valid or not enough permissions",
    )


def get_api_key(db: Session = Depends(get_db), token: str = Security(api_key_header)) -> APIKeyModel:
    """
    Verifies the api-key for writing.
    Returns True if valid, raises a HTTP exception if not.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid api key token")
    key_id = get_key_id_from_access_token(token)
    if not key_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    key = crud_api_key.get(db, id=key_id)
    if not key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API key not found")
    if key.api_key != token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token doesn't match")
    return key


def get_current_user(db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)) -> UserModel:
    """
    Verifies the current user by its access token. Returns the user if valid.
    Raises a HTTP exception if not.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")
    user_id = get_user_id_from_access_token(token)

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def get_current_active_user(
    current_user: UserModel = Depends(get_current_user),
) -> UserModel:
    """
    Returns the current user if active. Raises a HTTP exception if not.
    """
    if not crud_user.is_active(current_user):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=lang(current_user).API.DEPS.INACTIVE)
    return current_user


def get_current_active_superuser(
    current_user: UserModel = Depends(get_current_user),
) -> UserModel:
    """
    Returns the current user if it's an active super user. Raises a HTTP exception if not.
    """
    if not crud_user.is_active(current_user):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=lang(current_user).API.DEPS.INACTIVE)
    if not crud_user.is_superuser(current_user):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=lang(current_user).API.DEPS.SUPERUSER_REQUIRED
        )
    return current_user


def get_current_active_adminuser(
    current_user: UserModel = Depends(get_current_user),
) -> UserModel:
    """
    Returns the current user if it's an active admin user. Raises a HTTP exception if not.
    """
    if not crud_user.is_active(current_user):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=lang(current_user).API.DEPS.INACTIVE)
    if not crud_user.is_adminuser(current_user):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=lang(current_user).API.DEPS.ADMINUSER_REQUIRED
        )
    return current_user


def get_current_active_guestuser(
    current_user: UserModel = Depends(get_current_user),
) -> UserModel:
    """
    Returns the current user if it's an active guest user. Raises a HTTP exception if not.
    """
    if not crud_user.is_active(current_user):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=lang(current_user).API.DEPS.INACTIVE)
    if not crud_user.is_guestuser(current_user):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=lang(current_user).API.DEPS.GUESTUSER_REQUIRED
        )
    return current_user


def get_current_user_personal_access_token(
    db: Session = Depends(get_db),
    token: str = Security(api_key_header),
    verified: bool = Depends(verify_personal_access_token),
) -> UserModel:
    """
    Verifies the current user by its personal access token. Returns the user if valid.
    Raises a HTTP exception if not. User must be active.
    """
    user_id = get_user_id_from_access_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    if user.personal_access_token != token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token doesn't match")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is inactive")
    return user
