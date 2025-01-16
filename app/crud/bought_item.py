"""
    Create-Read-Update-Delete: Bought Item
"""

# pylint: disable=R0914

from datetime import date
from typing import List
from typing import Optional
from typing import Tuple

from api.schemas.bought_item import BoughtItemCreatePatSchema
from api.schemas.bought_item import BoughtItemCreateWebSchema
from api.schemas.bought_item import BoughtItemUpdateWebSchema
from api.schemas.email_notification import EmailNotificationCreateSchema
from config import cfg
from crud.base import CRUDBase
from crud.email_notification import crud_email_notification
from crud.project import crud_project
from db.models import BoughtItemModel
from db.models import ProjectModel
from db.models import UserModel
from exceptions import BoughtItemAlreadyPlannedError
from exceptions import BoughtItemCannotChangeToOpenError
from exceptions import BoughtItemOfAnotherUserError
from exceptions import BoughtItemRequiredFieldNotSetError
from exceptions import BoughtItemUnknownStatusError
from exceptions import InsufficientPermissionsError
from exceptions import ProjectInactiveError
from exceptions import ProjectNotFoundError
from fastapi.encoders import jsonable_encoder
from multilog import log
from sqlalchemy import asc
from sqlalchemy import desc
from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from sqlalchemy.sql.elements import TextClause
from utilities.helper import get_changelog


class CRUDBoughtItem(
    CRUDBase[
        BoughtItemModel,
        BoughtItemCreateWebSchema | BoughtItemCreatePatSchema,
        BoughtItemUpdateWebSchema,
    ]
):
    """CRUDBoughtItem class. Descendent of the CRUDBase class."""

    def get_multi(
        self,
        db: Session,
        *,
        skip: int | None = None,
        limit: int | None = None,
        sort_by: str | None = None,
        id: str | None = None,  # pylint: disable=W0622
        status: str | None = None,
        project_number: str | None = None,
        project_customer: str | None = None,
        project_description: str | None = None,
        product_number: str | None = None,
        quantity: float | None = None,
        unit: str | None = None,
        partnumber: str | None = None,
        order_number: str | None = None,
        manufacturer: str | None = None,
        supplier: str | None = None,
        group_1: str | None = None,
        note_general: str | None = None,
        note_supplier: str | None = None,
        creator_id: int | None = None,
        created_from: date | None = None,
        created_to: date | None = None,
        changed_from: date | None = None,
        changed_to: date | None = None,
        desired_from: date | None = None,
        desired_to: date | None = None,
        requester_id: int | None = None,
        requested_from: date | None = None,
        requested_to: date | None = None,
        orderer_id: int | None = None,
        ordered_from: date | None = None,
        ordered_to: date | None = None,
        expected_from: date | None = None,
        expected_to: date | None = None,
        delivered_from: date | None = None,
        delivered_to: date | None = None,
        receiver_id: int | None = None,
        storage_place: str | None = None,
        high_priority: bool | None = None,
        ignore_delivered: bool | None = None,
        ignore_canceled: bool | None = None,
        ignore_lost: bool | None = None,
    ) -> Tuple[int, List[BoughtItemModel]]:
        """Returns a list of bought items by the given filter params."""

        def build_order_by(keyword: str | None) -> TextClause:
            """
            Inner function to create the order_by clause.
            # TODO: Refactor this.
            """
            if keyword is None:
                return text(str(desc(self.model.id)))
            output_list = []
            values = keyword.split(",")
            for value in values:
                if value == cfg.items.bought.order_by.high_priority:
                    output_list.append(desc(self.model.high_priority))
                elif value == cfg.items.bought.order_by.created:
                    output_list.append(asc(self.model.created))
                elif value == cfg.items.bought.order_by.project:
                    # Ordering by association proxy is not possible.
                    # Therefor it is required to specify the foreign table column name.
                    # This required the join statement when building the query.
                    output_list.append(asc(ProjectModel.number))
                elif value == cfg.items.bought.order_by.product:
                    output_list.append(asc(ProjectModel.product_number))
                elif value == cfg.items.bought.order_by.group_1:
                    output_list.append(asc(self.model.group_1))
                elif value == cfg.items.bought.order_by.manufacturer:
                    output_list.append(asc(self.model.manufacturer))
                elif value == cfg.items.bought.order_by.supplier:
                    output_list.append(asc(self.model.supplier))
            output_list.append(desc(self.model.id))
            return text(",".join(str(i) for i in output_list))

        if created_from is None:
            created_from = date(2000, 1, 1)
        if created_to is None:
            created_to = date.today()

        if changed_from is None:
            changed_from = date(2000, 1, 1)
        if changed_to is None:
            changed_to = date.today()

        # order_by = text(sort_by or str(desc(self.model.id)))
        order_by = build_order_by(sort_by)

        query = (
            db.query(self.model)
            .filter_by(
                deleted=False,
                status=status if status else self.model.status,
                high_priority=high_priority if high_priority else self.model.high_priority,
                id=id if id else self.model.id,
                quantity=quantity if quantity else self.model.quantity,
                unit=unit if unit else self.model.unit,
                creator_id=creator_id if creator_id else self.model.creator_id,
            )
            .filter(
                # ignore filter
                self.model.status != cfg.items.bought.status.delivered if ignore_delivered else text(""),
                self.model.status != cfg.items.bought.status.canceled if ignore_canceled else text(""),
                self.model.status != cfg.items.bought.status.lost if ignore_lost else text(""),
                # search filter
                self.model.project_number.ilike(f"%{project_number}%") if project_number else text(""),
                self.model.project_customer.ilike(f"%{project_customer}%") if project_customer else text(""),
                self.model.project_description.ilike(f"%{project_description}%") if project_description else text(""),
                self.model.product_number.ilike(f"%{product_number}%") if product_number else text(""),
                self.model.partnumber.ilike(f"%{partnumber}%") if partnumber else text(""),
                self.model.order_number.ilike(f"%{order_number}%") if order_number else text(""),
                self.model.manufacturer.ilike(f"%{manufacturer}%") if manufacturer else text(""),
                self.model.supplier.ilike(f"%{supplier}%") if supplier else text(""),
                self.model.group_1.ilike(f"%{group_1}%") if group_1 else text(""),
                self.model.note_general.ilike(f"%{note_general}%") if note_general else text(""),
                self.model.note_supplier.ilike(f"%{note_supplier}%") if note_supplier else text(""),
                self.model.created >= created_from,
                self.model.created <= created_to,
                self.model.changed >= changed_from,
                self.model.changed <= changed_to,
                self.model.desired_delivery_date >= desired_from if desired_from else text(""),
                self.model.desired_delivery_date <= desired_to if desired_to else text(""),
                self.model.requester_id == requester_id if requester_id else text(""),
                self.model.requested_date >= requested_from if requested_from else text(""),
                self.model.requested_date <= requested_to if requested_to else text(""),
                self.model.orderer_id == orderer_id if orderer_id else text(""),
                self.model.ordered_date >= ordered_from if ordered_from else text(""),
                self.model.ordered_date <= ordered_to if ordered_to else text(""),
                self.model.expected_delivery_date >= expected_from if expected_from else text(""),
                self.model.expected_delivery_date <= expected_to if expected_to else text(""),
                self.model.delivery_date >= delivered_from if delivered_from else text(""),
                self.model.delivery_date <= delivered_to if delivered_to else text(""),
                self.model.receiver_id == receiver_id if receiver_id else text(""),
                self.model.storage_place.ilike(f"%{storage_place}%") if storage_place else text(""),
            )
            .join(ProjectModel, self.model.project)
        )

        items: List[BoughtItemModel] = query.order_by(order_by).offset(skip).limit(limit).all()
        # log.debug(f"Items: {[i.__dict__ for i in items]}")
        total: int = query.count()
        return total, items

    def create(
        self,
        db: Session,
        *,
        db_obj_user: UserModel,
        obj_in: BoughtItemCreateWebSchema | BoughtItemCreatePatSchema,
    ) -> BoughtItemModel:
        """Create a new bought item.

        Args:
            db (Session): DB session.
            db_obj_user (UserModel): The user who creates the item as db model.
            obj_in (BoughtItemCreateWebSchema): The item data as api schema.

        Raises:
            InsufficientPermissionsError: User doesn't have required permissions.
            ProjectNotFoundError: The project given by ob_in doesn't exists.
            ProjectInactiveError: The project given by ob_in is inactive.

        Returns:
            BoughtItemModel: The new bought item as db model.
        """
        if db_obj_user.is_guestuser:
            raise InsufficientPermissionsError(
                f"Blocked creation of an item by user #{db_obj_user.id} ({db_obj_user.full_name}): "
                "A guest user is not allowed to create bought items."
            )

        project = None
        if isinstance(obj_in, BoughtItemCreateWebSchema):
            project = crud_project.get_by_id(db, id=obj_in.project_id)
        elif isinstance(obj_in, BoughtItemCreatePatSchema):
            project = crud_project.get_by_number(db, number=obj_in.project)
        else:
            raise ValueError(f"The given data doesn't contain any information about the associated project.")

        if not project:
            raise ProjectNotFoundError(
                f"Blocked creation of an item by user #{db_obj_user.id} ({db_obj_user.full_name}): "
                f"The given project doesn't exists."
            )
        if not project.is_active:
            raise ProjectInactiveError(
                f"Blocked creation of an item by user #{db_obj_user.id} ({db_obj_user.full_name}): "
                f"The given project (ID={project.id}) is inactive."
            )

        data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=False)

        # Handle project from different clients
        # The web client knows the project ID and sends it via the required db field `project_id`.
        # But the pat client only knows the project number and sends it via the field `project`.
        # Thus it's mandatory to resolve this name issue, because the key name `project` is an object
        # in the db model.
        if "project" in data:  # This is only present in the BoughtItemCreatePatSchema.
            data.pop("project")
        data["project_id"] = project.id

        # Manipulate data
        data["created"] = date.today()
        data["changed"] = date.today()
        data["creator_id"] = db_obj_user.id
        data["changes"] = get_changelog(changes="Item created.", db_obj_user=db_obj_user)

        db_obj = BoughtItemModel(**data)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        log.info(f"User {db_obj_user.username!r} created new 'bought item' " f"({db_obj.partnumber}), ID={db_obj.id}.")
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj_user: UserModel,
        db_obj_item: BoughtItemModel,
        obj_in: BoughtItemUpdateWebSchema,
    ) -> BoughtItemModel:
        """Update a bought item.

        Args:
            db (Session): DB session.
            db_obj_user (UserModel): The user who updates the item.
            db_obj_item (BoughtItemModel): The current item as model.
            obj_in (BoughtItemUpdateSchema): The new data as schema.

        Raises:
            ProjectNotFoundError: The project of the given new data doesn't exists.
            ProjectInactiveError: The project of the given new data isn't active.
            InsufficientPermissionsError: The user is not allowed to make changed.
            BoughtItemAlreadyPlannedError: The item's state is not open.
            BoughtItemOfAnotherUserError: The item belongs to another user.

        Returns:
            BoughtItemModel: The updated item as model.
        """
        project = crud_project.get_by_id(db, id=obj_in.project_id)
        if not project:
            raise ProjectNotFoundError(
                f"Blocked update of a bought item #{db_obj_item.id} ({db_obj_item.partnumber}): "
                f"User #{db_obj_user.id} ({db_obj_user.full_name}) tried to update, but no project with the number "
                f"#{obj_in.project_id} exists."
            )
        if db_obj_item.project_id != obj_in.project_id and not project.is_active:
            raise ProjectInactiveError(
                f"Blocked update of a bought item #{db_obj_item.id} ({db_obj_item.partnumber}): "
                f"User #{db_obj_user.id} ({db_obj_user.full_name}) tried to move the item to project "
                f"#{db_obj_item.project_id}, but this project is inactive."
            )
        if not db_obj_item.project.is_active:
            raise ProjectInactiveError(
                f"Blocked update of a bought item #{db_obj_item.id} ({db_obj_item.partnumber}): "
                f"User #{db_obj_user.id} ({db_obj_user.full_name}) tried to update the item of project "
                f"#{db_obj_item.project_id}, but this project is inactive."
            )

        data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)

        # Rules
        if db_obj_user.is_guestuser:
            raise InsufficientPermissionsError(
                f"Blocked update of a bought item #{db_obj_item.id} ({db_obj_item.partnumber}): "
                f"User #{db_obj_user.id} ({db_obj_user.full_name}) tried to update, but has not enough permissions "
                "(guest user)."
            )

        if (
            not (db_obj_user.is_superuser or db_obj_user.is_adminuser)
            and db_obj_item.status != cfg.items.bought.status.open
        ):
            raise BoughtItemAlreadyPlannedError(
                f"Blocked update of a bought item #{db_obj_item.id} ({db_obj_item.partnumber}): "
                f"User #{db_obj_user.id} ({db_obj_user.full_name}) tried to update, but has not enough permissions "
                "to change planned items (not a superuser or admin user)."
            )

        if not (db_obj_user.is_superuser or db_obj_user.is_adminuser) and not db_obj_item.creator_id == db_obj_user.id:
            raise BoughtItemOfAnotherUserError(
                f"Blocked update of a bought item #{db_obj_item.id} ({db_obj_item.partnumber}): "
                f"User #{db_obj_user.id} ({db_obj_user.full_name}) tried to update, but has not enough permissions "
                "to change another users items (not a superuser or admin user)."
            )

        # Manipulate data
        data["changed"] = date.today()

        # Calculate difference between data (for the changelog)
        changes: List[str] = []
        for key, value in db_obj_item.__dict__.items():
            if key in data and data[key] != value and key != "changed":
                changes.append(f"  • {key}: {value!r} → {data[key]!r}")
        changelog = "\n".join(changes)
        data["changes"] = get_changelog(
            changes=f"Item updated:\n{changelog}", db_obj_user=db_obj_user, db_obj_item=db_obj_item
        )

        item = super().update(db, db_obj=db_obj_item, obj_in=data)

        log.info(f"User {db_obj_user.username!r} updated a bought item " f"({item.partnumber}), ID={item.id}.")
        return item

    def update_status(
        self, db: Session, *, db_obj_user: UserModel, db_obj_item: BoughtItemModel, status: str
    ) -> BoughtItemModel:
        """Update the status of a bought item. Status can only be changed via this method.

        Args:
            db (Session): DB session.
            db_obj_user (UserModel): The user who changes the status.
            db_obj_item (BoughtItemModel): The current item from which to change the status.
            status (str): The status value.

        Raises:
            InsufficientPermissionsError: User is not allowed to change the status.
            BoughtItemCannotChangeToOpenError: The status cannot be set back to open.
            BoughtItemAlreadyPlannedError: The item is already planned and the user is not allowed to change.
            BoughtItemOfAnotherUserError: The item belongs to another user and the user is not allowed to change.
            BoughtItemUnknownStatusError: The given status value is unknown.

        Returns:
            BoughtItemModel: The update bought item as model.
        """
        if status == db_obj_item.status:
            log.debug(f"No changes in item #{db_obj_item.id}.")
            return db_obj_item

        # Rules
        if db_obj_user.is_guestuser:
            raise InsufficientPermissionsError(
                f"Blocked update of a bought item #{db_obj_item.id} ({db_obj_item.partnumber}): "
                f"User #{db_obj_user.id} ({db_obj_user.full_name}) tried to set the status, but has not enough "
                "permissions (guest user)."
            )

        if status == cfg.items.bought.status.open and db_obj_item.status != cfg.items.bought.status.open:
            raise BoughtItemCannotChangeToOpenError(
                f"Blocked update of a bought item #{db_obj_item.id} ({db_obj_item.partnumber}): "
                f"User #{db_obj_user.id} ({db_obj_user.full_name}) tried to set the status to open, but the item is "
                "already planned (cannot change status back to open)."
            )

        if (
            not (db_obj_user.is_superuser or db_obj_user.is_adminuser)
            and db_obj_item.status != cfg.items.bought.status.open
        ):
            raise BoughtItemAlreadyPlannedError(
                f"Blocked update of a bought item #{db_obj_item.id} ({db_obj_item.partnumber}): "
                f"User #{db_obj_user.id} ({db_obj_user.full_name}) tried to set the status, but has not enough "
                "permissions to change planned items (not a superuser or admin user)."
            )

        if not (db_obj_user.is_superuser or db_obj_user.is_adminuser) and not db_obj_item.creator_id == db_obj_user.id:
            raise BoughtItemOfAnotherUserError(
                f"Blocked update of a bought item #{db_obj_item.id} ({db_obj_item.partnumber}): "
                f"User #{db_obj_user.id} ({db_obj_user.full_name}) tried to set the status, but has not enough "
                "permissions to change another users items (not a superuser or admin user)."
            )

        # Incoming data rules
        if status not in cfg.items.bought.status.values:
            raise BoughtItemUnknownStatusError(
                f"Blocked update of a bought item #{db_obj_item.id} ({db_obj_item.partnumber}): "
                f"User #{db_obj_user.id} ({db_obj_user.full_name}) tried to set the status, but the given value "
                f"({status}) is unknown."
            )

        # Manipulate data
        data = {"status": status}
        if status == cfg.items.bought.status.requested:
            data["requested_date"] = date.today()  # type:ignore
            data["requester_id"] = int(db_obj_user.id)  # type:ignore
        if status == cfg.items.bought.status.ordered:
            data["ordered_date"] = date.today()  # type:ignore
            data["orderer_id"] = int(db_obj_user.id)  # type:ignore
        if status == cfg.items.bought.status.delivered:
            data["delivery_date"] = date.today()  # type:ignore
            data["receiver_id"] = int(db_obj_user.id)  # type:ignore
        data["changed"] = date.today()  # type:ignore
        data["changes"] = get_changelog(  # type:ignore
            changes=f"Update status: {db_obj_item.status} -> {status}",
            db_obj_user=db_obj_user,
            db_obj_item=db_obj_item,
        )

        # Important: Update the item before creating a new email notification!
        # Reason: The db session is the same for every query, and the changes
        # will get lost if the data is updated after the notification is created.
        return_obj = super().update(db, db_obj=db_obj_item, obj_in=data)

        # Add notification
        if status == cfg.items.bought.status.late:
            notification = EmailNotificationCreateSchema(
                reason="late",
                receiver_id=db_obj_item.creator_id,
                bought_item_id=db_obj_item.id,
            )
            crud_email_notification.create(db=db, obj_in=notification)

        if db_obj_item.notify_on_delivery and status == cfg.items.bought.status.delivered:
            notification = EmailNotificationCreateSchema(
                reason="delivered",
                receiver_id=db_obj_item.creator_id,
                bought_item_id=db_obj_item.id,
            )
            crud_email_notification.create(db=db, obj_in=notification)

        item = return_obj
        log.info(
            f"User {db_obj_user.username!r} updated the status of a bought item "
            f"({item.partnumber}), status={item.status}, ID={item.id}."
        )
        return item

    def update_project(
        self, db: Session, *, db_obj_user: UserModel, db_obj_item: BoughtItemModel, project_number: str
    ) -> BoughtItemModel:
        """Update the project of a bought item.

        Args:
            db (Session): DB session.
            db_obj_user (UserModel): The user who changes the status.
            db_obj_item (BoughtItemModel): The current bought item.
            project_number (str): The new project number to which to move the item to.

        Raises:
            ProjectNotFoundError: The given project number doesn't exist.
            ProjectInactiveError: The project from the given number isn't active.
            InsufficientPermissionsError: User is not allowed to change the project.
            BoughtItemAlreadyPlannedError: The item is already planned and the user is not allowed to change.
            BoughtItemOfAnotherUserError: The item belongs to another user and the user is not allowed to change.

        Returns:
            BoughtItemModel: The updated bought item as model.
        """
        project = crud_project.get_by_number(db, number=project_number)
        if not project:
            raise ProjectNotFoundError(
                f"Blocked update of a bought item #{db_obj_item.id} ({db_obj_item.partnumber}): "
                f"User #{db_obj_user.id} ({db_obj_user.full_name}) tried to move the item to project "
                f"number #{db_obj_item.project_id}, but this project doesn't exists."
            )
        if db_obj_item.project_id != db_obj_item.project_id and not project.is_active:
            raise ProjectInactiveError(
                f"Blocked update of a bought item #{db_obj_item.id} ({db_obj_item.partnumber}): "
                f"User #{db_obj_user.id} ({db_obj_user.full_name}) tried to move the item to project "
                f"#{db_obj_item.project_id}, but this project is inactive."
            )

        # Rules
        if db_obj_user.is_guestuser:
            raise InsufficientPermissionsError(
                f"Blocked update of a bought item #{db_obj_item.id} ({db_obj_item.partnumber}): "
                f"User #{db_obj_user.id} ({db_obj_user.full_name}) tried to set the project, but has not enough "
                "permissions (guest user)."
            )

        if (
            not (db_obj_user.is_superuser or db_obj_user.is_adminuser)
            and db_obj_item.status != cfg.items.bought.status.open
        ):
            raise BoughtItemAlreadyPlannedError(
                f"Blocked update of a bought item #{db_obj_item.id} ({db_obj_item.partnumber}): "
                f"User #{db_obj_user.id} ({db_obj_user.full_name}) tried to set the project, but has not enough "
                "permissions to change planned items (not a superuser or admin user)."
            )

        if not (db_obj_user.is_superuser or db_obj_user.is_adminuser) and not db_obj_item.creator_id == db_obj_user.id:
            raise BoughtItemOfAnotherUserError(
                f"Blocked update of a bought item #{db_obj_item.id} ({db_obj_item.partnumber}): "
                f"User #{db_obj_user.id} ({db_obj_user.full_name}) tried to set the project, but has not enough "
                "permissions to change another users items (not a superuser or admin user)."
            )

        # Manipulate data
        data = {"project_id": project.id}
        data["changed"] = date.today()  # type:ignore
        data["changes"] = get_changelog(  # type:ignore
            changes=(f"Update project: {db_obj_item.project_number} -> {project.number}"),
            db_obj_user=db_obj_user,
            db_obj_item=db_obj_item,
        )

        return_obj = super().update(db, db_obj=db_obj_item, obj_in=data)
        log.info(
            f"User {db_obj_user.username!r} updated the project of a bought item "
            f"({return_obj.partnumber}), {db_obj_item.project_number} -> {project.number}, ID={return_obj.id}."
        )
        return return_obj

    def update_field(
        self,
        db: Session,
        *,
        db_obj_user: UserModel,
        db_obj_item: BoughtItemModel,
        db_field: InstrumentedAttribute,
        value: bool | int | float | str | date,
    ) -> BoughtItemModel:
        """Update a field's value in the table of the bought item.

        Args:
            db (Session): DB session.
            db_obj_user (UserModel): The user who update the value.
            db_obj_item (BoughtItemModel): The current bought item as model.
            db_field (InstrumentedAttribute): The field which to update.
            value (bool | int | float | str | date): The value which to assign to the field.

        Raises:
            InsufficientPermissionsError: User is not allowed to change the field.
            BoughtItemAlreadyPlannedError: The item is already planned and the user is not allowed to change.
            BoughtItemOfAnotherUserError: The item belongs to another user and the user is not allowed to change.
            ProjectInactiveError: The project of this item is inactive.

        Returns:
            BoughtItemModel: The updated bought item as model.
        """
        field_name = db_field.description
        field_value = jsonable_encoder(db_obj_item)[field_name]

        # Rules
        if db_obj_user.is_guestuser:
            raise InsufficientPermissionsError(
                f"Blocked update of a bought item #{db_obj_item.id} ({db_obj_item.partnumber}): "
                f"User #{db_obj_user.id} ({db_obj_user.full_name}) tried to set the {field_name}, but has not enough "
                "permissions (guest user)."
            )

        if (
            not (db_obj_user.is_superuser or db_obj_user.is_adminuser)
            and db_obj_item.status != cfg.items.bought.status.open
        ):
            raise BoughtItemAlreadyPlannedError(
                f"Blocked update of a bought item #{db_obj_item.id} ({db_obj_item.partnumber}): "
                f"User #{db_obj_user.id} ({db_obj_user.full_name}) tried to set the {field_name}, but has not enough "
                "permissions to change planned items (not a superuser or admin user)."
            )

        if not (db_obj_user.is_superuser or db_obj_user.is_adminuser) and not db_obj_item.creator_id == db_obj_user.id:
            raise BoughtItemOfAnotherUserError(
                f"Blocked update of a bought item #{db_obj_item.id} ({db_obj_item.partnumber}): "
                f"User #{db_obj_user.id} ({db_obj_user.full_name}) tried to set the {field_name}, but has not enough "
                "permissions to change another users items (not a superuser or admin user)."
            )

        if not db_obj_item.project.is_active:
            raise ProjectInactiveError(
                f"Blocked update of a bought item #{db_obj_item.id} ({db_obj_item.partnumber}): "
                f"User #{db_obj_user.id} ({db_obj_user.full_name}) tried to update the item of project "
                f"#{db_obj_item.project_id}, but this project is inactive."
            )

        if value == field_value:
            return db_obj_item

        # Manipulate data
        data = {field_name: value}
        data["changed"] = date.today()  # type:ignore
        data["changes"] = get_changelog(  # type:ignore
            changes=(f"Update {field_name}: {field_value} -> {value}"),
            db_obj_user=db_obj_user,
            db_obj_item=db_obj_item,
        )
        item = super().update(db, db_obj=db_obj_item, obj_in=data)

        log.info(
            f"User {db_obj_user.username!r} updated the field {field_name!r} of a "
            f"bought item ({item.partnumber}), value={value}, ID={item.id}."
        )
        return item

    def update_required_field(
        self,
        db: Session,
        *,
        db_obj_user: UserModel,
        db_obj_item: BoughtItemModel,
        db_field: InstrumentedAttribute,
        value: bool | int | float | str | date,
    ) -> BoughtItemModel:
        """_summary_

        Args:
            db (Session): DB session.
            db_obj_user (UserModel): The user who update the value.
            db_obj_item (BoughtItemModel): The current bought item as model.
            db_field (InstrumentedAttribute): The field which to update.
            value (bool | int | float | str | date): The value which to assign to the field.

        Raises:
            BoughtItemRequiredFieldNotSetError: The field is required. No value was given.

        Raises (by extension):
            InsufficientPermissionsError: User is not allowed to change the field.
            BoughtItemAlreadyPlannedError: The item is already planned and the user is not allowed to change.
            BoughtItemOfAnotherUserError: The item belongs to another user and the user is not allowed to change.
            ProjectInactiveError: The project of this item is inactive.

        Returns:
            BoughtItemModel: The updated bought item as model.
        """
        kwargs = locals()
        kwargs.pop("self")

        field_name = db_field.description
        if value == "" or value is None:
            raise BoughtItemRequiredFieldNotSetError(
                f"Blocked update of a bought item #{db_obj_item.id} ({db_obj_item.partnumber}): "
                f"User #{db_obj_user.id} ({db_obj_user.full_name}) tried to set the required field {field_name}, but "
                "no value was given."
            )
        return self.update_field(**kwargs)

    def delete(self, db: Session, *, db_obj_user: UserModel, db_obj_item: BoughtItemModel) -> Optional[BoughtItemModel]:
        """Deletes a bought item. Only marks the item as ´deleted`, items are never really gone.

        Args:
            db (Session): DB session.
            db_obj_user (UserModel): The user who deletes the item.
            db_obj_item (BoughtItemModel): The current item as model.

        Raises:
            InsufficientPermissionsError: User has not enough permission to delete the item.
            BoughtItemAlreadyPlannedError: User has not enough permission to delete a planned item.
            BoughtItemOfAnotherUserError: User has not enough permission to delete an item of another user.

        Returns:
            Optional[BoughtItemModel]: The deleted item as model.
        """
        # Rules
        if db_obj_user.is_guestuser:
            raise InsufficientPermissionsError(
                f"Blocked deletion of a bought item #{db_obj_item.id} ({db_obj_item.partnumber}): "
                f"User #{db_obj_user.id} ({db_obj_user.full_name}) tried to delete, but has not enough "
                "permissions (guest user)."
            )

        if (
            not (db_obj_user.is_superuser or db_obj_user.is_adminuser)
            and db_obj_item.status != cfg.items.bought.status.open
        ):
            raise BoughtItemAlreadyPlannedError(
                f"Blocked deletion of a bought item #{db_obj_item.id} ({db_obj_item.partnumber}): "
                f"User #{db_obj_user.id} ({db_obj_user.full_name}) tried to delete, but has not enough "
                "permissions to change planned items (not a superuser or admin user)."
            )

        if not (db_obj_user.is_superuser or db_obj_user.is_adminuser) and not db_obj_item.creator_id == db_obj_user.id:
            raise BoughtItemOfAnotherUserError(
                f"Blocked deletion of a bought item #{db_obj_item.id} ({db_obj_item.partnumber}): "
                f"User #{db_obj_user.id} ({db_obj_user.full_name}) tried to delete, but has not enough "
                "permissions to change another users items (not a superuser or admin user)."
            )

        data = {"deleted": True}
        data["changed"] = date.today()  # type:ignore
        data["changes"] = get_changelog(  # type:ignore
            changes="Marked item as deleted.",
            db_obj_user=db_obj_user,
            db_obj_item=db_obj_item,
        )
        item = super().update(db, db_obj=db_obj_item, obj_in=data)

        log.info(f"User {db_obj_user.username!r} deleted the a bought item " f"({item.partnumber}), ID={item.id}.")
        return item


crud_bought_item = CRUDBoughtItem(BoughtItemModel)
