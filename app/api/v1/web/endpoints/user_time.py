"""
    Handles all routes to the users-time-resource.
"""

from datetime import date
from datetime import datetime
from enum import Enum
from typing import Any
from typing import List

from api.deps import get_current_active_user
from api.deps import verify_token
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
from exceptions import LoginTimeRequiredError
from exceptions import LogoutBeforeLoginError
from exceptions import MustBeLoggedOut
from exceptions import NotSameDayError
from fastapi import status
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends
from fastapi.routing import APIRouter
from locales import lang
from multilog import log
from sqlalchemy.orm import Session

router = APIRouter()


class OptionalFieldName(str, Enum):
    note = "note"


@router.get("/", response_model=PageSchema[UserTimeSchema])
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


@router.post("/", response_model=UserTimeSchema)
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
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Login time required") from e
    except LogoutBeforeLoginError as e:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Login cannot be after logout") from e
    except NotSameDayError as e:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Logout date differs from login date"
        ) from e
    except EntryOverlapsError as e:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="The given time overlaps with an existing entry"
        ) from e
    except MustBeLoggedOut as e:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Cannot create entry while logged in"
        ) from e


@router.post("/login", response_model=UserTimeSchema)
def login_user(
    *,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    try:
        return crud_user_time.login(db, db_obj_user=current_user)
    except AlreadyLoggedInError as e:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Already logged in") from e


@router.post("/logout", response_model=UserTimeSchema)
def logout_user(
    *,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    try:
        return crud_user_time.logout(db, db_obj_user=current_user)
    except AlreadyLoggedOutError as e:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Already logged out") from e


@router.get("/{entry_id}", response_model=UserTimeSchema)
def read_user_time_entry_by_id(
    entry_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get a specific user time entry by id."""
    entry = crud_user_time.get(db, id=entry_id)
    if entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Time entry not found")
    return entry


@router.put("/{entry_id}", response_model=UserTimeSchema)
def update_user_time_entry(
    *,
    db: Session = Depends(get_db),
    entry_id: int,
    data_in: UserTimeUpdateSchema,
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """Update a user time entry by id."""
    entry = crud_user_time.get(db, id=entry_id)
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Time entry not found")

    try:
        update_entry = crud_user_time.update(db, db_obj_user=current_user, db_obj=entry, obj_in=data_in)
    except LoginTimeRequiredError as e:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Login time required") from e
    except LogoutBeforeLoginError as e:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Login cannot be after logout") from e
    except NotSameDayError as e:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Logout date differs from login date"
        ) from e
    except EntryOverlapsError as e:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="The given time overlaps with an existing entry"
        ) from e
    except InsufficientPermissionsError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot update another users entry") from e

    return update_entry


@router.put("/{entry_id}/field/optional/{field_name}", response_model=UserTimeSchema)
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Field not found")

    time_entry = crud_user_time.get(db, id=entry_id)
    if not time_entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entry not found")

    try:
        updated_item = crud_user_time.update_field(
            db, db_obj_user=current_user, db_obj=time_entry, db_field=db_field, value=value
        )
    except InsufficientPermissionsError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No permission to update entry") from e

    return updated_item


@router.delete("/{entry_id}", response_model=UserTimeSchema)
def delete_project(
    *,
    db: Session = Depends(get_db),
    entry_id: int,
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """Delete a user time entry."""
    entry = crud_user_time.get(db, id=entry_id)
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entry not found")

    try:
        deleted_entry = crud_user_time.delete(db, db_obj=entry, db_obj_user=current_user)
    except InsufficientPermissionsError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No permission to delete entry") from e

    return deleted_entry
