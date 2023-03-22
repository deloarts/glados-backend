"""
    Handles all routes to the bought-items-resource web-API.
"""

# pylint: disable=R0913
# pylint: disable=R0914

import datetime
from pathlib import Path
from typing import Any, List

from db.session import DB
from api.deps import get_current_active_superuser, get_current_active_user, verify_token
from config import cfg
from const import ROOT, TEMPLATES
from crud import crud_bought_item
from excel.xlsx_export import ExportExcel
from excel.xlsx_import import ImportExcel
from fastapi import UploadFile
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends
from fastapi.responses import FileResponse
from fastapi.routing import APIRouter
from models import model_user
from models.model_bought_item import BoughtItem
from schemas import schema_bought_item
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/", response_model=List[schema_bought_item.BoughtItem])
def read_bought_items(
    db: Session = Depends(DB.get),
    skip: int | None = None,
    limit: int | None = None,
    sort_by: str | None = None,
    id: str | None = None,  # pylint: disable=W0622
    status: str | None = None,
    group_1: str | None = None,
    project: str | None = None,
    machine: str | None = None,
    partnumber: str | None = None,
    definition: str | None = None,
    manufacturer: str | None = None,
    supplier: str | None = None,
    creator_id: int | None = None,
    created_from: datetime.date | None = None,
    created_to: datetime.date | None = None,
    changed_from: datetime.date | None = None,
    changed_to: datetime.date | None = None,
    expected_from: datetime.date | None = None,
    expected_to: datetime.date | None = None,
    high_priority: bool | None = None,
    ignore_delivered: bool | None = None,
    ignore_canceled: bool | None = None,
    ignore_lost: bool | None = None,
    verified: bool = Depends(verify_token),
) -> Any:
    """Retrieve bought items."""
    kwargs = locals()
    kwargs.pop("verified")
    return crud_bought_item.bought_item.get_multi(**kwargs)


@router.get("/excel", response_class=FileResponse)
def read_bought_items_excel(
    db: Session = Depends(DB.get),
    skip: int | None = None,
    limit: int | None = None,
    sort_by: str | None = None,
    id: str | None = None,  # pylint: disable=W0622
    status: str | None = None,
    group_1: str | None = None,
    project: str | None = None,
    machine: str | None = None,
    partnumber: str | None = None,
    definition: str | None = None,
    manufacturer: str | None = None,
    supplier: str | None = None,
    creator_id: int | None = None,
    created_from: datetime.date | None = None,
    created_to: datetime.date | None = None,
    changed_from: datetime.date | None = None,
    changed_to: datetime.date | None = None,
    high_priority: bool | None = None,
    ignore_delivered: bool | None = None,
    ignore_canceled: bool | None = None,
    ignore_lost: bool | None = None,
    verified: bool = Depends(verify_token),
) -> Any:
    """Retrieve bought items as xlsx."""
    kwargs = locals()
    kwargs.pop("verified")

    data = crud_bought_item.bought_item.get_multi(**kwargs)
    xlsx = ExportExcel(data=data, schema=schema_bought_item.BoughtItemExcelExport)
    path = xlsx.save()

    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail="The EXCEL file could not be generated.",
        )

    return FileResponse(
        path=str(path),
        headers={"Content-Disposition": f'attachment; filename="{path.name}"'},
    )


@router.get("/excel-template", response_class=FileResponse)
def read_bought_items_excel_template(
    verified: bool = Depends(verify_token),
) -> Any:
    """Retrieve the excel template for the excel import."""
    path = Path(ROOT, TEMPLATES, cfg.templates.bought_item_excel_import)
    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail="Template file not found.",
        )

    return FileResponse(
        path=str(path),
        headers={"Content-Disposition": f'attachment; filename="{path.name}"'},
    )


@router.get("/{item_id}", response_model=schema_bought_item.BoughtItem)
def read_bought_item_by_id(
    item_id: int,
    verified: bool = Depends(verify_token),
    db: Session = Depends(DB.get),
) -> Any:
    """Get a specific bought item by db id."""
    item = crud_bought_item.bought_item.get(db, id=item_id)
    if not item:
        raise HTTPException(
            status_code=404,
            detail="The item with this id does not exist.",
        )
    return item


@router.get("/{item_id}/changelog", response_model=List[str])
def read_bought_item_changelog_by_id(
    item_id: int,
    verified: bool = Depends(verify_token),
    db: Session = Depends(DB.get),
) -> Any:
    """Get a specific bought item by db id."""
    item = crud_bought_item.bought_item.get(db, id=item_id)
    if not item:
        raise HTTPException(
            status_code=404,
            detail="The item with this id does not exist.",
        )
    return item.changes


@router.post("/", response_model=schema_bought_item.BoughtItem)
def create_bought_item(
    *,
    db: Session = Depends(DB.get),
    obj_in: schema_bought_item.BoughtItemCreate,
    current_user: model_user.User = Depends(get_current_active_user),
) -> Any:
    """Create new bought item."""
    return crud_bought_item.bought_item.create(
        db, db_obj_user=current_user, obj_in=obj_in
    )


@router.post("/excel", response_model=List[schema_bought_item.BoughtItem])
def create_bought_items_from_excel(
    *,
    db: Session = Depends(DB.get),
    file: UploadFile,
    current_user: model_user.User = Depends(get_current_active_user),
) -> Any:
    """Create new bought items from an excel file."""
    xlsx = ImportExcel(
        db=db,
        model=BoughtItem,
        schema=schema_bought_item.BoughtItemCreate,
        db_obj_user=current_user,
        file=file,
    )
    return xlsx.load()


@router.put("/{item_id}", response_model=schema_bought_item.BoughtItem)
def update_bought_item(
    *,
    db: Session = Depends(DB.get),
    item_id: int,
    obj_in: schema_bought_item.BoughtItemUpdate,
    current_user: model_user.User = Depends(get_current_active_user),
) -> Any:
    """Update a bought item."""
    item = crud_bought_item.bought_item.get(db, id=item_id)
    return crud_bought_item.bought_item.update(
        db, db_obj_user=current_user, db_obj_item=item, obj_in=obj_in
    )


@router.put("/{item_id}/status", response_model=schema_bought_item.BoughtItem)
def update_bought_item_status(
    *,
    db: Session = Depends(DB.get),
    item_id: int,
    status: str,
    current_user: model_user.User = Depends(get_current_active_superuser),
) -> Any:
    """Updates the status of an item."""
    item = crud_bought_item.bought_item.get(db, id=item_id)
    return crud_bought_item.bought_item.update_status(
        db, db_obj_user=current_user, db_obj_item=item, status=status
    )


@router.put("/{item_id}/group-1", response_model=schema_bought_item.BoughtItem)
def update_bought_item_group_1(
    *,
    db: Session = Depends(DB.get),
    item_id: int,
    group: str,
    current_user: model_user.User = Depends(get_current_active_superuser),
) -> Any:
    """Updates the group of an item."""
    item = crud_bought_item.bought_item.get(db, id=item_id)
    return crud_bought_item.bought_item.update_field(
        db,
        db_obj_user=current_user,
        db_obj_item=item,
        db_field=BoughtItem.group_1,
        value=group,
    )


@router.put("/{item_id}/project", response_model=schema_bought_item.BoughtItem)
def update_bought_item_project(
    *,
    db: Session = Depends(DB.get),
    item_id: int,
    project: str,
    current_user: model_user.User = Depends(get_current_active_superuser),
) -> Any:
    """Updates the project of an item."""
    item = crud_bought_item.bought_item.get(db, id=item_id)
    return crud_bought_item.bought_item.update_required_field(
        db,
        db_obj_user=current_user,
        db_obj_item=item,
        db_field=BoughtItem.project,
        value=project,
    )


@router.put("/{item_id}/machine", response_model=schema_bought_item.BoughtItem)
def update_bought_item_machine(
    *,
    db: Session = Depends(DB.get),
    item_id: int,
    machine: str,
    current_user: model_user.User = Depends(get_current_active_superuser),
) -> Any:
    """Updates the machine of an item."""
    item = crud_bought_item.bought_item.get(db, id=item_id)
    return crud_bought_item.bought_item.update_field(
        db,
        db_obj_user=current_user,
        db_obj_item=item,
        db_field=BoughtItem.machine,
        value=machine,
    )


@router.put("/{item_id}/quantity", response_model=schema_bought_item.BoughtItem)
def update_bought_item_quantity(
    *,
    db: Session = Depends(DB.get),
    item_id: int,
    quantity: str,
    current_user: model_user.User = Depends(get_current_active_superuser),
) -> Any:
    """Updates the quantity of an item."""
    item = crud_bought_item.bought_item.get(db, id=item_id)
    return crud_bought_item.bought_item.update_required_field(
        db,
        db_obj_user=current_user,
        db_obj_item=item,
        db_field=BoughtItem.quantity,
        value=quantity,
    )


@router.put("/{item_id}/partnumber", response_model=schema_bought_item.BoughtItem)
def update_bought_item_partnumber(
    *,
    db: Session = Depends(DB.get),
    item_id: int,
    partnumber: str,
    current_user: model_user.User = Depends(get_current_active_superuser),
) -> Any:
    """Updates the partnumber of an item."""
    item = crud_bought_item.bought_item.get(db, id=item_id)
    return crud_bought_item.bought_item.update_required_field(
        db,
        db_obj_user=current_user,
        db_obj_item=item,
        db_field=BoughtItem.partnumber,
        value=partnumber,
    )


@router.put("/{item_id}/definition", response_model=schema_bought_item.BoughtItem)
def update_bought_item_definition(
    *,
    db: Session = Depends(DB.get),
    item_id: int,
    definition: str,
    current_user: model_user.User = Depends(get_current_active_superuser),
) -> Any:
    """Updates the definition of an item."""
    item = crud_bought_item.bought_item.get(db, id=item_id)
    return crud_bought_item.bought_item.update_required_field(
        db,
        db_obj_user=current_user,
        db_obj_item=item,
        db_field=BoughtItem.definition,
        value=definition,
    )


@router.put("/{item_id}/manufacturer", response_model=schema_bought_item.BoughtItem)
def update_bought_item_manufacturer(
    *,
    db: Session = Depends(DB.get),
    item_id: int,
    manufacturer: str,
    current_user: model_user.User = Depends(get_current_active_superuser),
) -> Any:
    """Updates the manufacturer of an item."""
    item = crud_bought_item.bought_item.get(db, id=item_id)
    return crud_bought_item.bought_item.update_required_field(
        db,
        db_obj_user=current_user,
        db_obj_item=item,
        db_field=BoughtItem.manufacturer,
        value=manufacturer,
    )


@router.put("/{item_id}/supplier", response_model=schema_bought_item.BoughtItem)
def update_bought_item_supplier(
    *,
    db: Session = Depends(DB.get),
    item_id: int,
    supplier: str,
    current_user: model_user.User = Depends(get_current_active_superuser),
) -> Any:
    """Updates the supplier of an item."""
    item = crud_bought_item.bought_item.get(db, id=item_id)
    return crud_bought_item.bought_item.update_field(
        db,
        db_obj_user=current_user,
        db_obj_item=item,
        db_field=BoughtItem.supplier,
        value=supplier,
    )


@router.put("/{item_id}/note-general", response_model=schema_bought_item.BoughtItem)
def update_bought_item_note_general(
    *,
    db: Session = Depends(DB.get),
    item_id: int,
    note: str,
    current_user: model_user.User = Depends(get_current_active_superuser),
) -> Any:
    """Updates the general note of an item."""
    item = crud_bought_item.bought_item.get(db, id=item_id)
    return crud_bought_item.bought_item.update_field(
        db,
        db_obj_user=current_user,
        db_obj_item=item,
        db_field=BoughtItem.note_general,
        value=note,
    )


@router.put("/{item_id}/note-supplier", response_model=schema_bought_item.BoughtItem)
def update_bought_item_note_supplier(
    *,
    db: Session = Depends(DB.get),
    item_id: int,
    note: str,
    current_user: model_user.User = Depends(get_current_active_superuser),
) -> Any:
    """Updates the supplier note of an item."""
    item = crud_bought_item.bought_item.get(db, id=item_id)
    return crud_bought_item.bought_item.update_field(
        db,
        db_obj_user=current_user,
        db_obj_item=item,
        db_field=BoughtItem.note_supplier,
        value=note,
    )


@router.put(
    "/{item_id}/desired-delivery-date", response_model=schema_bought_item.BoughtItem
)
def update_bought_item_desired_delivery_date(
    *,
    db: Session = Depends(DB.get),
    item_id: int,
    date: datetime.date,
    current_user: model_user.User = Depends(get_current_active_superuser),
) -> Any:
    """Updates the desired delivery date of an item."""
    item = crud_bought_item.bought_item.get(db, id=item_id)
    return crud_bought_item.bought_item.update_field(
        db,
        db_obj_user=current_user,
        db_obj_item=item,
        db_field=BoughtItem.desired_delivery_date,
        value=date,
    )


@router.put(
    "/{item_id}/expected-delivery-date", response_model=schema_bought_item.BoughtItem
)
def update_bought_item_expected_delivery_date(
    *,
    db: Session = Depends(DB.get),
    item_id: int,
    date: datetime.date,
    current_user: model_user.User = Depends(get_current_active_superuser),
) -> Any:
    """Updates the expected delivery date of an item."""
    item = crud_bought_item.bought_item.get(db, id=item_id)
    return crud_bought_item.bought_item.update_field(
        db,
        db_obj_user=current_user,
        db_obj_item=item,
        db_field=BoughtItem.expected_delivery_date,
        value=date,
    )


@router.put("/{item_id}/storage", response_model=schema_bought_item.BoughtItem)
def update_bought_item_storage(
    *,
    db: Session = Depends(DB.get),
    item_id: int,
    storage_place: str,
    current_user: model_user.User = Depends(get_current_active_superuser),
) -> Any:
    """Updates the storage of an item."""
    item = crud_bought_item.bought_item.get(db, id=item_id)
    return crud_bought_item.bought_item.update_field(
        db,
        db_obj_user=current_user,
        db_obj_item=item,
        db_field=BoughtItem.storage_place,
        value=storage_place,
    )


@router.delete("/{item_id}", response_model=schema_bought_item.BoughtItem)
def delete_bought_item(
    *,
    db: Session = Depends(DB.get),
    item_id: int,
    current_user: model_user.User = Depends(get_current_active_user),
) -> Any:
    """Delete an item."""
    item = crud_bought_item.bought_item.get(db, id=item_id)
    return crud_bought_item.bought_item.delete(
        db, db_obj_item=item, db_obj_user=current_user
    )
