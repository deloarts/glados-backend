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

    def get_logged_in(self, db: Session) -> List[Tuple[UserModel, UserTimeModel]]:
        obj_out: List[Tuple[UserModel, UserTimeModel]] = []
        entries = db.query(self.model).filter_by(logout=None).all()
        for entry in entries:
            obj_out.append((entry.user, entry))
        return obj_out

    def create(self, db: Session, *, db_obj_user: UserModel, obj_in: UserTimeCreateSchema) -> UserTimeModel:
        if not obj_in.login:
            raise LoginTimeRequiredError("Cannot create user time entry: No login date provided.")

        if db.query(self.model).filter_by(user_id=db_obj_user.id, logout=None).first():
            raise MustBeLoggedOut("Cannot create user time entry: User isn't logged out.")

        if obj_in.logout and obj_in.logout < obj_in.login:
            raise LogoutBeforeLoginError("Cannot create user time entry: Login time is before logout.")

        if (
            db.query(self.model)
            .filter_by(user_id=db_obj_user.id)
            .filter(obj_in.login > self.model.login, obj_in.login < self.model.logout)
            .all()
            or db.query(self.model)
            .filter_by(user_id=db_obj_user.id)
            .filter(obj_in.logout < self.model.logout, obj_in.logout > self.model.login)
            .all()
        ):
            raise EntryOverlapsError("Cannot create user time entry: Overlaps with existing entry.")

        # if obj_in.logout and obj_in.logout.date() != obj_in.login.date():
        #     raise NotSameDayError("Cannot create user time entry: Logout date differs from login date.")

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
        if db_obj_user.id != db_obj.user_id:
            raise InsufficientPermissionsError(
                f"Blocked update of user time entry #{db_obj.id}: "
                f"User #{db_obj_user.id} ({db_obj_user.full_name}) tried to update an entry of another user."
            )

        if not obj_in.login:
            raise LoginTimeRequiredError(f"Cannot update user time entry: No login date provided.")

        if obj_in.logout and obj_in.logout < obj_in.login:
            raise LogoutBeforeLoginError("Cannot update user time entry: Login time is before logout.")

        if (
            db.query(self.model)
            .filter_by(user_id=db_obj_user.id)
            .filter(obj_in.login > self.model.login, obj_in.login < self.model.logout)
            .all()
            or db.query(self.model)
            .filter_by(user_id=db_obj_user.id)
            .filter(obj_in.logout < self.model.logout, obj_in.logout > self.model.login)
            .all()
        ):
            raise EntryOverlapsError("Cannot create user time entry: Overlaps with existing entry.")

        # if obj_in.logout and obj_in.logout.date() != obj_in.login.date():
        #     raise NotSameDayError("Cannot update user time entry: Logout date differs from login date.")

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
        if db_obj_user.id != db_obj.user_id:
            raise InsufficientPermissionsError(
                f"Blocked deletion of user time entry #{db_obj.id}: "
                f"User #{db_obj_user.id} ({db_obj_user.full_name}) tried to delete an entry of another user."
            )

        deleted_entry = super().delete(db, id=db_obj.id)
        log.info(f"User #{db_obj_user.id} ({db_obj_user.full_name}) deleted the the time entry #{db_obj.id}.")
        return deleted_entry

    def login(self, db: Session, *, db_obj_user: UserModel, timestamp: datetime | None = None) -> UserTimeModel:
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
                user_time_bb = super().update(
                    db,
                    db_obj=db_obj,
                    obj_in={
                        "logout": auto_break_from,
                        "duration_minutes": duration_minutes_bb,
                    },
                )

                # Duration for time after auto-break (new db entry)
                duration_minutes_ab = (logout_time - auto_break_to).total_seconds() / 60
                user_time_ab = UserTimeModel(
                    **{
                        "user_id": db_obj_user.id,
                        "login": auto_break_to,
                        "logout": logout_time,
                        "duration_minutes": duration_minutes_ab,
                    }
                )
                db.add(user_time_ab)
                db.commit()
                db.refresh(user_time_ab)
                log.info(
                    f"Logged out user #{db_obj_user.id} ({db_obj_user.full_name}) at {logout_time} with "
                    "automatic break."
                )
                return user_time_ab

        duration_minutes = (logout_time - login_time).total_seconds() / 60
        user_time = super().update(
            db, db_obj=db_obj, obj_in={"logout": logout_time, "duration_minutes": duration_minutes}
        )
        log.info(f"Logged out user #{db_obj_user.id} ({db_obj_user.full_name}) at {logout_time}.")
        return user_time


crud_user_time = CRUDUserTime(UserTimeModel)
