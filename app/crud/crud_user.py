"""
    Create-Read-Update-Delete: User
"""

from datetime import datetime
from typing import Any
from typing import Dict
from typing import Optional

from api.schemas import schema_user
from config import cfg
from crud.crud_base import CRUDBase
from db.models import model_user
from fastapi import HTTPException
from multilog import log
from security.pwd import get_password_hash
from security.pwd import verify_password
from sqlalchemy.orm import Session


class CRUDUser(CRUDBase[model_user.User, schema_user.UserCreate, schema_user.UserUpdate]):
    """CRUDUser class. Descendent of the CRUDBase class."""

    def get_by_id(self, db: Session, *, id: int) -> Optional[model_user.User]:
        """Returns a user by the id."""
        return db.query(model_user.User).filter(model_user.User.id == id).first()

    def get_by_username(self, db: Session, *, username: str) -> Optional[model_user.User]:
        """Returns a user by the username."""
        return db.query(model_user.User).filter(model_user.User.username == username).first()

    def get_by_email(self, db: Session, *, email: str) -> Optional[model_user.User]:
        """Returns a user by the email."""
        return db.query(model_user.User).filter(model_user.User.email == email).first()

    def create(self, db: Session, *, current_user: model_user.User, obj_in: schema_user.UserCreate) -> model_user.User:
        """Creates a user.

        Args:
            db (Session): The database session.
            obj_in (schema_user.UserCreate): The creation schema.

        Returns:
            model_user.User: The user model.
        """
        data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)
        data["created"] = datetime.utcnow()
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

        db_obj = model_user.User(**data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        log.info(
            f"Created user {db_obj.username!r} (Name={db_obj.full_name!r}, ID={db_obj.id}) "
            f"by {current_user.username!r} (Name={current_user.full_name!r}, ID={current_user.id})."
        )
        return db_obj

    def update(
        self,
        db: Session,
        *,
        current_user: model_user.User,
        db_obj: model_user.User,
        obj_in: schema_user.UserUpdate | Dict[str, Any],
    ) -> model_user.User:
        """Updates a user.

        Args:
            db (Session): The database session.
            db_obj (model_user.User): The user model.
            obj_in (schema_user.UserUpdate | Dict[str, Any]): The update schema.

        Raises:
            HTTPException: Raised if the password change doesn't match the security standard.


        Returns:
            model_user.User: The user model.
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
                    detail="The systemuser cannot be edited by another user.",
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

    def authenticate(self, db: Session, *, username: str, password: str) -> Optional[model_user.User]:
        """Authenticates a user.

        Args:
            db (Session): The database session.
            username (str): The username of the user to authenticate.
            password (str): The password of the user to authenticate.

        Returns:
            Optional[model_user.User]: The user model if the credentials are valid, \
                otherwise None.
        """
        user = self.get_by_username(db, username=username)
        if not user:
            return None
        if not verify_password(password, str(user.hashed_password)):
            return None
        return user

    def is_active(self, user: model_user.User) -> bool:
        """Checks if the user is active."""
        return bool(user.is_active)

    def is_superuser(self, user: model_user.User) -> bool:
        """Checks if a user is a superuser."""
        return bool(user.is_superuser)

    def is_adminuser(self, user: model_user.User) -> bool:
        """Checks if a user is a admin user."""
        return bool(user.is_adminuser)

    def is_guestuser(self, user: model_user.User) -> bool:
        """Checks if a user is a guest user."""
        return bool(user.is_guestuser)

    def is_systemuser(self, user: model_user.User) -> bool:
        """Checks if a user is a systemuser."""
        return bool(user.is_systemuser)


user = CRUDUser(model_user.User)
