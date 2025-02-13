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
from const import Themes
from crud.base import CRUDBase
from db.models import UserModel
from exceptions import EmailAlreadyExistsError
from exceptions import InsufficientPermissionsError
from exceptions import PasswordCriteriaError
from exceptions import RfidAlreadyExistsError
from exceptions import UsernameAlreadyExistsError
from locales import Locales
from mail.presets import MailPreset
from multilog import log
from security.pwd import get_hash
from security.pwd import verify_hash
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

    def get_by_rfid(self, db: Session, *, rfid: str) -> Optional[UserModel]:
        """Returns a user by their rfid id.

        Args:
            db (Session): DB session.
            rfid (str): The rfid id to lookup.

        Returns:
            Optional[UserModel]: The user as model.
        """
        users = db.query(self.model).filter(self.model.hashed_rfid != None, self.model.is_active).all()
        for user in users:
            if verify_hash(rfid, user.hashed_rfid):
                return user

    def create(self, db: Session, *, current_user: UserModel, obj_in: UserCreateSchema) -> UserModel:
        """Creates a user.

        Args:
            db (Session): DB session.
            current_user (UserModel): The current user who creates a new user.
            obj_in (UserCreateSchema): The user data as schema.

        Raises:
            UsernameAlreadyExistsError: A user with this username exists.
            EmailAlreadyExistsError: A user with this email exists.

        Returns:
            UserModel: The newly created user.
        """
        if self.get_by_username(db, username=obj_in.username):
            raise UsernameAlreadyExistsError(
                f"Blocked creation of a user: User with username {obj_in.username!r} already exists."
            )
        if self.get_by_email(db, email=obj_in.email):
            raise EmailAlreadyExistsError(
                f"Blocked creation of a user: User with email {obj_in.email!r} already exists."
            )
        if obj_in.rfid and self.get_by_rfid(db, rfid=obj_in.rfid):
            raise RfidAlreadyExistsError(
                f"Blocked creation of a user: The given RFID is already assigned to an account."
            )

        data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)
        data["created"] = datetime.now(UTC)
        data["hashed_password"] = get_hash(obj_in.password)
        del data["password"]
        if "rfid" in data:
            if data["rfid"] is not None:
                hashed_rfid = get_hash(data["rfid"])
                data["hashed_rfid"] = hashed_rfid
            del data["rfid"]

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

        try:
            MailPreset.send_welcome_mail(
                email=db_obj.email,
                full_name=db_obj.full_name,
                username=db_obj.username,
                password=obj_in.password,
            )
        except Exception as e:
            log.error(f"Error sending welcome mail to {db_obj.email!r}: {e}")

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
            UsernameAlreadyExistsError: A user with this username exists.
            EmailAlreadyExistsError: A user with this email exists.
            RfidAlreadyExistsError: A user with this rfid exists.
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
            raise UsernameAlreadyExistsError(
                f"Blocked update of a user #{db_obj.id} ({db_obj.username}): "
                f"User #{current_user.id} ({current_user.full_name}) tried to update this users username to "
                f"{data['username']}, but another user with this username already exists."
            )

        if (
            "email" in data
            and (existing_user := self.get_by_email(db, email=data["email"]))
            and existing_user.id != db_obj.id
        ):
            raise EmailAlreadyExistsError(
                f"Blocked update of a user #{db_obj.id} ({db_obj.username}): "
                f"User #{current_user.id} ({current_user.full_name}) tried to update this users mail to "
                f"{data['email']}, but another user with this mail already exists."
            )

        # Handle a new password
        if "password" in data:
            if len(data["password"]) < cfg.security.min_pw_len:
                raise PasswordCriteriaError(
                    f"Blocked update of a user #{db_obj.id} ({db_obj.full_name}): "
                    f"User #{current_user.id} ({current_user.full_name}) tried to set a weak password"
                )
            hashed_password = get_hash(data["password"])
            del data["password"]
            data["hashed_password"] = hashed_password

        # Handle a new rfid id
        if "rfid" in data:
            if data["rfid"] is not None:
                user_from_rfid = self.get_by_rfid(db, rfid=data["rfid"])
                if user_from_rfid and user_from_rfid.id != db_obj.id:
                    raise RfidAlreadyExistsError(
                        f"Blocked update of a user #{db_obj.id} ({db_obj.username}): "
                        f"User #{current_user.id} ({current_user.full_name}) tried to update, but the given RFID is "
                        "already assigned to an account."
                    )
                hashed_rfid = get_hash(data["rfid"])
                data["hashed_rfid"] = hashed_rfid
            del data["rfid"]

        # Handle missing data
        if "language" not in data or data["language"] is None or data["language"] not in Locales._value2member_map_:
            data["language"] = Locales.EN_GB.value
        if "theme" not in data or data["theme"] is None or data["theme"] not in Themes._value2member_map_:
            data["theme"] = "dark"

        # Handling permissions
        # Only system- and admin-users can edit permissions (ignore given permissions)
        if not current_user.is_adminuser and not current_user.is_systemuser:
            data["is_active"] = db_obj.is_active
            data["is_superuser"] = db_obj.is_superuser
            data["is_adminuser"] = db_obj.is_adminuser
            data["is_guestuser"] = db_obj.is_guestuser

        # The systemuser can only update itself and has fixed permissions that cannot be altered
        # FIXME: Currently it's possible to create another system user. This should be forbidden in the future.
        elif db_obj.is_systemuser:
            if db_obj.id != current_user.id:
                raise InsufficientPermissionsError(
                    f"Blocked update of a user #{db_obj.id} ({db_obj.full_name}): "
                    f"User #{current_user.id} ({current_user.full_name}) tried to update the system user"
                )
            data["is_active"] = True
            data["is_superuser"] = True
            data["is_adminuser"] = True
            data["is_guestuser"] = False

        # And a user cannot change their own permission
        elif db_obj.id == current_user.id:
            data["is_active"] = db_obj.is_active
            data["is_superuser"] = db_obj.is_superuser
            data["is_adminuser"] = db_obj.is_adminuser
            data["is_guestuser"] = db_obj.is_guestuser

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
        if not verify_hash(password, str(user.hashed_password)):
            return None
        return user

    def authenticate_rfid(self, db: Session, *, rfid: str) -> Optional[UserModel]:
        """Authenticates a user by the rfid id"""
        user = self.get_by_rfid(db, rfid=rfid)
        if not user:
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
