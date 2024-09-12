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
from exceptions import InsufficientPermissionsError
from exceptions import PasswordCriteriaError
from exceptions import UserAlreadyExistsError
from multilog import log
from security.pwd import get_password_hash
from security.pwd import verify_password
from sqlalchemy.orm import Session


class CRUDUser(CRUDBase[UserModel, UserCreateSchema, UserUpdateSchema]):
    """CRUDUser class. Descendent of the CRUDBase class."""

    def get_by_id(self, db: Session, *, id: int) -> Optional[UserModel]:
        """Returns a user by their ID.

        Args:
            db (Session): DB session.
            id (int): The ID to lookup.

        Returns:
            Optional[UserModel]: The user as model.
        """
        return db.query(self.model).filter(self.model.id == id).first()

    def get_by_username(self, db: Session, *, username: str) -> Optional[UserModel]:
        """Returns a user by their username.

        Args:
            db (Session): DB session.
            username (str): The username to lookup.

        Returns:
            Optional[UserModel]: The user as model.
        """
        return db.query(self.model).filter(self.model.username == username).first()

    def get_by_email(self, db: Session, *, email: str) -> Optional[UserModel]:
        """Returns a user by their email.

        Args:
            db (Session): DB session.
            email (str): The mail address to lookup.

        Returns:
            Optional[UserModel]: The user as model.
        """
        return db.query(self.model).filter(self.model.email == email).first()

    def create(self, db: Session, *, current_user: UserModel, obj_in: UserCreateSchema) -> UserModel:
        """Creates a user.

        Args:
            db (Session): DB session.
            current_user (UserModel): The current user who creates a new user.
            obj_in (UserCreateSchema): The user data as schema.

        Returns:
            UserModel: The newly created user.
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
        """Update a user.

        Args:
            db (Session): DB session.
            current_user (UserModel): The user who updates another user.
            db_obj (UserModel): The current to-be-updated user as model.
            obj_in (UserUpdateSchema | Dict[str, Any]): The new data.

        Raises:
            UserAlreadyExistsError: A user with this username exists.
            UserAlreadyExistsError: A user with this email exists.
            PasswordCriteriaError: Password too weak.
            InsufficientPermissionsError: System user cannot be updated by another user.

        Returns:
            UserModel: _description_
        """
        data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)

        if (
            "username" in data
            and (existing_user := self.get_by_username(db, username=data["username"]))
            and existing_user.id != db_obj.id
        ):
            raise UserAlreadyExistsError(
                f"Blocked update of a user #{db_obj.id} ({db_obj.username}): "
                f"User #{current_user.id} ({current_user.full_name}) tried to update, but a user with this username "
                "already exists."
            )

        if (
            "email" in data
            and (existing_user := self.get_by_email(db, email=data["email"]))
            and existing_user.id != db_obj.id
        ):
            raise UserAlreadyExistsError(
                f"Blocked update of a user #{db_obj.id} ({db_obj.username}): "
                f"User #{current_user.id} ({current_user.full_name}) tried to update, but a user with this mail "
                "already exists."
            )

        # Handle a new password
        if "password" in data:
            if len(data["password"]) < cfg.security.min_pw_len:
                raise PasswordCriteriaError(
                    f"Blocked update of a user #{db_obj.id} ({db_obj.full_name}): "
                    f"User #{current_user.id} ({current_user.full_name}) tried to set a weak password"
                )
            hashed_password = get_password_hash(data["password"])
            del data["password"]
            data["hashed_password"] = hashed_password

        # The systemuser can only update itself!
        # The systemuser has fixed permissions that cannot be altered.
        if db_obj.is_systemuser:
            if db_obj.id != current_user.id:
                raise InsufficientPermissionsError(
                    f"Blocked update of a user #{db_obj.id} ({db_obj.full_name}): "
                    f"User #{current_user.id} ({current_user.full_name}) tried to update the system user"
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
