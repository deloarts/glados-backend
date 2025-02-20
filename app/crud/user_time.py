"""
    Create-Read-Update-Delete: User Time
"""

from datetime import UTC
from datetime import date
from datetime import datetime
from typing import List
from typing import Optional
from typing import Tuple

from api.schemas.user_time import UserTimeCreateSchema
from api.schemas.user_time import UserTimeUpdateSchema
from crud.base import CRUDBase
from db.models import UserModel
from db.models import UserTimeModel
from exceptions import AlreadyLoggedInError
from exceptions import AlreadyLoggedOutError
from exceptions import EntryOverlapsError
from exceptions import InsufficientPermissionsError
from exceptions import LoginNotTodayError
from exceptions import LoginTimeRequiredError
from exceptions import LogoutBeforeLoginError
from exceptions import MustBeLoggedOut
from fastapi.encoders import jsonable_encoder
from multilog import log
from sqlalchemy import desc
from sqlalchemy import text
from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy.orm import Session


class CRUDUserTime(CRUDBase[UserTimeModel, UserTimeCreateSchema, UserTimeUpdateSchema]):
    """CRUDUserTime class. Descendent of the CRUDBase class."""

    def get(self, db: Session, id: int, db_obj_user: UserModel) -> Optional[UserTimeModel]:
        """Returns a user time entry by its ID for the given user.

        Args:
            db (Session): The DB session.
            id (int): The user-time entry ID.
            db_obj_user (UserModel): The user from which to lookup the time entry.

        Raises:
            InsufficientPermissionsError: Raised if the entry doesn't belong to the user.

        Returns:
            Optional[UserTimeModel]: The user time entry if found, else None.
        """
        db_obj = super().get(db, id=id)
        if db_obj and db_obj_user.id != db_obj.user_id:
            raise InsufficientPermissionsError(
                f"Blocked reading of user time entry #{db_obj.id}: "
                f"User #{db_obj_user.id} ({db_obj_user.full_name}) tried to read an entry of another user."
            )
        return db_obj

    def get_multi(
        self,
        db: Session,
        db_obj_user: UserModel,
        *,
        skip: int | None = None,
        limit: int | None = None,
        id: str | None = None,  # pylint: disable=W0622
        login_from: datetime | None = None,
        login_to: datetime | None = None,
        logout_from: datetime | None = None,
        logout_to: datetime | None = None,
    ) -> Tuple[int, List[UserTimeModel]]:
        """Returns multiple user time entries for the given user. Args after the asterisk are db-filters.

        Args:
            db (Session): The DB session.
            db_obj_user (UserModel): The user from whom to read the time entries.

        Returns:
            Tuple[int, List[UserTimeModel]]: The total number of entries found with the given filter-args and the \
                entries as list.
        """
        query = (
            db.query(self.model)
            .filter_by(
                id=id if id else self.model.id,
                user_id=db_obj_user.id,
            )
            .filter(
                self.model.login >= login_from if login_from else text(""),
                self.model.login <= login_to if login_to else text(""),
                self.model.logout >= logout_from if logout_from else text(""),
                self.model.logout <= logout_to if logout_to else text(""),
            )
        )

        items: List[UserTimeModel] = query.order_by(desc(self.model.login)).offset(skip).limit(limit).all()
        total: int = query.count()
        return total, items

    def get_logged_in(self, db: Session, db_obj_user: UserModel | None = None) -> List[Tuple[UserModel, UserTimeModel]]:
        """Returns all logged-in users and their corresponding time entry.
        Note: Logged-in means that the time entry has no logout-times set.

        Args:
            db (Session): The DB session.
            db_obj_user (UserModel | None, optional): If provided, only the logged-in user-time entry of this user is \
                returned. Defaults to None.

        Returns:
            List[Tuple[UserModel, UserTimeModel]]: A list of tuples containing the logged-in user and their time entry.
        """
        obj_out: List[Tuple[UserModel, UserTimeModel]] = []
        entries = (
            db.query(self.model)
            .filter_by(user_id=db_obj_user.id if db_obj_user else self.model.user_id, logout=None)
            .all()
        )
        for entry in entries:
            obj_out.append((entry.user, entry))
        return obj_out

    def get_last_login(self, db: Session, db_obj_user: UserModel) -> Optional[UserTimeModel]:
        """Returns the last user-time entry where the logout time is not set (the user is logged in).

        Args:
            db (Session): The DB session.
            db_obj_user (UserModel): The user from whom to get the last login time.

        Returns:
            Optional[UserTimeModel]: The last user-time entry where the user is logged in.
        """
        return (
            db.query(self.model).filter_by(user_id=db_obj_user.id, logout=None).order_by(desc(self.model.login)).first()
        )

    def get_last_logout(self, db: Session, db_obj_user: UserModel) -> Optional[UserTimeModel]:
        """Returns the last user-time entry where both login and logout times are set.
        Warning: This doesn't necessarily mean that the user is currently logged out.

        Args:
            db (Session): The DB session.
            db_obj_user (UserModel): The user from whom to get the entry.

        Returns:
            Optional[UserTimeModel]: The last user-time entry where the user is logged out.
        """
        return db.query(self.model).filter_by(user_id=db_obj_user.id).order_by(desc(self.model.logout)).first()

    def create(self, db: Session, *, db_obj_user: UserModel, obj_in: UserTimeCreateSchema) -> UserTimeModel:
        """Creates a user time entry for the given user.

        Args:
            db (Session): The DB session.
            db_obj_user (UserModel): The user for whom to create the time entry.
            obj_in (UserTimeCreateSchema): The data to create the time entry with.

        Raises:
            LoginTimeRequiredError: Raised when no login time is provided.
            MustBeLoggedOut: Raised when the user is already logged in.
            LogoutBeforeLoginError: Raised when the logout time is before the login time.
            LoginNotTodayError: Raised when the login time is not today and no logout time is provided.
            EntryOverlapsError: Raised when the new entry overlaps with an existing entry.

        Returns:
            UserTimeModel: The created user time entry.
        """
        if not obj_in.login:
            raise LoginTimeRequiredError("Cannot create user time entry: No login date provided.")

        if db.query(self.model).filter_by(user_id=db_obj_user.id, logout=None).first():
            raise MustBeLoggedOut("Cannot create user time entry: User isn't logged out.")

        if obj_in.logout and obj_in.logout < obj_in.login:
            raise LogoutBeforeLoginError("Cannot create user time entry: Login time is before logout.")

        if not obj_in.logout and obj_in.login.date() != date.today():
            raise LoginNotTodayError("Cannot create user time entry: Login must be today when no logout is provided.")

        if db.query(self.model).filter_by(user_id=db_obj_user.id).filter(
            obj_in.login > self.model.login, obj_in.login < self.model.logout
        ).all() or (
            obj_in.logout
            and db.query(self.model)
            .filter_by(user_id=db_obj_user.id)
            .filter(
                obj_in.logout < self.model.logout,
                obj_in.logout > self.model.login,
            )
            .all()
        ):
            raise EntryOverlapsError("Cannot create user time entry: Overlaps with existing entry.")

        data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)
        data["user_id"] = db_obj_user.id
        if obj_in.logout:
            data["duration_minutes"] = (
                obj_in.logout.replace(tzinfo=UTC) - obj_in.login.replace(tzinfo=UTC)
            ).total_seconds() / 60

        db_obj = UserTimeModel(**data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        log.info(f"Created user time entry (ID={db_obj.id}, USER={db_obj_user.id}).")
        return db_obj

    def update(
        self, db: Session, *, db_obj_user: UserModel, db_obj: UserTimeModel, obj_in: UserTimeUpdateSchema
    ) -> UserTimeModel:
        """Updates a user time entry for the given user.

        Args:
            db (Session): The DB session.
            db_obj_user (UserModel): The user who wants to update the time entry.
            db_obj (UserTimeModel): The time entry to update.
            obj_in (UserTimeUpdateSchema): The data to update the time entry with.

        Raises:
            InsufficientPermissionsError: Raised when the user tries to update an entry of another user.
            LoginTimeRequiredError: Raised when no login time is provided.
            LogoutBeforeLoginError: Raised when the logout time is before the login time.
            EntryOverlapsError: Raised when the new entry overlaps with an existing entry.

        Returns:
            UserTimeModel: The updated user time entry.
        """
        if db_obj_user.id != db_obj.user_id:
            raise InsufficientPermissionsError(
                f"Blocked update of user time entry #{db_obj.id}: "
                f"User #{db_obj_user.id} ({db_obj_user.full_name}) tried to update an entry of another user."
            )

        if not obj_in.login:
            raise LoginTimeRequiredError(f"Cannot update user time entry: No login date provided.")

        if obj_in.logout and obj_in.logout < obj_in.login:
            raise LogoutBeforeLoginError("Cannot update user time entry: Login time is before logout.")

        if db.query(self.model).filter_by(user_id=db_obj_user.id).filter(
            self.model.id != db_obj.id, obj_in.login > self.model.login, obj_in.login < self.model.logout
        ).all() or (
            obj_in.logout
            and db.query(self.model)
            .filter_by(user_id=db_obj_user.id)
            .filter(self.model.id != db_obj.id, obj_in.logout < self.model.logout, obj_in.logout > self.model.login)
            .all()
        ):
            raise EntryOverlapsError("Cannot create user time entry: Overlaps with existing entry.")

        if obj_in.login and obj_in.logout:
            duration_minutes = (
                obj_in.logout.replace(tzinfo=UTC) - obj_in.login.replace(tzinfo=UTC)
            ).total_seconds() / 60
        else:
            duration_minutes = None

        data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)
        data["duration_minutes"] = duration_minutes

        user_time = super().update(db, db_obj=db_obj, obj_in=data)
        log.info(
            f"Updated user time entry #{user_time.id} "
            f"by {db_obj_user.username} (Name={db_obj_user.full_name}, ID={db_obj_user.id})."
        )
        return user_time

    def update_field(
        self,
        db: Session,
        *,
        db_obj_user: UserModel,
        db_obj: UserTimeModel,
        db_field: InstrumentedAttribute,
        value: bool | int | float | str | date,
    ) -> UserTimeModel:
        """Updates a single field of a user time entry for the given user.

        Args:
            db (Session): The DB session.
            db_obj_user (UserModel): The user who wants to update the time entry.
            db_obj (UserTimeModel): The time entry to update.
            db_field (InstrumentedAttribute): The field to update.
            value (bool | int | float | str | date): The new value for the field.

        Raises:
            InsufficientPermissionsError: Raised when the user tries to update an entry of another user.

        Returns:
            UserTimeModel: The updated user time entry.
        """
        if db_obj_user.id != db_obj.user_id:
            raise InsufficientPermissionsError(
                f"Blocked update of user time entry #{db_obj.id}: "
                f"User #{db_obj_user.id} ({db_obj_user.full_name}) tried to update an entry of another user."
            )

        field_name = db_field.description
        field_value = jsonable_encoder(db_obj)[field_name]
        if value == field_value:
            return db_obj

        data = {field_name: value}
        obj = super().update(db, db_obj=db_obj, obj_in=data)

        log.info(f"User {db_obj_user.username!r} updated the field {field_name!r} of their time logger #{db_obj.id}")
        return obj

    def delete(self, db: Session, *, db_obj_user: UserModel, db_obj: UserTimeModel) -> Optional[UserTimeModel]:
        """Deletes a user time entry for the given user.

        Args:
            db (Session): The DB session.
            db_obj_user (UserModel): The user who wants to delete the time entry.
            db_obj (UserTimeModel): The time entry to delete.

        Raises:
            InsufficientPermissionsError: Raised when the user tries to delete an entry of another user.

        Returns:
            Optional[UserTimeModel]: Returns the deleted user time entry. If None, the item was not found.
        """
        if db_obj_user.id != db_obj.user_id:
            raise InsufficientPermissionsError(
                f"Blocked deletion of user time entry #{db_obj.id}: "
                f"User #{db_obj_user.id} ({db_obj_user.full_name}) tried to delete an entry of another user."
            )

        deleted_entry = super().delete(db, id=db_obj.id)
        log.info(f"User #{db_obj_user.id} ({db_obj_user.full_name}) deleted the the time entry #{db_obj.id}.")
        return deleted_entry

    def login(self, db: Session, *, db_obj_user: UserModel, timestamp: datetime | None = None) -> UserTimeModel:
        """Logs in a user.

        Args:
            db (Session): The DB session.
            db_obj_user (UserModel): The user to log in.
            timestamp (datetime | None, optional): The login-time. If None, UTC-now will be used. Defaults to None.

        Raises:
            AlreadyLoggedInError: Raised when the user is already logged in.

        Returns:
            UserTimeModel: The created user time entry.
        """
        if not timestamp:
            timestamp = datetime.now(UTC)

        if db.query(self.model).filter_by(user_id=db_obj_user.id, logout=None).count() > 0:
            raise AlreadyLoggedInError(f"User #{db_obj_user.id} tried to login, but is already logged in.")

        db_obj = UserTimeModel(**{"user_id": db_obj_user.id, "login": timestamp})
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        log.info(f"Logged in user #{db_obj_user.id} ({db_obj_user.full_name}) at {timestamp}.")
        return db_obj

    def logout(self, db: Session, *, db_obj_user: UserModel, timestamp: datetime | None = None) -> UserTimeModel:
        """Logs out a user.
        Automatically calculates the break, if the user has an automatic break set.

        Args:
            db (Session): The DB session.
            db_obj_user (UserModel): The user to log out.
            timestamp (datetime | None, optional): The logout-time. If None, UTC-now will be used. Defaults to None.

        Raises:
            AlreadyLoggedOutError: Raised when the user is already logged out.

        Returns:
            UserTimeModel: The created user time entry.
        """
        if not timestamp:
            timestamp = datetime.now(UTC)

        db_obj = db.query(self.model).filter_by(user_id=db_obj_user.id, logout=None).first()
        if not db_obj:
            raise AlreadyLoggedOutError(f"User #{db_obj_user.id} tried to logout, but is already logged out.")

        login_time = db_obj.login.replace(tzinfo=UTC)
        logout_time = timestamp.replace(tzinfo=UTC)

        if db_obj_user.auto_break_from and db_obj_user.auto_break_to:
            auto_break_from = datetime.combine(date.today(), db_obj_user.auto_break_from).replace(tzinfo=UTC)
            auto_break_to = datetime.combine(date.today(), db_obj_user.auto_break_to).replace(tzinfo=UTC)

            if login_time < auto_break_from and logout_time > auto_break_to:
                # Duration for time before auto-break (update db entry)
                duration_minutes_bb = (auto_break_from - login_time).total_seconds() / 60
                user_time_before_break = super().update(
                    db,
                    db_obj=db_obj,
                    obj_in={
                        "logout": auto_break_from,
                        "duration_minutes": duration_minutes_bb,
                    },
                )

                # Duration for time after auto-break (new db entry)
                duration_minutes_ab = (logout_time - auto_break_to).total_seconds() / 60
                user_time_after_break = UserTimeModel(
                    **{
                        "user_id": db_obj_user.id,
                        "login": auto_break_to,
                        "logout": logout_time,
                        "duration_minutes": duration_minutes_ab,
                    }
                )
                db.add(user_time_after_break)
                db.commit()
                db.refresh(user_time_after_break)
                log.info(
                    f"Logged out user #{db_obj_user.id} ({db_obj_user.full_name}) at {logout_time} with "
                    "automatic break."
                )
                return user_time_after_break

        duration_minutes = (logout_time - login_time).total_seconds() / 60
        user_time = super().update(
            db, db_obj=db_obj, obj_in={"logout": logout_time, "duration_minutes": duration_minutes}
        )
        log.info(f"Logged out user #{db_obj_user.id} ({db_obj_user.full_name}) at {logout_time}.")
        return user_time


crud_user_time = CRUDUserTime(UserTimeModel)
