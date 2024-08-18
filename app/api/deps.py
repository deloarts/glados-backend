"""
    API dependencies.
"""

from crud import crud_user
from db.models import model_user
from db.session import get_db
from fastapi import status
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends
from fastapi.param_functions import Security
from security.access import api_key_header
from security.access import get_id_from_access_token
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
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access token not valid.")


def verify_token_superuser(
    access_token_valid: bool = Depends(validate_access_token_superuser),
) -> bool:
    """
    Verifies the access token for active superusers.
    Returns True is valid, raises a http exception if not.
    """
    if access_token_valid:
        return True
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Access token not valid or not enough permissions.",
    )


def verify_token_adminuser(
    access_token_valid: bool = Depends(validate_access_token_adminuser),
) -> bool:
    """
    Verifies the access token for active adminusers.
    Returns True is valid, raises a http exception if not.
    """
    if access_token_valid:
        return True
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Access token not valid or not enough permissions.",
    )


def verify_token_guestuser(
    access_token_valid: bool = Depends(validate_access_token_guestuser),
) -> bool:
    """
    Verifies the access token for active guestusers.
    Returns True is valid, raises a http exception if not.
    """
    if access_token_valid:
        return True
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Access token not valid or not enough permissions.",
    )


def verify_personal_access_token(
    access_token_valid: bool = Depends(validate_personal_access_token),
) -> bool:
    """
    Verifies the personal access token for active users.
    Returns True is valid, raises a http exception if not.
    """
    if access_token_valid:
        return True
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Personal access token not valid.",
    )


def verify_api_key(
    api_key_valid: bool = Depends(validate_api_key),
) -> bool:
    """
    Verifies the api-key for writing.
    Returns True if valid, raises a HTTP exception if not.
    """
    if api_key_valid:
        return True
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="API key not valid or not enough permissions.",
    )


def get_current_user(db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)) -> model_user.User:
    """
    Verifies the current user by its access token. Returns the user if valid.
    Raises a HTTP exception if not.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token.")
    user_id = get_id_from_access_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials.",
        )
    user = crud_user.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return user


def get_current_active_user(
    current_user: model_user.User = Depends(get_current_user),
) -> model_user.User:
    """
    Returns the current user if active. Raises a HTTP exception if not.
    """
    if not crud_user.user.is_active(current_user):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user.")
    return current_user


def get_current_active_superuser(
    current_user: model_user.User = Depends(get_current_user),
) -> model_user.User:
    """
    Returns the current user if it's an active super user. Raises a HTTP exception if not.
    """
    if not crud_user.user.is_active(current_user):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user.")
    if not crud_user.user.is_superuser(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough privileges.")
    return current_user


def get_current_active_adminuser(
    current_user: model_user.User = Depends(get_current_user),
) -> model_user.User:
    """
    Returns the current user if it's an active admin user. Raises a HTTP exception if not.
    """
    if not crud_user.user.is_active(current_user):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user.")
    if not crud_user.user.is_adminuser(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough privileges.")
    return current_user


def get_current_active_guestuser(
    current_user: model_user.User = Depends(get_current_user),
) -> model_user.User:
    """
    Returns the current user if it's an active guest user. Raises a HTTP exception if not.
    """
    if not crud_user.user.is_active(current_user):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user.")
    if not crud_user.user.is_guestuser(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough privileges.")
    return current_user


def get_current_user_personal_access_token(
    db: Session = Depends(get_db),
    token: str = Security(api_key_header),
    verified: bool = Depends(verify_personal_access_token),
) -> model_user.User:
    """
    Verifies the current user by its personal access token. Returns the user if valid.
    Raises a HTTP exception if not.
    """
    user_id = get_id_from_access_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials.",
        )
    user = crud_user.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return user
