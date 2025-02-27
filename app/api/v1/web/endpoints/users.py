"""
    Handles all routes to the users-resource.
"""

from datetime import timedelta
from typing import Any
from typing import List

from api.deps import get_current_active_adminuser
from api.deps import get_current_active_user
from api.deps import verify_token
from api.responses import HTTP_401_RESPONSE
from api.responses import ResponseModelDetail
from api.schemas.user import UserCreateSchema
from api.schemas.user import UserSchema
from api.schemas.user import UserUpdateSchema
from const import Themes
from crud.user import crud_user
from db.models import UserModel
from db.session import get_db
from exceptions import EmailAlreadyExistsError
from exceptions import InsufficientPermissionsError
from exceptions import PasswordCriteriaError
from exceptions import RfidAlreadyExistsError
from exceptions import UsernameAlreadyExistsError
from fastapi import status
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends
from fastapi.routing import APIRouter
from locales import Locales
from locales import lang
from security import create_access_token
from sqlalchemy.orm import Session

router = APIRouter()


@router.get(
    "/",
    response_model=List[UserSchema],
    responses={**HTTP_401_RESPONSE},
)
def read_users(
    db: Session = Depends(get_db),
    skip: int | None = None,
    limit: int | None = None,
    verified: UserModel = Depends(verify_token),
) -> Any:
    """Retrieve all users."""
    return crud_user.get_multi(db, skip=skip, limit=limit)


@router.post(
    "/",
    response_model=UserSchema,
    responses={
        **HTTP_401_RESPONSE,
        status.HTTP_406_NOT_ACCEPTABLE: {
            "model": ResponseModelDetail,
            "description": "Username, mail or rfid already in use",
        },
    },
)
def create_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreateSchema,
    current_user: UserModel = Depends(get_current_active_adminuser),
) -> Any:
    """Create new user."""
    try:
        new_user = crud_user.create(db, current_user=current_user, obj_in=user_in)
    except UsernameAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=lang(current_user).API.USER.USERNAME_IN_USE
        ) from e
    except EmailAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=lang(current_user).API.USER.MAIL_IN_USE
        ) from e
    except RfidAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=lang(current_user).API.USER.RFID_IN_USE
        ) from e
    return new_user


@router.get(
    "/me",
    response_model=UserSchema,
    responses={**HTTP_401_RESPONSE},
)
def read_user_me(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """Get current user."""
    return current_user


@router.put(
    "/me",
    response_model=UserSchema,
    responses={
        **HTTP_401_RESPONSE,
        status.HTTP_403_FORBIDDEN: {"model": ResponseModelDetail, "description": "No permission to update user"},
        status.HTTP_404_NOT_FOUND: {"model": ResponseModelDetail, "description": "User not found"},
        status.HTTP_406_NOT_ACCEPTABLE: {
            "model": ResponseModelDetail,
            "description": "Username, mail or rfid already in use",
        },
        status.HTTP_409_CONFLICT: {"model": ResponseModelDetail, "description": "Password does not meet the criteria"},
    },
)
def update_user_me(
    *,
    db: Session = Depends(get_db),
    user_in: UserUpdateSchema,
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """Update own user."""

    if not current_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=lang(current_user).API.USER.NOT_FOUND)

    try:
        updated_user = crud_user.update(db, current_user=current_user, db_obj=current_user, obj_in=user_in)
    except PasswordCriteriaError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=lang(current_user).API.USER.PASSWORD_WEAK,
        ) from e
    except UsernameAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=lang(current_user).API.USER.USERNAME_IN_USE
        ) from e
    except EmailAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=lang(current_user).API.USER.MAIL_IN_USE
        ) from e
    except RfidAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=lang(current_user).API.USER.RFID_IN_USE
        ) from e
    except InsufficientPermissionsError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=lang(current_user).API.USER.UPDATE_NO_PERMISSION
        ) from e

    return updated_user


@router.get(
    "/{user_id}",
    response_model=UserSchema,
    responses={
        **HTTP_401_RESPONSE,
        status.HTTP_404_NOT_FOUND: {"model": ResponseModelDetail, "description": "User not found"},
    },
)
def read_user_by_id(
    user_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get a specific user by id."""
    user = crud_user.get(db, id=user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=lang(current_user).API.USER.NOT_FOUND,
        )
    if user == current_user:
        return user
    return user


@router.put(
    "/{user_id}",
    response_model=UserSchema,
    responses={
        **HTTP_401_RESPONSE,
        status.HTTP_403_FORBIDDEN: {"model": ResponseModelDetail, "description": "No permission to update user"},
        status.HTTP_404_NOT_FOUND: {"model": ResponseModelDetail, "description": "User not found"},
        status.HTTP_406_NOT_ACCEPTABLE: {
            "model": ResponseModelDetail,
            "description": "Username, mail or rfid already in use",
        },
        status.HTTP_409_CONFLICT: {"model": ResponseModelDetail, "description": "Password does not meet the criteria"},
    },
)
def update_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    user_in: UserUpdateSchema,
    current_user: UserModel = Depends(get_current_active_adminuser),
) -> Any:
    """Update a user."""
    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=lang(current_user).API.USER.NOT_FOUND)

    try:
        updated_user = crud_user.update(db, current_user=current_user, db_obj=user, obj_in=user_in)
    except PasswordCriteriaError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=lang(current_user).API.USER.PASSWORD_WEAK,
        ) from e
    except UsernameAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=lang(current_user).API.USER.USERNAME_IN_USE
        ) from e
    except EmailAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=lang(current_user).API.USER.MAIL_IN_USE
        ) from e
    except RfidAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=lang(current_user).API.USER.RFID_IN_USE
        ) from e
    except InsufficientPermissionsError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=lang(current_user).API.USER.UPDATE_NO_PERMISSION
        ) from e

    return updated_user


@router.put(
    "/me/personal-access-token",
    response_model=str,
    responses={
        **HTTP_401_RESPONSE,
        status.HTTP_403_FORBIDDEN: {"model": ResponseModelDetail, "description": "No permission to create token"},
    },
)
def update_user_personal_access_token(
    *,
    db: Session = Depends(get_db),
    expires_in_minutes: int,
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """Updates the personal access token of an user."""
    if current_user.is_guestuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=lang(current_user).API.USER.TOKEN_GUEST_NO_PERMISSION
        )

    access_token = create_access_token(
        subject=current_user.id, expires_delta=timedelta(minutes=expires_in_minutes), persistent=True
    )
    crud_user.update(
        db,
        current_user=current_user,
        db_obj=current_user,
        obj_in={"personal_access_token": access_token},
    )
    return access_token


@router.put(
    "/me/language",
    response_model=UserSchema,
    responses={**HTTP_401_RESPONSE},
)
def update_user_me_language(
    *,
    db: Session = Depends(get_db),
    language: Locales,
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """Updates the theme."""
    updated_user = crud_user.update(
        db,
        current_user=current_user,
        db_obj=current_user,
        obj_in={"language": language},
    )
    return updated_user


@router.put(
    "/me/theme",
    response_model=UserSchema,
    responses={**HTTP_401_RESPONSE},
)
def update_user_me_theme(
    *,
    db: Session = Depends(get_db),
    theme: Themes,
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """Updates the theme."""
    updated_user = crud_user.update(
        db,
        current_user=current_user,
        db_obj=current_user,
        obj_in={"theme": theme},
    )
    return updated_user
