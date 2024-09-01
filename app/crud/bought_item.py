"""
    Create-Read-Update-Delete: Bought Item
"""

# pylint: disable=R0914

from datetime import date
from typing import List
from typing import Optional

from api.schemas.bought_item import BoughtItemCreateSchema
from api.schemas.bought_item import BoughtItemUpdateSchema
from api.schemas.email_notification import EmailNotificationCreateSchema
from config import cfg
from crud.base import CRUDBase
from crud.email_notification import crud_email_notification
from db.models import BoughtItemModel
from db.models import UserModel
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
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
        BoughtItemCreateSchema,
        BoughtItemUpdateSchema,
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
        project: str | None = None,
        machine: str | None = None,
        quantity: float | None = None,
        unit: str | None = None,
        partnumber: str | None = None,
        definition: str | None = None,
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
        taken_over_id: int | None = None,
        storage_place: str | None = None,
        high_priority: bool | None = None,
        ignore_delivered: bool | None = None,
        ignore_canceled: bool | None = None,
        ignore_lost: bool | None = None,
    ) -> List[BoughtItemModel]:
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
                    output_list.append(asc(self.model.project))
                elif value == cfg.items.bought.order_by.machine:
                    output_list.append(asc(self.model.machine))
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
                self.model.project.ilike(f"%{project}%") if project else text(""),
                self.model.machine.ilike(f"%{machine}%") if machine else text(""),
                self.model.partnumber.ilike(f"%{partnumber}%") if partnumber else text(""),
                self.model.definition.ilike(f"%{definition}%") if definition else text(""),
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
                self.model.taken_over_id == taken_over_id if taken_over_id else text(""),
                self.model.storage_place.ilike(f"%{storage_place}%") if storage_place else text(""),
            )
            .order_by(order_by)
            .offset(skip)
            .limit(limit)
        )
        # log.debug(str(query))
        return query.all()

    def create(self, db: Session, *, db_obj_user: UserModel, obj_in: BoughtItemCreateSchema) -> BoughtItemModel:
        """Creates a new bought item.

        Args:
            db (Session): The database session.
            db_obj_user (UserModel): The user model who creates the item.
            obj_in (BoughtItemCreateSchema): The creation schema.

        Returns:
            BoughtItem: The new bought item model.
        """
        if db_obj_user.is_guestuser:
            raise HTTPException(status_code=403, detail="A guest user cannot create items.")

        data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=False)

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
        db_obj_item: BoughtItemModel | None,
        obj_in: BoughtItemUpdateSchema,
    ) -> BoughtItemModel:
        """Updates a bought item.

        Args:
            db (Session): The database session.
            db_obj_user (UserModel): The user model who updates the item.
            db_obj_item (BoughtItem): The model of the item to update.
            obj_in (BoughtItemUpdateSchema): The update data.

        Raises:
            HTTPException: Raised if the item doesn't exist.
            HTTPException: Raised if a normal user tries to edit a planned item.
            HTTPException: Raised if a normal user tries to edit an item of another user.

        Returns:
            BoughtItem: The updated bought item data model.
        """
        if not db_obj_item:
            raise HTTPException(status_code=404, detail="The item does not exist.")

        data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)

        # Rules
        if db_obj_user.is_guestuser:
            raise HTTPException(status_code=403, detail="A guest user cannot change items.")

        if (
            not (db_obj_user.is_superuser or db_obj_user.is_adminuser)
            and db_obj_item.status != cfg.items.bought.status.open
        ):
            raise HTTPException(status_code=403, detail="Only superusers and adminusers can change planned items.")

        if not (db_obj_user.is_superuser or db_obj_user.is_adminuser) and not db_obj_item.creator_id == db_obj_user.id:
            raise HTTPException(
                status_code=403,
                detail="Only superusers and adminusers can edit items from another user.",
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
        self, db: Session, *, db_obj_user: UserModel, db_obj_item: BoughtItemModel | None, status: str
    ) -> BoughtItemModel:
        """Updates the status of a bought item.

        Args:
            db (Session): The database session.
            db_obj_user (UserModel): The user model who updates the status.
            db_obj_item (BoughtItem): The bought item model.
            status (str): The new status.

        Raises:
            HTTPException: Raised if the item doesn't exist.
            HTTPException: Raised if the status would be set back to open.
            HTTPException: Raised if the status is unknown.

        Returns:
            BoughtItem: The bought item model of the updated field.
        """
        if not db_obj_item:
            raise HTTPException(status_code=404, detail="The item does not exist.")

        if status == db_obj_item.status:
            log.debug(f"No changes in item #{db_obj_item.id}.")
            return db_obj_item

        # Rules
        if db_obj_user.is_guestuser:
            raise HTTPException(status_code=403, detail="A guest user cannot change items.")

        if status == cfg.items.bought.status.open and db_obj_item.status != cfg.items.bought.status.open:
            raise HTTPException(status_code=403, detail="Cannot change status back to open.")

        if (
            not (db_obj_user.is_superuser or db_obj_user.is_adminuser)
            and db_obj_item.status != cfg.items.bought.status.open
        ):
            raise HTTPException(status_code=403, detail="Only superusers and adminusers can change planned items.")

        if not (db_obj_user.is_superuser or db_obj_user.is_adminuser) and not db_obj_item.creator_id == db_obj_user.id:
            raise HTTPException(
                status_code=403,
                detail="Only superusers and adminusers can edit items from another user.",
            )

        # Incoming data rules
        if status not in cfg.items.bought.status.values:
            raise HTTPException(status_code=400, detail="Unknown status.")

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
            data["taken_over_id"] = int(db_obj_user.id)  # type:ignore
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

    def update_field(
        self,
        db: Session,
        *,
        db_obj_user: UserModel,
        db_obj_item: BoughtItemModel | None,
        db_field: InstrumentedAttribute,
        value: bool | int | float | str | date,
    ) -> BoughtItemModel:
        """Updates a data field (db column).

        Args:
            db (Session): The database session.
            db_obj_user (UserModel): The user who updates the item.
            db_obj_item (BoughtItem | None): The item to update.
            db_field (Column): The database column.

            value (bool | int | float | str | date): The value to write to the column.

        Raises:
            HTTPException: Raised if the given item doesn't exist.

        Returns:
            BoughtItem: Returns the updated item.
        """
        if not db_obj_item:
            raise HTTPException(status_code=404, detail="The item with this id does not exist.")

        # Rules
        if db_obj_user.is_guestuser:
            raise HTTPException(status_code=403, detail="A guest user cannot change items.")

        if (
            not (db_obj_user.is_superuser or db_obj_user.is_adminuser)
            and db_obj_item.status != cfg.items.bought.status.open
        ):
            raise HTTPException(status_code=403, detail="Only superusers and adminusers can change planned items.")

        if not (db_obj_user.is_superuser or db_obj_user.is_adminuser) and not db_obj_item.creator_id == db_obj_user.id:
            raise HTTPException(
                status_code=403,
                detail="Only superusers and adminusers can edit an items from another user.",
            )

        field_name = db_field.description
        field_value = jsonable_encoder(db_obj_item)[field_name]

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
        db_obj_item: BoughtItemModel | None,
        db_field: InstrumentedAttribute,
        value: bool | int | float | str | date,
    ) -> BoughtItemModel:
        """Updates a required data field (db column).

        Args:
            db (Session): The database session.
            db_obj_user (UserModel): The user who updates the item.
            db_obj_item (BoughtItem | None): The item to update.
            db_field (Column): The database column.

            value (bool | int | float | str | date): The value to write to the column.

        Raises:
            HTTPException: Raised if the value is invalid.
            HTTPException: Raised if the given item doesn't exist.

        Returns:
            BoughtItem: Returns the updated item.
        """
        if db_obj_user.is_guestuser:
            raise HTTPException(status_code=403, detail="A guest user cannot change items.")

        kwargs = locals()
        kwargs.pop("self")

        if value == "" or value is None:
            raise HTTPException(
                status_code=403,
                detail=f"{db_field.description.capitalize()} must be set.",
            )
        return self.update_field(**kwargs)

    def delete(
        self, db: Session, *, db_obj_user: UserModel, db_obj_item: BoughtItemModel | None
    ) -> Optional[BoughtItemModel]:
        """Deletes an item (set its status to deleted).

        Args:
            db (Session): The database session.
            db_obj_user (UserModel): The user who deletes the item.
            db_obj_item (BoughtItem | None): The item to delete.

        Raises:
            HTTPException: Raised if the item doesn't exist.
            HTTPException: Raised if a normal user tries to delete an item from another \
                user.
            HTTPException: Raised if a normal user tries to delete a planned item.

        Returns:
            Optional[BoughtItem]: The as deleted marked item.
        """
        if db_obj_user.is_guestuser:
            raise HTTPException(status_code=403, detail="A guest user cannot delete items.")

        if not db_obj_item:
            raise HTTPException(
                status_code=404,
                detail="The item does not exist.",
            )

        if not (db_obj_user.is_superuser or db_obj_user.is_adminuser) and not db_obj_item.creator_id == db_obj_user.id:
            raise HTTPException(
                status_code=403,
                detail="Only a superuser or adminuser can delete an item from another user.",
            )

        if (
            not (db_obj_user.is_superuser or db_obj_user.is_adminuser)
            and db_obj_item.status != cfg.items.bought.status.open
        ):
            raise HTTPException(status_code=403, detail="Only a superuser or adminuser can delete a planned item.")

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
