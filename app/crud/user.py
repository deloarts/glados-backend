"""
    Create-Read-Update-Delete: User
"""

from datetime import UTC
from datetime import datetime
from typing import Any
from typing import Dict
from typing import Optional

from api.schemas.user import UserCreateSchema
from api.schemas.user import UserUpdateSchema
from config import cfg
from crud.base import CRUDBase
from db.models import UserModel
from fastapi import HTTPException
from multilog import log
from security.pwd import get_password_hash
from security.pwd import verify_password
from sqlalchemy.orm import Session


class CRUDUser(CRUDBase[UserModel, UserCreateSchema, UserUpdateSchema]):
    """CRUDUser class. Descendent of the CRUDBase class."""

    def get_by_id(self, db: Session, *, id: int) -> Optional[UserModel]:
        """Returns a user by the id."""
        return db.query(UserModel).filter(UserModel.id == id).first()

    def get_by_username(self, db: Session, *, username: str) -> Optional[UserModel]:
        """Returns a user by the username."""
        return db.query(UserModel).filter(UserModel.username == username).first()

    def get_by_email(self, db: Session, *, email: str) -> Optional[UserModel]:
        """Returns a user by the email."""
        return db.query(UserModel).filter(UserModel.email == email).first()

    def create(self, db: Session, *, current_user: UserModel, obj_in: UserCreateSchema) -> UserModel:
        """Creates a UserModel.

        Args:
            db (Session): The database session.
            obj_in (UserCreateSchema): The creation schema.

        Returns:
            User: The user model.
        """
        data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)
        data["created"] = datetime.now(UTC)
        data["hashed_password"] = get_password_hash(obj_in.password)
        del data["password"]

        # The systemuser can only be created by another systemuser!
        # Permissions of a systemuser cannot be edited!
        if "is_systemuser" in data and data["is_systemuser"] and current_user.is_systemuser:
            data["is_active"] = True
            data["is_superuser"] = True
            data["is_adminuser"] = True
            data["is_guestuser"] = False

        # A adminuser has all permissions, even if they aren't received via api, and is no guestuser
        elif "is_adminuser" in data and data["is_adminuser"]:
            data["is_superuser"] = True
            data["is_guestuser"] = False

        # A superuser is no guestuser
        elif "is_superuser" in data and data["is_superuser"]:
            data["is_guestuser"] = False

        db_obj = UserModel(**data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        log.info(
            f"Created user {db_obj.username!r} (Name={db_obj.full_name!r}, ID={db_obj.id}) "
            f"by {current_user.username!r} (Name={current_user.full_name!r}, ID={current_user.id})."
        )
        return db_obj

    def update(
        self, db: Session, *, current_user: UserModel, db_obj: UserModel, obj_in: UserUpdateSchema | Dict[str, Any]
    ) -> UserModel:
        """Updates a UserModel.

        Args:
            db (Session): The database session.
            db_obj (UserModel): The user model.
            obj_in (UserUpdateSchema | Dict[str, Any]): The update schema.

        Raises:
            HTTPException: Raised if the password change doesn't match the security standard.


        Returns:
            User: The user model.
        """
        data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)

        # Handle a new password
        if "password" in data:
            if len(data["password"]) < cfg.security.min_pw_len:
                raise HTTPException(
                    status_code=406,
                    detail="Password must have at least 8 characters.",
                )
            hashed_password = get_password_hash(data["password"])
            del data["password"]
            data["hashed_password"] = hashed_password

        # The systemuser can only update itself!
        # The systemuser has fixed permissions that cannot be altered.
        if db_obj.is_systemuser:
            if db_obj.id != current_user.id:
                raise HTTPException(
                    status_code=403,
                    detail="The systemuser cannot be edited by another UserModel.",
                )
            data["is_active"] = True
            data["is_superuser"] = True
            data["is_adminuser"] = True
            data["is_guestuser"] = False

        # A adminuser has all permissions and is no guestuser
        elif "is_adminuser" in data and data["is_adminuser"]:
            data["is_superuser"] = True
            data["is_guestuser"] = False

        # A superuser is no guestuser
        elif "is_superuser" in data and data["is_superuser"]:
            data["is_guestuser"] = False

        user = super().update(db, db_obj=db_obj, obj_in=data)
        log.info(
            f"Updated user {db_obj.username!r} (Name={db_obj.full_name!r}, ID={db_obj.id}) "
            f"by {current_user.username!r} (Name={current_user.full_name!r}, ID={current_user.id})."
        )
        return user

    def authenticate(self, db: Session, *, username: str, password: str) -> Optional[UserModel]:
        """Authenticates a UserModel.

        Args:
            db (Session): The database session.
            username (str): The username of the user to authenticate.
            password (str): The password of the user to authenticate.

        Returns:
            Optional[User]: The user model if the credentials are valid, \
                otherwise None.
        """
        user = self.get_by_username(db, username=username)
        if not user:
            return None
        if not verify_password(password, str(user.hashed_password)):
            return None
        return user

    def is_active(self, user: UserModel) -> bool:
        """Checks if the user is active."""
        return bool(user.is_active)

    def is_superuser(self, user: UserModel) -> bool:
        """Checks if a user is a superUserModel."""
        return bool(user.is_superuser)

    def is_adminuser(self, user: UserModel) -> bool:
        """Checks if a user is a admin UserModel."""
        return bool(user.is_adminuser)

    def is_guestuser(self, user: UserModel) -> bool:
        """Checks if a user is a guest UserModel."""
        return bool(user.is_guestuser)

    def is_systemuser(self, user: UserModel) -> bool:
        """Checks if a user is a systemUserModel."""
        return bool(user.is_systemuser)


crud_user = CRUDUser(UserModel)
