"""
    Create-Read-Update-Delete: Bought Item
"""

# pylint: disable=R0914

from datetime import date
from typing import List, Optional

from config import cfg
from crud.crud_base import CRUDBase
from crud.crud_email_notification import email_notification
from crud.helper import get_changelog
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from multilog import log
from schemas import schema_bought_item, schema_email_notification
from sqlalchemy import Column
from sqlalchemy.orm import Session
from sqlalchemy.sql import text

from models import model_user, model_bought_item  # isort: skip


class CRUDBoughtItem(
    CRUDBase[
        model_bought_item.BoughtItem,
        schema_bought_item.BoughtItemCreate,
        schema_bought_item.BoughtItemUpdate,
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
    ) -> List[model_bought_item.BoughtItem]:
        """Returns a list of bought items by the given filter params."""

        def build_order_by(keyword: str | None) -> str:
            """
            Inner function to create the order_by string.
            # TODO: Refactor this.
            """
            if keyword is None:
                return f"{self.model.id} desc"
            output_list = []
            values = keyword.split(",")
            for value in values:
                if value == cfg.items.bought.order_by.high_priority:
                    output_list.append(f"{self.model.high_priority} desc")
                elif value == cfg.items.bought.order_by.created:
                    output_list.append(f"{self.model.created} asc")
                elif value == cfg.items.bought.order_by.project:
                    output_list.append(f"{self.model.project} asc")
                elif value == cfg.items.bought.order_by.machine:
                    output_list.append(f"{self.model.machine} asc")
                elif value == cfg.items.bought.order_by.group_1:
                    output_list.append(f"{self.model.group_1} asc")
                elif value == cfg.items.bought.order_by.manufacturer:
                    output_list.append(f"{self.model.manufacturer} asc")
                elif value == cfg.items.bought.order_by.supplier:
                    output_list.append(f"{self.model.supplier} asc")
            output_list.append(f"{self.model.id} desc")
            return ",".join(output_list)

        if created_from is None:
            created_from = date(2000, 1, 1)
        if created_to is None:
            created_to = date.today()

        if changed_from is None:
            changed_from = date(2000, 1, 1)
        if changed_to is None:
            changed_to = date.today()

        # if desired_from is None:
        #     desired_from = date(2000, 1, 1)
        # if desired_to is None:
        #     desired_to = date.today()

        # if expected_from is None:
        #     expected_from = date(2000, 1, 1)
        # if expected_to is None:
        #     expected_to = date.today()

        order_by = build_order_by(sort_by)

        return (
            db.query(self.model)
            .filter_by(
                deleted=False,
                status=status if status else self.model.status,
                high_priority=high_priority
                if high_priority
                else self.model.high_priority,
                id=id if id else self.model.id,
                quantity=quantity if quantity else self.model.quantity,
                unit=unit if unit else self.model.unit,
                creator_id=creator_id if creator_id else self.model.creator_id,
            )
            .filter(
                # ignore filter
                self.model.status != cfg.items.bought.status.delivered
                if ignore_delivered
                else text(""),
                self.model.status != cfg.items.bought.status.canceled
                if ignore_canceled
                else text(""),
                self.model.status != cfg.items.bought.status.lost
                if ignore_lost
                else text(""),
                # search filter
                self.model.project.ilike(f"%{project}%") if project else text(""),
                self.model.machine.ilike(f"%{machine}%") if machine else text(""),
                self.model.partnumber.ilike(f"%{partnumber}%")
                if partnumber
                else text(""),
                self.model.definition.ilike(f"%{definition}%")
                if definition
                else text(""),
                self.model.manufacturer.ilike(f"%{manufacturer}%")
                if manufacturer
                else text(""),
                self.model.supplier.ilike(f"%{supplier}%") if supplier else text(""),
                self.model.group_1.ilike(f"%{group_1}%") if group_1 else text(""),
                self.model.note_general.ilike(f"%{note_general}%")
                if note_general
                else text(""),
                self.model.note_supplier.ilike(f"%{note_supplier}%")
                if note_supplier
                else text(""),
                self.model.created >= created_from,
                self.model.created <= created_to,
                self.model.changed >= changed_from,
                self.model.changed <= changed_to,
                self.model.desired_delivery_date >= desired_from
                if desired_from
                else text(""),
                self.model.desired_delivery_date <= desired_to
                if desired_to
                else text(""),
                self.model.requester_id == requester_id if requester_id else text(""),
                self.model.requested_date >= requested_from
                if requested_from
                else text(""),
                self.model.requested_date <= requested_to if requested_to else text(""),
                self.model.orderer_id == orderer_id if orderer_id else text(""),
                self.model.ordered_date >= ordered_from if ordered_from else text(""),
                self.model.ordered_date <= ordered_to if ordered_to else text(""),
                self.model.expected_delivery_date >= expected_from
                if expected_from
                else text(""),
                self.model.expected_delivery_date <= expected_to
                if expected_to
                else text(""),
                self.model.delivery_date >= delivered_from
                if delivered_from
                else text(""),
                self.model.delivery_date <= delivered_to if delivered_to else text(""),
                self.model.taken_over_id == taken_over_id
                if taken_over_id
                else text(""),
                self.model.storage_place.ilike(f"%{storage_place}%")
                if storage_place
                else text(""),
            )
            .order_by(text(order_by))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create(
        self,
        db: Session,
        *,
        db_obj_user: model_user.User,
        obj_in: schema_bought_item.BoughtItemCreate,
    ) -> model_bought_item.BoughtItem:
        """Creates a new bought item.

        Args:
            db (Session): The database session.
            db_obj_user (model_user.User): The user model who creates the item.
            obj_in (schema_bought_item.BoughtItemCreate): The creation schema.

        Returns:
            model_bought_item.BoughtItem: The new bought item model.
        """
        data = obj_in if isinstance(obj_in, dict) else obj_in.dict(exclude_unset=False)

        # Manipulate data
        data["created"] = date.today()
        data["changed"] = date.today()
        data["creator_id"] = db_obj_user.id
        data["changes"] = get_changelog(
            changes="Item created.", db_obj_user=db_obj_user
        )

        db_obj = model_bought_item.BoughtItem(**data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        log.info(
            f"User {db_obj_user.username!r} created new 'bought item' "
            f"({db_obj.partnumber}), ID={db_obj.id}."
        )
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj_user: model_user.User,
        db_obj_item: model_bought_item.BoughtItem | None,
        obj_in: schema_bought_item.BoughtItemUpdate,  # | Dict[str, Any],
    ) -> model_bought_item.BoughtItem:
        """Updates a bought item.

        Args:
            db (Session): The database session.
            db_obj_user (model_user.User): The user model who updates the item.
            db_obj_item (model_bought_item.BoughtItem | None): The model of the item to \
                update.
            obj_in (schema_bought_item.BoughtItemUpdate): The update data.

        Raises:
            HTTPException: Raised if the item doesn't exist.
            HTTPException: Raised if a normal user tries to edit a planned item.
            HTTPException: Raised if a normal user tries to edit an item of another user.

        Returns:
            model_bought_item.BoughtItem: _description_
        """
        if not db_obj_item:
            raise HTTPException(status_code=404, detail="The item does not exist.")

        data = obj_in if isinstance(obj_in, dict) else obj_in.dict(exclude_unset=True)

        # Rules
        if (
            not db_obj_user.is_superuser
            and db_obj_item.status != cfg.items.bought.status.open
        ):
            raise HTTPException(
                status_code=403, detail="Only a superuser can change planned items."
            )

        if (
            not db_obj_user.is_superuser
            and not db_obj_item.creator_id == db_obj_user.id
        ):
            raise HTTPException(
                status_code=403,
                detail="Only a superuser can edit an item from another user.",
            )

        # Manipulate data
        data["changed"] = date.today()
        data["changes"] = get_changelog(
            changes="Item updated.", db_obj_user=db_obj_user, db_obj_item=db_obj_item
        )

        item = super().update(db, db_obj=db_obj_item, obj_in=data)

        log.info(
            f"User {db_obj_user.username!r} updated a bought item "
            f"({item.partnumber}), ID={item.id}."
        )
        return item

    def update_status(
        self,
        db: Session,
        *,
        db_obj_user: model_user.User,
        db_obj_item: model_bought_item.BoughtItem | None,
        status: str,
    ) -> model_bought_item.BoughtItem:
        """Updates the status of a bought item.

        Args:
            db (Session): The database session.
            db_obj_user (model_user.User): The user model who updates the status.
            db_obj_item (model_bought_item.BoughtItem | None): The bought item model.
            status (str): The new status.

        Raises:
            HTTPException: Raised if the item doesn't exist.
            HTTPException: Raised if the status would be set back to open.
            HTTPException: Raised if the status is unknown.

        Returns:
            model_bought_item.BoughtItem: _description_
        """
        if not db_obj_item:
            raise HTTPException(status_code=404, detail="The item does not exist.")

        if status == db_obj_item.status:
            log.debug(f"No changes in item #{db_obj_item.id}.")
            return db_obj_item

        # Rules
        if (
            status == cfg.items.bought.status.open
            and db_obj_item.status != cfg.items.bought.status.open
        ):
            raise HTTPException(
                status_code=403, detail="Cannot change status back to open."
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
            notification = schema_email_notification.EmailNotificationCreate(
                reason="late",
                receiver_id=db_obj_item.creator_id,
                bought_item_id=db_obj_item.id,
            )
            email_notification.create(db=db, obj_in=notification)

        if (
            db_obj_item.notify_on_delivery
            and status == cfg.items.bought.status.delivered
        ):
            notification = schema_email_notification.EmailNotificationCreate(
                reason="delivered",
                receiver_id=db_obj_item.creator_id,
                bought_item_id=db_obj_item.id,
            )
            email_notification.create(db=db, obj_in=notification)

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
        db_obj_user: model_user.User,
        db_obj_item: model_bought_item.BoughtItem | None,
        db_field: Column,
        value: bool | int | float | str | date,
    ) -> model_bought_item.BoughtItem:
        """Updates a data field (db column).

        Args:
            db (Session): The database session.
            db_obj_user (model_user.User): The user who updates the item.
            db_obj_item (model_bought_item.BoughtItem | None): The item to update.
            db_field (Column): The database column.

            value (bool | int | float | str | date): The value to write to the column.

        Raises:
            HTTPException: Raised if the given item doesn't exist.

        Returns:
            model_bought_item.BoughtItem: Returns the updated item.
        """
        if not db_obj_item:
            raise HTTPException(
                status_code=404, detail="The item with this id does not exist."
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
        db_obj_user: model_user.User,
        db_obj_item: model_bought_item.BoughtItem | None,
        db_field: Column,
        value: bool | int | float | str | date,
    ) -> model_bought_item.BoughtItem:
        """Updates a required data field (db column).

        Args:
            db (Session): The database session.
            db_obj_user (model_user.User): The user who updates the item.
            db_obj_item (model_bought_item.BoughtItem | None): The item to update.
            db_field (Column): The database column.

            value (bool | int | float | str | date): The value to write to the column.

        Raises:
            HTTPException: Raised if the value is invalid.
            HTTPException: Raised if the given item doesn't exist.

        Returns:
            model_bought_item.BoughtItem: Returns the updated item.
        """
        kwargs = locals()
        kwargs.pop("self")

        if value == "" or value is None:
            raise HTTPException(
                status_code=403,
                detail=f"{db_field.description.capitalize()} must be set.",
            )
        return self.update_field(**kwargs)

    def delete(
        self,
        db: Session,
        *,
        db_obj_user: model_user.User,
        db_obj_item: model_bought_item.BoughtItem | None,
    ) -> Optional[model_bought_item.BoughtItem]:
        """Deletes an item (set its status to deleted).

        Args:
            db (Session): The database session.
            db_obj_user (model_user.User): The user who deletes the item.
            db_obj_item (model_bought_item.BoughtItem | None): The item to delete.

        Raises:
            HTTPException: Raised if the item doesn't exist.
            HTTPException: Raised if a normal user tries to delete an item from another \
                user.
            HTTPException: Raised if a normal user tries to delete a planned item.

        Returns:
            Optional[model_bought_item.BoughtItem]: The as deleted marked item.
        """
        if not db_obj_item:
            raise HTTPException(
                status_code=404,
                detail="The item does not exist.",
            )

        if (
            not db_obj_user.is_superuser
            and not db_obj_item.creator_id == db_obj_user.id
        ):
            raise HTTPException(
                status_code=403,
                detail="Only a superuser can delete an item from another user.",
            )

        if (
            not db_obj_user.is_superuser
            and db_obj_item.status != cfg.items.bought.status.open
        ):
            raise HTTPException(
                status_code=403, detail="Only a superuser can delete a planned item."
            )

        data = {"deleted": True}
        data["changed"] = date.today()  # type:ignore
        data["changes"] = get_changelog(  # type:ignore
            changes="Marked item as deleted.",
            db_obj_user=db_obj_user,
            db_obj_item=db_obj_item,
        )
        item = super().update(db, db_obj=db_obj_item, obj_in=data)

        log.info(
            f"User {db_obj_user.username!r} deleted the a bought item "
            f"({item.partnumber}), ID={item.id}."
        )
        return item


bought_item = CRUDBoughtItem(model_bought_item.BoughtItem)
