"""
    Handles all routes to the users-resource.
"""

from typing import Any
from typing import List

from api.deps import get_current_active_user
from api.deps import verify_token
from api.schemas import PageSchema
from api.schemas.project import ProjectCreateSchema
from api.schemas.project import ProjectSchema
from api.schemas.project import ProjectUpdateSchema
from crud.project import crud_project
from db.models import UserModel
from db.session import get_db
from exceptions import InsufficientPermissionsError
from exceptions import ProjectAlreadyExistsError
from fastapi import status
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends
from fastapi.routing import APIRouter
from locales import lang
from multilog import log
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/", response_model=PageSchema[ProjectSchema])
def read_projects(
    db: Session = Depends(get_db),
    skip: int | None = None,
    limit: int | None = None,
    id: int | None = None,
    number: str | None = None,
    product_number: str | None = None,
    customer: str | None = None,
    description: str | None = None,
    is_active: bool | None = None,
    designated_user_id: int | None = None,
    verified: bool = Depends(verify_token),
) -> Any:
    """Retrieve all project."""
    kwargs = locals()
    kwargs.pop("verified")
    count, projects = crud_project.get_multi(**kwargs)
    return PageSchema(
        items=[ProjectSchema.model_validate(i) for i in projects],
        total=count,
        limit=limit if limit else count,
        skip=skip if skip else 0,
    )


@router.post("/", response_model=ProjectSchema)
def create_project(
    *,
    db: Session = Depends(get_db),
    project_in: ProjectCreateSchema,
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """Create new project."""
    try:
        new_project = crud_project.create(db, db_obj_user=current_user, obj_in=project_in)
    except ProjectAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=lang(current_user).API.PROJECT.ALREADY_EXISTS,
        )
    except InsufficientPermissionsError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=lang(current_user).API.PROJECT.GUEST_USER_NO_PERMISSION
        ) from e

    return new_project


@router.get("/my", response_model=List[ProjectSchema])
def read_project_my(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """Get current users projects."""
    return crud_project.get_by_designated_user_id(db, user_id=current_user.id)


@router.get("/{project_id}", response_model=ProjectSchema)
def read_project_by_id(
    project_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get a specific project by id."""
    project = crud_project.get_by_id(db, id=project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=lang(current_user).API.PROJECT.NOT_FOUND)

    return project


@router.get("/number/{project_number}", response_model=ProjectSchema)
def read_project_by_number(
    project_number: str,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get a specific project by its number."""
    project = crud_project.get_by_number(db, number=project_number)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=lang(current_user).API.PROJECT.NOT_FOUND)

    return project


@router.get("/product-number/{product_number}", response_model=List[ProjectSchema])
def read_project_by_product_number(
    product_number: str,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get a projects with the product number number."""
    return crud_project.get_by_product_number(db, product_number=product_number)


@router.put("/{project_id}", response_model=ProjectSchema)
def update_project(
    *,
    db: Session = Depends(get_db),
    project_id: int,
    project_in: ProjectUpdateSchema,
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """Update a project by id."""
    project = crud_project.get(db, id=project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=lang(current_user).API.PROJECT.NOT_FOUND)

    try:
        updated_project = crud_project.update(db, db_obj_user=current_user, db_obj=project, obj_in=project_in)
    except ProjectAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=lang(current_user).API.PROJECT.ALREADY_EXISTS,
        )
    except InsufficientPermissionsError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=lang(current_user).API.PROJECT.UPDATE_NO_PERMISSION
        ) from e

    return updated_project


@router.delete("/{project_id}", response_model=ProjectSchema)
def delete_project(
    *,
    db: Session = Depends(get_db),
    project_id: int,
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """Delete a project."""
    project = crud_project.get(db, id=project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=lang(current_user).API.PROJECT.NOT_FOUND)

    try:
        deleted_project = crud_project.delete(db, db_obj_project=project, db_obj_user=current_user)
    except InsufficientPermissionsError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=lang(current_user).API.PROJECT.DELETE_NO_PERMISSION
        ) from e

    return deleted_project
