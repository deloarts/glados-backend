"""
    Handles all routes to the api-key-resource.
"""

from datetime import UTC
from datetime import datetime
from typing import Any
from typing import List

from api import deps
from api.schemas.api_key import APIKeyCreateSchema
from api.schemas.api_key import APIKeySchema
from crud.api_key import crud_api_key
from db.session import get_db
from fastapi import status
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/", response_model=List[APIKeySchema])
def read_api_keys(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    verified: bool = Depends(deps.verify_token_adminuser),
) -> Any:
    """Retrieve api keys."""
    api_keys = crud_api_key.get_multi(db, skip=skip, limit=limit)
    return api_keys


@router.get("/{api_key_id}", response_model=APIKeySchema)
def read_api_key_by_id(
    api_key_id: int,
    db: Session = Depends(get_db),
    verified: bool = Depends(deps.verify_token_adminuser),
) -> Any:
    """Get a specific api key by id."""
    api_key = crud_api_key.get(db, id=api_key_id)
    if not api_key:
        raise HTTPException(
            status_code=404,
            detail="An api key with this id does not exist in the system",
        )
    return api_key


@router.get("/deleted-keys/", response_model=List[APIKeySchema])
def read_deleted_api_keys(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    verified: bool = Depends(deps.verify_token_adminuser),
) -> Any:
    """Retrieve deleted api keys."""
    deleted_api_keys = crud_api_key.get_deleted_multi(db, skip=skip, limit=limit)
    return deleted_api_keys


@router.get("/deleted-keys/{api_key_id}", response_model=APIKeySchema)
def read_deleted_api_key_by_id(
    api_key_id: int,
    db: Session = Depends(get_db),
    verified: bool = Depends(deps.verify_token_adminuser),
) -> Any:
    """Get a specific deleted api key by id."""
    deleted_api_key = crud_api_key.get_deleted(db, id=api_key_id)
    if not deleted_api_key:
        raise HTTPException(
            status_code=404,
            detail="An api key with this id does not exist in the system",
        )
    return deleted_api_key


@router.post("/", response_model=APIKeySchema)
def create_api_key(
    *,
    db: Session = Depends(get_db),
    data_in: APIKeyCreateSchema,
    verified: bool = Depends(deps.verify_token_adminuser),
) -> Any:
    """Create an new api key."""
    if crud_api_key.get_by_name(db, name=data_in.name):
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="An api key with this name already exists",
        )
    if data_in.expiration_date < datetime.now(UTC):
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="The expiration date cannot be in the past",
        )

    return crud_api_key.create(db, obj_in=data_in)


# @router.put("/{api_key_id}", response_model=APIKeySchema)
# def update_api_key(
#     *,
#     db: Session = Depends(get_db),
#     api_key_id: int,
#     data_in: APIKeyUpdateSchema,
#     verified: bool = Depends(deps.verify_token_adminuser),
# ) -> Any:
#     """
#     Update an api key.
#     """
#     api_key = crud_crud_api_key.get(db, id=api_key_id)
#     if not api_key:
#         raise HTTPException(
#             status_code=404,
#             detail="An api key with this id does not exist in the system",
#         )
#     api_key = crud_crud_api_key.update(db, db_obj=api_key, obj_in=data_in)
#     return api_key


@router.delete("/{api_key_id}", response_model=APIKeySchema)
def delete_api_key(
    *,
    db: Session = Depends(get_db),
    api_key_id: int,
    verified: bool = Depends(deps.verify_token_adminuser),
) -> Any:
    """Deletes an api key."""
    api_key = crud_api_key.get(db, id=api_key_id)
    if not api_key:
        raise HTTPException(
            status_code=404,
            detail="An api key with this id does not exist in the system",
        )
    api_key = crud_api_key.delete(db, id=api_key_id)
    return api_key
