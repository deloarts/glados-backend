"""
    Create-Read-Update-Delete: User
"""

from datetime import datetime
from typing import Any, Dict, Optional

from config import cfg
from crud.crud_base import CRUDBase
from fastapi import HTTPException
from models import model_user
from multilog import log
from schemas import schema_user
from security import get_password_hash, verify_password
from sqlalchemy.orm import Session


class CRUDUser(
    CRUDBase[model_user.User, schema_user.UserCreate, schema_user.UserUpdate]
):
    """CRUDUser class. Descendent of the CRUDBase class."""

    def get_by_username(
        self, db: Session, *, username: str
    ) -> Optional[model_user.User]:
        """Returns a user by the username."""
        return (
            db.query(model_user.User)
            .filter(model_user.User.username == username)
            .first()
        )

    def get_by_email(self, db: Session, *, email: str) -> Optional[model_user.User]:
        """Returns a user by the email."""
        return db.query(model_user.User).filter(model_user.User.email == email).first()

    def create(self, db: Session, *, obj_in: schema_user.UserCreate) -> model_user.User:
        """Creates a user.

        Args:
            db (Session): The database session.
            obj_in (schema_user.UserCreate): The creation schema.

        Returns:
            model_user.User: The user model.
        """
        data = obj_in if isinstance(obj_in, dict) else obj_in.dict(exclude_unset=True)
        data["created"] = datetime.utcnow()
        data["hashed_password"] = get_password_hash(obj_in.password)
        del data["password"]

        if "is_systemuser" in data and data["is_systemuser"]:
            data["is_active"] = True
            data["is_superuser"] = True

        db_obj = model_user.User(**data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        log.info(
            f"Created user {db_obj.username!r} ({db_obj.full_name}), ID={db_obj.id}."
        )
        return db_obj

    def update(
        self,
        db: Session,
        *,
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
        data = obj_in if isinstance(obj_in, dict) else obj_in.dict(exclude_unset=True)

        if "password" in data:
            if len(data["password"]) < cfg.security.min_pw_len:
                raise HTTPException(
                    status_code=406,
                    detail="Password must have at least 8 characters.",
                )
            hashed_password = get_password_hash(data["password"])
            del data["password"]
            data["hashed_password"] = hashed_password

        user = super().update(db, db_obj=db_obj, obj_in=data)
        log.info(f"Updated user {user.username!r} ({user.full_name}), ID={user}.")
        return user

    def authenticate(
        self, db: Session, *, username: str, password: str
    ) -> Optional[model_user.User]:
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

    def is_systemuser(self, user: model_user.User) -> bool:
        """Checks if a user is a systemuser."""
        return bool(user.is_systemuser)


user = CRUDUser(model_user.User)
