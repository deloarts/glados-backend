"""
    Handles all routes to the users-resource.
"""

from typing import Any

from api.deps import verify_personal_access_token
from api.schemas.project import ProjectSchema
from crud.project import crud_project
from db.session import get_db
from fastapi import status
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/{project_id}", response_model=ProjectSchema)
def read_project_by_id(
    project_id: int,
    verified: bool = Depends(verify_personal_access_token),
    db: Session = Depends(get_db),
) -> Any:
    """Get a specific project by id."""
    project = crud_project.get_by_id(db, id=project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The project does not exist")

    return project


@router.get("/number/{project_number}", response_model=ProjectSchema)
def read_project_by_number(
    project_number: str,
    verified: bool = Depends(verify_personal_access_token),
    db: Session = Depends(get_db),
) -> Any:
    """Get a specific project by its number."""
    project = crud_project.get_by_number(db, number=project_number)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The project does not exist")

    return project
