"""
    Create-Read-Update-Delete: Project
"""

from datetime import UTC
from datetime import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from api.schemas.project import ProjectCreateSchema
from api.schemas.project import ProjectUpdateSchema
from crud.base import CRUDBase
from db.models import ProjectModel
from db.models import UserModel
from fastapi import HTTPException
from multilog import log
from sqlalchemy import desc
from sqlalchemy import text
from sqlalchemy.orm import Session


class CRUDProject(CRUDBase[ProjectModel, ProjectCreateSchema, ProjectUpdateSchema]):
    """CRUDProject class. Descendent of the CRUDBase class."""

    def get_multi(
        self,
        db: Session,
        *,
        skip: int | None = None,
        limit: int | None = None,
        number: str | None = None,
        machine: str | None = None,
        customer: str | None = None,
        description: str | None = None,
        is_active: bool | None = None,
        designated_user_id: int | None = None,
    ) -> List[ProjectModel]:
        return (
            db.query(self.model)
            .filter_by(
                deleted=False,
                is_active=is_active if is_active else self.model.is_active,
                designated_user_id=designated_user_id if designated_user_id else self.model.designated_user_id,
            )
            .filter(
                self.model.number.ilike(f"%{number}%") if number else text(""),
                self.model.machine.ilike(f"%{machine}%") if machine else text(""),
                self.model.customer.ilike(f"%{customer}%") if customer else text(""),
                self.model.description.ilike(f"%{description}%") if description else text(""),
            )
            .order_by(desc(self.model.number))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_id(self, db: Session, *, id: int) -> Optional[ProjectModel]:
        """Returns a project by the id."""
        return db.query(self.model).filter(self.model.id == id).first()

    def get_by_number(self, db: Session, *, number: str) -> Optional[ProjectModel]:
        """Returns a project by the project number."""
        return db.query(self.model).filter(self.model.number == number).first()

    def get_by_designated_user(self, db: Session, *, user_id: int) -> Optional[List[ProjectModel]]:
        """Returns all projects from a user."""
        return db.query(self.model).filter(self.model.designated_user_id == user_id).all()

    def create(self, db: Session, *, db_obj_user: UserModel, obj_in: ProjectCreateSchema) -> ProjectModel:
        """Creates a project.

        Args:
            db (Session): The database session.
            db_obj_user (UserModel): The user who creates the project.
            obj_in (ProjectCreateSchema): The creation data.

        Returns:
            ProjectModel: The data of the created project as model.
        """
        data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)
        data["created"] = datetime.now(UTC)

        db_obj = ProjectModel(**data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        log.info(
            f"Created project {db_obj.number} (ID={db_obj.id}, DES-USER={obj_in.designated_user_id}) "
            f"by {db_obj_user.username} (Name={db_obj_user.full_name}, ID={db_obj_user.id})."
        )
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj_user: UserModel,
        db_obj: ProjectModel,
        obj_in: ProjectUpdateSchema | Dict[str, Any],
    ) -> ProjectModel:
        """Updates a project.

        Args:
            db (Session): The database session.
            db_obj_user (UserModel): The user who alters the project.
            db_obj (ProjectModel): The project model.
            obj_in (ProjectUpdateSchema | Dict[str, Any]): The update schema.

        Returns:
            ProjectModel: The data of the created project as model.
        """
        data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)

        project = super().update(db, db_obj=db_obj, obj_in=data)
        log.info(
            f"Updated project {project.number} (ID={project.id}, DES-USER={project.designated_user_id})"
            f"by {db_obj_user.username} (Name={db_obj_user.full_name}, ID={db_obj_user.id})."
        )
        return project

    def is_active(self, project: ProjectModel) -> bool:
        """Checks if the user is active."""
        return bool(project.is_active)

    def delete(
        self, db: Session, *, db_obj_user: UserModel, db_obj_project: ProjectModel | None
    ) -> Optional[ProjectModel]:
        if not db_obj_user.is_adminuser:
            raise HTTPException(status_code=403, detail="Only admin users can delete projects.")

        if not db_obj_project:
            raise HTTPException(
                status_code=404,
                detail="The project does not exist.",
            )

        project_data = {"deleted": True, "is_active": False}
        project = super().update(db, db_obj=db_obj_project, obj_in=project_data)

        # Mark all items as deleted
        for bought_item in db_obj_project.bought_items:
            # Late import to prevent circular import error
            from crud.bought_item import crud_bought_item

            crud_bought_item.delete(db, db_obj_user=db_obj_user, db_obj_item=bought_item)
        log.info(f"User {db_obj_user.username!r} deleted the a project ({project.number}), ID={project.id}.")
        return project


crud_project = CRUDProject(ProjectModel)
