"""
    Handles all routes to the users-resource.
"""

from datetime import timedelta
from typing import Any, List

from api.deps import (
    get_current_active_superuser,
    get_current_active_user,
    verify_token,
    verify_token_superuser,
)
from crud import crud_user
from db.session import DB
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Body, Depends
from fastapi.routing import APIRouter
from models import model_user
from pydantic import EmailStr
from schemas import schema_user
from security import create_access_token
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/", response_model=List[schema_user.User])
def read_users(
    db: Session = Depends(DB.get),
    skip: int = 0,
    limit: int = 100,
    verified: model_user.User = Depends(verify_token),
) -> Any:
    """Retrieve all users."""
    return crud_user.user.get_multi(db, skip=skip, limit=limit)


@router.post("/", response_model=schema_user.User)
def create_user(
    *,
    db: Session = Depends(DB.get),
    user_in: schema_user.UserCreate,
    verified: model_user.User = Depends(verify_token_superuser),
) -> Any:
    """Create new user."""
    user = crud_user.user.get_by_email(
        db, email=user_in.email
    ) or crud_user.user.get_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=406,
            detail="The user already exists in the system.",
        )
    return crud_user.user.create(db, obj_in=user_in)


@router.put("/me", response_model=schema_user.User)
def update_user_me(
    *,
    db: Session = Depends(DB.get),
    password: str = Body(None),
    full_name: str = Body(None),
    email: EmailStr = Body(None),
    current_user: model_user.User = Depends(get_current_active_user),
) -> Any:
    """Update own user."""
    current_user_data = jsonable_encoder(current_user)
    user_in = schema_user.UserUpdate(**current_user_data)
    if password is not None:
        user_in.password = password
    if full_name is not None:
        user_in.full_name = full_name
    if email is not None:
        user_in.email = email
    user = crud_user.user.update(db, db_obj=current_user, obj_in=user_in)
    return user


@router.get("/me", response_model=schema_user.User)
def read_user_me(
    db: Session = Depends(DB.get),
    current_user: model_user.User = Depends(get_current_active_user),
) -> Any:
    """Get current user."""
    return current_user


@router.get("/{user_id}", response_model=schema_user.User)
def read_user_by_id(
    user_id: int,
    current_user: model_user.User = Depends(get_current_active_user),
    db: Session = Depends(DB.get),
) -> Any:
    """Get a specific user by id."""
    user = crud_user.user.get(db, id=user_id)
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="The user with this id doesn't exists in the system.",
        )
    if user == current_user:
        return user
    return user


@router.put("/{user_id}", response_model=schema_user.User)
def update_user(
    *,
    db: Session = Depends(DB.get),
    user_id: int,
    user_in: schema_user.UserUpdate,
    current_user: model_user.User = Depends(get_current_active_superuser),
) -> Any:
    """Update a user."""
    user = crud_user.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    user = crud_user.user.update(db, db_obj=user, obj_in=user_in)
    return user


@router.put("/me/personal-access-token", response_model=str)
def update_user_personal_access_token(
    *,
    db: Session = Depends(DB.get),
    expires_in_minutes: int,
    current_user: model_user.User = Depends(get_current_active_user),
) -> Any:
    """Updates the personal access token of an user."""
    # access_token = secrets.token_urlsafe(32)
    access_token = create_access_token(
        subject=current_user.id, expires_delta=timedelta(minutes=expires_in_minutes)
    )
    crud_user.user.update(
        db,
        db_obj=current_user,
        obj_in={"personal_access_token": access_token},
    )
    return access_token


# @router.delete("/{user_id}", response_model=schema_user.User)
# def delete_user(*, db: Session = Depends(DB.get), user_id: int) -> Any:
#     """Deletes a user."""
#     user = crud_user.user.get(db, id=user_id)
#     if not user:
#         raise HTTPException(
#             status_code=404,
#             detail="The user with this id does not exist in the system",
#         )
#     user = crud_user.user.delete(db, id=user_id)
#     return user
