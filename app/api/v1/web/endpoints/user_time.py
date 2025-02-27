"""
    Handles all routes to the users-time-resource.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from api.deps import get_current_active_user
from api.responses import HTTP_401_RESPONSE
from api.responses import ResponseModelDetail
from api.schemas import PageSchema
from api.schemas.user_time import UserTimeCreateSchema
from api.schemas.user_time import UserTimeSchema
from api.schemas.user_time import UserTimeUpdateSchema
from crud.user_time import crud_user_time
from db.models import UserModel
from db.models import UserTimeModel
from db.session import get_db
from exceptions import AlreadyLoggedInError
from exceptions import AlreadyLoggedOutError
from exceptions import EntryOverlapsError
from exceptions import InsufficientPermissionsError
from exceptions import LoginNotTodayError
from exceptions import LoginTimeRequiredError
from exceptions import LogoutBeforeLoginError
from exceptions import MustBeLoggedOut
from exceptions import NotSameDayError
from fastapi import status
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends
from fastapi.routing import APIRouter
from locales import lang
from sqlalchemy.orm import Session

router = APIRouter()


class OptionalFieldName(str, Enum):
    note = "note"


@router.get(
    "/",
    response_model=PageSchema[UserTimeSchema],
    responses={
        **HTTP_401_RESPONSE,
    },
)
def read_user_time_entries(
    db: Session = Depends(get_db),
    db_obj_user: UserModel = Depends(get_current_active_user),
    skip: int | None = None,
    limit: int | None = None,
    id: int | None = None,
    login_from: datetime | None = None,
    login_to: datetime | None = None,
    logout_from: datetime | None = None,
    logout_to: datetime | None = None,
) -> Any:
    """Retrieve all time entries for the current user."""
    kwargs = locals()

    count, entries = crud_user_time.get_multi(**kwargs)
    return PageSchema(
        items=[UserTimeSchema.model_validate(i) for i in entries],
        total=count,
        limit=limit if limit else count,
        skip=skip if skip else 0,
    )


@router.get(
    "/login",
    response_model=UserTimeSchema,
    responses={
        **HTTP_401_RESPONSE,
        status.HTTP_404_NOT_FOUND: {"model": ResponseModelDetail, "description": "User is logged out"},
    },
)
def read_user_time_login_entry(
    db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_active_user)
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
    "/",
    response_model=UserTimeSchema,
    responses={
        **HTTP_401_RESPONSE,
        status.HTTP_406_NOT_ACCEPTABLE: {
            "model": ResponseModelDetail,
            "description": (
                "There is an issue with the given time:\n"
                " - Login time is not given\n"
                " - Logout time is before login time\n"
                " - Logout date differs from login date\n"
                " - Login must be today, if no logout time is given\n"
                " - Time overlaps with another entry"
                " - Must be logged out to log in"
            ),
        },
    },
)
def create_user_time_entry(
    *,
    db: Session = Depends(get_db),
    data_in: UserTimeCreateSchema,
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """Create new user time entry."""
    try:
        return crud_user_time.create(db, db_obj_user=current_user, obj_in=data_in)
    except LoginTimeRequiredError as e:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=lang(current_user).API.USERTIME.LOGIN_TIME_REQUIRED,
        ) from e
    except LogoutBeforeLoginError as e:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=lang(current_user).API.USERTIME.LOGIN_CANNOT_BE_AFTER_LOGOUT,
        ) from e
    except NotSameDayError as e:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=lang(current_user).API.USERTIME.LOGOUT_DATE_DIFFERS_FROM_LOGIN,
        ) from e
    except LoginNotTodayError as e:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=lang(current_user).API.USERTIME.LOGIN_MUST_BE_TODAY,
        ) from e
    except EntryOverlapsError as e:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=lang(current_user).API.USERTIME.TIME_OVERLAPS_WITH_ENTRY,
        ) from e
    except MustBeLoggedOut as e:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=lang(current_user).API.USERTIME.MUST_BE_LOGGED_OUT,
        ) from e


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
    current_user: UserModel = Depends(get_current_active_user),
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
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    try:
        return crud_user_time.logout(db, db_obj_user=current_user)
    except AlreadyLoggedOutError as e:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=lang(current_user).API.USERTIME.ALREADY_LOGGED_OUT,
        ) from e


@router.get(
    "/{entry_id}",
    response_model=UserTimeSchema,
    responses={
        **HTTP_401_RESPONSE,
        status.HTTP_403_FORBIDDEN: {"model": ResponseModelDetail, "description": "Cannot read other users entry"},
        status.HTTP_404_NOT_FOUND: {"model": ResponseModelDetail, "description": "Entry with this ID not found"},
    },
)
def read_user_time_entry_by_id(
    entry_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get a specific user time entry by id."""
    try:
        entry = crud_user_time.get(db, id=entry_id, db_obj_user=current_user)
    except InsufficientPermissionsError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=lang(current_user).API.USERTIME.CANNOT_READ_OTHER_USERS_ENTRY,
        ) from e
    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=lang(current_user).API.USERTIME.ENTRY_NOT_FOUND,
        )
    return entry


@router.put(
    "/{entry_id}",
    response_model=UserTimeSchema,
    responses={
        **HTTP_401_RESPONSE,
        status.HTTP_403_FORBIDDEN: {"model": ResponseModelDetail, "description": "Cannot handle other users entry"},
        status.HTTP_404_NOT_FOUND: {"model": ResponseModelDetail, "description": "Entry with this ID not found"},
        status.HTTP_406_NOT_ACCEPTABLE: {
            "model": ResponseModelDetail,
            "description": (
                "There is an issue with the given time:\n"
                " - Login time is not given\n"
                " - Logout time is before login time\n"
                " - Logout date differs from login date\n"
                " - Time overlaps with another entry"
            ),
        },
    },
)
def update_user_time_entry(
    *,
    db: Session = Depends(get_db),
    entry_id: int,
    data_in: UserTimeUpdateSchema,
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """Update a user time entry by id."""
    try:
        entry = crud_user_time.get(db, id=entry_id, db_obj_user=current_user)
    except InsufficientPermissionsError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=lang(current_user).API.USERTIME.CANNOT_READ_OTHER_USERS_ENTRY,
        ) from e
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=lang(current_user).API.USERTIME.ENTRY_NOT_FOUND,
        )

    try:
        update_entry = crud_user_time.update(db, db_obj_user=current_user, db_obj=entry, obj_in=data_in)
    except LoginTimeRequiredError as e:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=lang(current_user).API.USERTIME.LOGIN_TIME_REQUIRED,
        ) from e
    except LogoutBeforeLoginError as e:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=lang(current_user).API.USERTIME.LOGIN_CANNOT_BE_AFTER_LOGOUT,
        ) from e
    except NotSameDayError as e:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=lang(current_user).API.USERTIME.LOGOUT_DATE_DIFFERS_FROM_LOGIN,
        ) from e
    except EntryOverlapsError as e:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=lang(current_user).API.USERTIME.TIME_OVERLAPS_WITH_ENTRY,
        ) from e
    except InsufficientPermissionsError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=lang(current_user).API.USERTIME.CANNOT_UPDATE_OTHER_USERS_ENTRY,
        ) from e

    return update_entry


@router.put(
    "/{entry_id}/field/optional/{field_name}",
    response_model=UserTimeSchema,
    responses={
        **HTTP_401_RESPONSE,
        status.HTTP_403_FORBIDDEN: {"model": ResponseModelDetail, "description": "Cannot handle other users entry"},
        status.HTTP_404_NOT_FOUND: {"model": ResponseModelDetail, "description": "Entry with this ID not found"},
        status.HTTP_405_METHOD_NOT_ALLOWED: {
            "model": ResponseModelDetail,
            "description": "The given field name is not supported",
        },
    },
)
def update_user_time_optional_field(
    *,
    db: Session = Depends(get_db),
    entry_id: int,
    field_name: OptionalFieldName,
    value: str,
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """Updates an optional field an item. The value can be empty."""
    if field_name is OptionalFieldName.note:
        db_field = UserTimeModel.note
    else:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail=lang(current_user).API.USERTIME.URL_FIELD_NAME_NOT_SUPPORTED,
        )

    try:
        time_entry = crud_user_time.get(db, id=entry_id, db_obj_user=current_user)
    except InsufficientPermissionsError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=lang(current_user).API.USERTIME.CANNOT_READ_OTHER_USERS_ENTRY,
        ) from e
    if not time_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=lang(current_user).API.USERTIME.ENTRY_NOT_FOUND,
        )

    try:
        updated_item = crud_user_time.update_field(
            db, db_obj_user=current_user, db_obj=time_entry, db_field=db_field, value=value
        )
    except InsufficientPermissionsError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=lang(current_user).API.USERTIME.CANNOT_UPDATE_OTHER_USERS_ENTRY,
        ) from e

    return updated_item


@router.delete(
    "/{entry_id}",
    response_model=UserTimeSchema,
    responses={
        **HTTP_401_RESPONSE,
        status.HTTP_403_FORBIDDEN: {"model": ResponseModelDetail, "description": "Cannot handle other users entry"},
        status.HTTP_404_NOT_FOUND: {"model": ResponseModelDetail, "description": "Entry with this ID not found"},
    },
)
def delete_project(
    *,
    db: Session = Depends(get_db),
    entry_id: int,
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """Delete a user time entry."""
    try:
        entry = crud_user_time.get(db, id=entry_id, db_obj_user=current_user)
    except InsufficientPermissionsError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=lang(current_user).API.USERTIME.CANNOT_READ_OTHER_USERS_ENTRY,
        ) from e
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=lang(current_user).API.USERTIME.ENTRY_NOT_FOUND,
        )

    try:
        deleted_entry = crud_user_time.delete(db, db_obj=entry, db_obj_user=current_user)
    except InsufficientPermissionsError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=lang(current_user).API.USERTIME.CANNOT_DELETE_OTHER_USERS_ENTRY,
        ) from e

    return deleted_entry
