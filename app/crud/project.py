"""
    Create-Read-Update-Delete: Project
"""

from datetime import UTC
from datetime import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

from api.schemas.project import ProjectCreateSchema
from api.schemas.project import ProjectUpdateSchema
from crud.base import CRUDBase
from crud.user import crud_user
from db.models import ProjectModel
from db.models import UserModel
from exceptions import InsufficientPermissionsError
from exceptions import ProjectAlreadyExistsError
from exceptions import UserDoesNotExistError
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
        id: str | None = None,  # pylint: disable=W0622
        number: str | None = None,
        product_number: str | None = None,
        customer: str | None = None,
        description: str | None = None,
        is_active: bool | None = None,
        designated_user_id: int | None = None,
    ) -> Tuple[int, List[ProjectModel]]:
        """Returns a list of projects.

        Args:
            db (Session): DB session.
            skip (int | None, optional): Number of items to skip (offset). Defaults to None.
            limit (int | None, optional): Number of items (limit). Defaults to None.
            id (int | None, optional): The id of the project. Defaults to None.
            number (str | None, optional): Filter the project number. Defaults to None.
            product_number (str | None, optional): Filter the product number. Defaults to None.
            customer (str | None, optional): Filter the customer. Defaults to None.
            description (str | None, optional): Filter the description. Defaults to None.
            is_active (bool | None, optional): Filter only active projects. Defaults to None.
            designated_user_id (int | None, optional): Filter projects by user. Defaults to None.

        Returns:
            List[ProjectModel]: The data as list of the model. Excludes `deleted` projects.
        """
        query = (
            db.query(self.model)
            .filter_by(
                deleted=False,
                id=id if id else self.model.id,
                is_active=is_active if is_active is not None else self.model.is_active,
                designated_user_id=designated_user_id if designated_user_id else self.model.designated_user_id,
            )
            .filter(
                self.model.number.ilike(f"%{number}%") if number else text(""),
                self.model.product_number.ilike(f"%{product_number}%") if product_number else text(""),
                self.model.customer.ilike(f"%{customer}%") if customer else text(""),
                self.model.description.ilike(f"%{description}%") if description else text(""),
            )
        )

        items: List[ProjectModel] = query.order_by(desc(self.model.number)).offset(skip).limit(limit).all()
        total: int = query.count()
        return total, items

    def get_by_id(self, db: Session, *, id: int) -> Optional[ProjectModel]:
        """Returns a project by its ID.

        Args:
            db (Session): DB session.
            id (int): The ID to lookup.

        Returns:
            Optional[ProjectModel]: The project as model if the given ID exists.
        """
        return db.query(self.model).filter(self.model.id == id).first()

    def get_by_number(self, db: Session, *, number: str) -> Optional[ProjectModel]:
        """Returns a project by the project number.

        Args:
            db (Session): DB session.
            number (str): The project number to lookup.

        Returns:
            Optional[ProjectModel]: The project as model if the given number exists.
        """
        return db.query(self.model).filter(self.model.number == number).first()

    def get_by_designated_user_id(self, db: Session, *, user_id: int) -> List[ProjectModel]:
        """Returns all projects from the designated user.

        Args:
            db (Session): DB session.
            user_id (int): The designate user ID to lookup.

        Returns:
            Optional[List[ProjectModel]]: A list of all projects as model from the given designated user.
        """
        return db.query(self.model).filter(self.model.designated_user_id == user_id).all()

    def get_by_product_number(self, db: Session, *, product_number: str) -> List[ProjectModel]:
        """Returns all projects from a product number.

        Args:
            db (Session): DB session.
            product_number (int): The product number number to lookup.

        Returns:
            Optional[List[ProjectModel]]: A list of all projects as model with the given product number.
        """
        return db.query(self.model).filter(self.model.product_number == product_number).all()

    def create(self, db: Session, *, db_obj_user: UserModel, obj_in: ProjectCreateSchema) -> ProjectModel:
        """Creates a new project.

        Args:
            db (Session): DB session.
            db_obj_user (UserModel): The user who creates the project.
            obj_in (ProjectCreateSchema): The project data as schema.

        Raises:
            ProjectAlreadyExistsError: A project with this number already exists.
            InsufficientPermissionsError: The user is not allowed to create the project.
            UserDoesNotExistError: The designated user does not exist.

        Returns:
            ProjectModel: The newly created project as model.
        """
        if self.get_by_number(db, number=obj_in.number):
            raise ProjectAlreadyExistsError(
                f"Blocked creation of a project ({obj_in.number}): "
                f"User #{db_obj_user.id} ({db_obj_user.full_name}) tried to create, but project with this number "
                "already exists."
            )

        if db_obj_user.is_guestuser:
            raise InsufficientPermissionsError(
                f"Blocked creation of a project ({obj_in.number}): "
                f"User #{db_obj_user.id} ({db_obj_user.full_name}) tried to create, but has not enough permissions."
            )

        if not crud_user.get_by_id(db, id=obj_in.designated_user_id):
            raise UserDoesNotExistError(
                f"Blocked creation of a project ({obj_in.number}): "
                f"User #{db_obj_user.id} ({db_obj_user.full_name}) tried to create, but the designated user does not "
                "exist."
            )

        # When a normal user creates a project they cannot assign another user.
        # Only a user with elevated permission can assign other users.
        # Ignore whatever user may be assigned through the api and automatically assign the normal user.
        if not db_obj_user.is_superuser and not db_obj_user.is_adminuser and not db_obj_user.is_systemuser:
            obj_in.designated_user_id = db_obj_user.id

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
            db (Session): DB session.
            db_obj_user (UserModel): The user who alters the project.
            db_obj (ProjectModel): The current project data as model.
            obj_in (ProjectUpdateSchema | Dict[str, Any]): The new project data as schema.

        Raises:
            ProjectAlreadyExistsError: A project with the given number already exists.
            InsufficientPermissionsError: The user is not allowed to alter the data.
            UserDoesNotExistError: The designated user does not exist.

        Returns:
            ProjectModel: The updated data as model.
        """
        data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)

        if (
            "number" in data
            and (existing_project := self.get_by_number(db, number=data["number"]))
            and existing_project.id != db_obj.id
        ):
            raise ProjectAlreadyExistsError(
                f"Blocked update of a project #{db_obj.id} ({db_obj.number}): "
                f"User #{db_obj_user.id} ({db_obj_user.full_name}) tried to update, but project with this number "
                "already exists."
            )

        if "designated_user_id" not in data or not crud_user.get_by_id(db, id=data["designated_user_id"]):
            raise UserDoesNotExistError(
                f"Blocked update of a project #{db_obj.id} ({db_obj.number}): "
                f"User #{db_obj_user.id} ({db_obj_user.full_name}) tried to update, but the designated user does not "
                "exist."
            )

        if (
            not db_obj_user.is_superuser
            and not db_obj_user.is_adminuser
            and not db_obj_user.is_systemuser
            and not db_obj_user.id == db_obj.designated_user_id
        ):
            raise InsufficientPermissionsError(
                f"Blocked update of a project #{db_obj.id} ({db_obj.number}): "
                f"User #{db_obj_user.id} ({db_obj_user.full_name}) tried to update, but has not enough permissions."
            )

        project = super().update(db, db_obj=db_obj, obj_in=data)
        log.info(
            f"Updated project {project.number} (ID={project.id}, DES-USER={project.designated_user_id})"
            f"by {db_obj_user.username} (Name={db_obj_user.full_name}, ID={db_obj_user.id})."
        )
        return project

    def delete(self, db: Session, *, db_obj_user: UserModel, db_obj_project: ProjectModel) -> Optional[ProjectModel]:
        """Deletes a project. The project is only marked as deleted and never really gone.

        Args:
            db (Session): DB session.
            db_obj_user (UserModel): The user who deletes the project.
            db_obj_project (ProjectModel): The project which should be deleted.

        Raises:
            InsufficientPermissionsError: The user is not allowed to delete the project.

        Returns:
            Optional[ProjectModel]: The deleted project.
        """
        if not db_obj_user.is_superuser and not db_obj_user.is_adminuser and not db_obj_user.is_systemuser:
            raise InsufficientPermissionsError(
                f"Blocked deletion of project #{db_obj_project.id} ({db_obj_project.number}): "
                f"User #{db_obj_user.id} ({db_obj_user.full_name}) tried to delete, but has not enough permissions."
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

    def is_active(self, project: ProjectModel) -> bool:
        """Checks if the user is active."""
        return bool(project.is_active)


crud_project = CRUDProject(ProjectModel)
