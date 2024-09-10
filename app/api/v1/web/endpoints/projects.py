"""
    Handles all routes to the users-resource.
"""

from typing import Any
from typing import List

from api.deps import get_current_active_adminuser
from api.deps import get_current_active_user
from api.deps import verify_token
from api.schemas.project import ProjectCreateSchema
from api.schemas.project import ProjectSchema
from api.schemas.project import ProjectUpdateSchema
from crud.project import crud_project
from db.models import ProjectModel
from db.models import UserModel
from db.session import get_db
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/", response_model=List[ProjectSchema])
def read_projects(
    db: Session = Depends(get_db),
    skip: int | None = None,
    limit: int | None = None,
    number: str | None = None,
    machine: str | None = None,
    customer: str | None = None,
    description: str | None = None,
    is_active: bool | None = None,
    designated_user_id: int | None = None,
    verified: ProjectModel = Depends(verify_token),
) -> Any:
    """Retrieve all project."""
    kwargs = locals()
    kwargs.pop("verified")
    return crud_project.get_multi(**kwargs)


@router.post("/", response_model=ProjectSchema)
def create_project(
    *,
    db: Session = Depends(get_db),
    project_in: ProjectCreateSchema,
    current_user: UserModel = Depends(get_current_active_adminuser),
) -> Any:
    """Create new project."""
    project = crud_project.get_by_number(db, number=project_in.number)
    if project:
        raise HTTPException(
            status_code=406,
            detail="The project already exists in the system.",
        )
    return crud_project.create(db, db_obj_user=current_user, obj_in=project_in)


@router.get("/my", response_model=List[ProjectSchema])
def read_project_my(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """Get current users projects."""
    return crud_project.get_by_designated_user(db, user_id=current_user.id)


@router.get("/{project_id}", response_model=ProjectSchema)
def read_project_by_id(
    project_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get a specific project by id."""
    project = crud_project.get_by_id(db, id=project_id)
    if project is None:
        raise HTTPException(
            status_code=404,
            detail="The project with this id doesn't exists in the system.",
        )
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
        raise HTTPException(
            status_code=404,
            detail="The project with this number doesn't exists in the system.",
        )
    return project


@router.put("/{project_id}", response_model=ProjectSchema)
def update_project(
    *,
    db: Session = Depends(get_db),
    project_id: int,
    project_in: ProjectUpdateSchema,
    current_user: UserModel = Depends(get_current_active_adminuser),
) -> Any:
    """Update a project by id."""
    project = crud_project.get(db, id=project_id)
    if not project:
        raise HTTPException(
            status_code=404,
            detail="The project with this id does not exist in the system.",
        )

    project_by_number = crud_project.get_by_number(db, number=project_in.number)
    if project_by_number and project_by_number.id != project_id:
        raise HTTPException(
            status_code=409,
            detail="This project number is already in use.",
        )

    return crud_project.update(db, db_obj_user=current_user, db_obj=project, obj_in=project_in)


@router.delete("/{project_id}", response_model=ProjectSchema)
def delete_project(
    *,
    db: Session = Depends(get_db),
    project_id: int,
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """Delete a project."""
    project = crud_project.get(db, id=project_id)
    return crud_project.delete(db, db_obj_project=project, db_obj_user=current_user)
