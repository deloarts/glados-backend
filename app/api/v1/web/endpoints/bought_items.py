"""
    Handles all routes to the bought-items-resource web-API.
"""

# pylint: disable=R0913
# pylint: disable=R0914

import datetime
from pathlib import Path
from typing import Any
from typing import List

from api.deps import get_current_active_user
from api.deps import verify_token
from api.schemas.bought_item import BoughtItemCreateWebSchema
from api.schemas.bought_item import BoughtItemSchema
from api.schemas.bought_item import BoughtItemUpdateWebSchema
from config import cfg
from const import ROOT
from const import TEMPLATES
from crud.bought_item import crud_bought_item
from db.models import BoughtItemModel
from db.models import UserModel
from db.session import get_db
from excel.xlsx_export.bought_item import BoughtItemExcelExport
from excel.xlsx_import.bought_item import BoughtItemExcelImport
from exceptions import BoughtItemAlreadyPlannedError
from exceptions import BoughtItemCannotChangeToOpenError
from exceptions import BoughtItemOfAnotherUserError
from exceptions import BoughtItemRequiredFieldNotSetError
from exceptions import BoughtItemUnknownStatusError
from exceptions import ExcelImportDataInvalidError
from exceptions import ExcelImportHeaderInvalidError
from exceptions import ExcelImportHeaderMissingError
from exceptions import InsufficientPermissionsError
from exceptions import ProjectInactiveError
from exceptions import ProjectNotFoundError
from fastapi import UploadFile
from fastapi import status as sc
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends
from fastapi.responses import FileResponse
from fastapi.routing import APIRouter
from locales import lang
from multilog import log
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/", response_model=List[BoughtItemSchema])
def read_bought_items(
    db: Session = Depends(get_db),
    skip: int | None = None,
    limit: int | None = None,
    sort_by: str | None = None,
    id: str | None = None,  # pylint: disable=W0622
    status: str | None = None,
    project_number: str | None = None,
    product_number: str | None = None,
    project_customer: str | None = None,
    project_description: str | None = None,
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
    created_from: datetime.date | None = None,
    created_to: datetime.date | None = None,
    changed_from: datetime.date | None = None,
    changed_to: datetime.date | None = None,
    desired_from: datetime.date | None = None,
    desired_to: datetime.date | None = None,
    requester_id: int | None = None,
    requested_from: datetime.date | None = None,
    requested_to: datetime.date | None = None,
    orderer_id: int | None = None,
    ordered_from: datetime.date | None = None,
    ordered_to: datetime.date | None = None,
    expected_from: datetime.date | None = None,
    expected_to: datetime.date | None = None,
    delivered_from: datetime.date | None = None,
    delivered_to: datetime.date | None = None,
    receiver_id: int | None = None,
    storage_place: str | None = None,
    high_priority: bool | None = None,
    ignore_delivered: bool | None = None,
    ignore_canceled: bool | None = None,
    ignore_lost: bool | None = None,
    verified: bool = Depends(verify_token),
) -> Any:
    """Retrieve bought items."""
    kwargs = locals()
    kwargs.pop("verified")
    items = crud_bought_item.get_multi(**kwargs)
    log.debug(f"Found {len(items)} items with filter {kwargs}")
    return items


@router.get("/excel", response_class=FileResponse)
def read_bought_items_excel(
    db: Session = Depends(get_db),
    skip: int | None = None,
    limit: int | None = None,
    sort_by: str | None = None,
    id: str | None = None,  # pylint: disable=W0622
    status: str | None = None,
    project_number: str | None = None,
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
    created_from: datetime.date | None = None,
    created_to: datetime.date | None = None,
    changed_from: datetime.date | None = None,
    changed_to: datetime.date | None = None,
    desired_from: datetime.date | None = None,
    desired_to: datetime.date | None = None,
    requester_id: int | None = None,
    requested_from: datetime.date | None = None,
    requested_to: datetime.date | None = None,
    orderer_id: int | None = None,
    ordered_from: datetime.date | None = None,
    ordered_to: datetime.date | None = None,
    expected_from: datetime.date | None = None,
    expected_to: datetime.date | None = None,
    delivered_from: datetime.date | None = None,
    delivered_to: datetime.date | None = None,
    receiver_id: int | None = None,
    storage_place: str | None = None,
    high_priority: bool | None = None,
    ignore_delivered: bool | None = None,
    ignore_canceled: bool | None = None,
    ignore_lost: bool | None = None,
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """Retrieve bought items as xlsx."""
    kwargs = locals()
    kwargs.pop("current_user")

    data = crud_bought_item.get_multi(**kwargs)
    export_handler = BoughtItemExcelExport(data=data)
    path = export_handler.save()

    if not path.exists():
        raise HTTPException(
            status_code=sc.HTTP_417_EXPECTATION_FAILED,
            detail=lang(current_user).API.BOUGHTITEM.FAILED_EXCEL_GENERATION,
        )
    return FileResponse(
        path=str(path),
        headers={"Content-Disposition": f'attachment; filename="{path.name}"'},
    )


@router.get("/excel-template", response_class=FileResponse)
def read_bought_items_excel_template(current_user: UserModel = Depends(get_current_active_user)) -> Any:
    """Retrieve the excel template for the excel import."""
    path = Path(ROOT, TEMPLATES, cfg.templates.bought_item_excel_import)
    if not path.exists():
        raise HTTPException(
            status_code=sc.HTTP_404_NOT_FOUND,
            detail=lang(current_user).API.BOUGHTITEM.TEMPLATE_NOT_FOUND,
        )
    return FileResponse(
        path=str(path),
        headers={"Content-Disposition": f'attachment; filename="{path.name}"'},
    )


@router.get("/{item_id}", response_model=BoughtItemSchema)
def read_bought_item_by_id(
    item_id: int, current_user: UserModel = Depends(get_current_active_user), db: Session = Depends(get_db)
) -> Any:
    """Get a specific bought item by db id."""
    item = crud_bought_item.get(db, id=item_id)
    if not item:
        raise HTTPException(
            status_code=sc.HTTP_404_NOT_FOUND,
            detail=lang(current_user).API.BOUGHTITEM.ITEM_NOT_FOUND,
        )
    return item


@router.get("/{item_id}/changelog", response_model=List[str])
def read_bought_item_changelog_by_id(
    item_id: int, current_user: UserModel = Depends(get_current_active_user), db: Session = Depends(get_db)
) -> Any:
    """Get a specific bought item by db id."""
    item = crud_bought_item.get(db, id=item_id)
    if not item:
        raise HTTPException(
            status_code=sc.HTTP_404_NOT_FOUND,
            detail=lang(current_user).API.BOUGHTITEM.ITEM_NOT_FOUND,
        )
    return item.changes


@router.post("/validate", response_model=BoughtItemCreateWebSchema)
def validate_bought_item(
    *,
    obj_in: BoughtItemCreateWebSchema,
) -> Any:
    return obj_in


@router.post("/", response_model=BoughtItemSchema)
def create_bought_item(
    *,
    db: Session = Depends(get_db),
    obj_in: BoughtItemCreateWebSchema,
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """Create new bought item."""
    try:
        item = crud_bought_item.create(db, db_obj_user=current_user, obj_in=obj_in)
    except InsufficientPermissionsError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.CREATE_NO_PERMISSION
        ) from e
    except ProjectNotFoundError as e:
        raise HTTPException(
            status_code=sc.HTTP_404_NOT_FOUND, detail=lang(current_user).API.BOUGHTITEM.PROJECT_NOT_FOUND
        ) from e
    except ProjectInactiveError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.PROJECT_INACTIVE
        ) from e
    return item


@router.post("/excel", response_model=List[BoughtItemCreateWebSchema] | List[BoughtItemSchema] | List[dict])
def create_bought_items_from_excel(
    *,
    db: Session = Depends(get_db),
    force_create: bool = False,
    skip_validation: bool = False,
    file: UploadFile,
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """Returns the bo."""
    xlsx = BoughtItemExcelImport(db=db, db_obj_user=current_user, file=file)
    try:
        if force_create:
            return xlsx.batch_create()
        else:
            return xlsx.get_data_as_create_schema(skip_validation=skip_validation)
    except ExcelImportHeaderInvalidError as e:
        raise HTTPException(status_code=sc.HTTP_406_NOT_ACCEPTABLE, detail=str(e)) from e
    except ExcelImportHeaderMissingError as e:
        raise HTTPException(status_code=sc.HTTP_404_NOT_FOUND, detail=str(e)) from e
    # except ExcelImportDataInvalidError as e:
    #     raise HTTPException(status_code=sc.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)) from e


@router.put("/{item_id}", response_model=BoughtItemSchema)
def update_bought_item(
    *,
    db: Session = Depends(get_db),
    item_id: int,
    obj_in: BoughtItemUpdateWebSchema,
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """Update a bought item."""
    item = crud_bought_item.get(db, id=item_id)
    if not item:
        raise HTTPException(status_code=sc.HTTP_404_NOT_FOUND, detail=lang(current_user).API.BOUGHTITEM.ITEM_NOT_FOUND)

    try:
        updated_item = crud_bought_item.update(db, db_obj_user=current_user, db_obj_item=item, obj_in=obj_in)
    except ProjectNotFoundError as e:
        raise HTTPException(
            status_code=sc.HTTP_404_NOT_FOUND, detail=lang(current_user).API.BOUGHTITEM.PROJECT_NOT_FOUND
        ) from e
    except ProjectInactiveError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.PROJECT_INACTIVE
        ) from e
    except BoughtItemOfAnotherUserError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.CANNOT_CHANGE_OTHER_USER_ITEM
        ) from e
    except BoughtItemAlreadyPlannedError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.CANNOT_CHANGE_PLANNED_ITEM
        ) from e
    except InsufficientPermissionsError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.UPDATE_NO_PERMISSION
        ) from e

    return updated_item


@router.put("/{item_id}/status", response_model=BoughtItemSchema)
def update_bought_item_status(
    *,
    db: Session = Depends(get_db),
    item_id: int,
    status: str,
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """Updates the status of an item."""
    item = crud_bought_item.get(db, id=item_id)
    if not item:
        raise HTTPException(status_code=sc.HTTP_404_NOT_FOUND, detail=lang(current_user).API.BOUGHTITEM.ITEM_NOT_FOUND)

    try:
        updated_item = crud_bought_item.update_status(db, db_obj_user=current_user, db_obj_item=item, status=status)
    except BoughtItemUnknownStatusError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.UNKNOWN_STATUS
        ) from e
    except BoughtItemCannotChangeToOpenError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.CANNOT_CHANGE_TO_OPEN
        ) from e
    except BoughtItemOfAnotherUserError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.CANNOT_CHANGE_OTHER_USER_ITEM
        ) from e
    except BoughtItemAlreadyPlannedError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.CANNOT_CHANGE_PLANNED_ITEM
        ) from e
    except InsufficientPermissionsError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.UPDATE_NO_PERMISSION
        ) from e

    return updated_item


@router.put("/{item_id}/project", response_model=BoughtItemSchema)
def update_bought_item_project(
    *,
    db: Session = Depends(get_db),
    item_id: int,
    project_number: str,
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """Updates the project of an item."""
    item = crud_bought_item.get(db, id=item_id)
    if not item:
        raise HTTPException(status_code=sc.HTTP_404_NOT_FOUND, detail=lang(current_user).API.BOUGHTITEM.ITEM_NOT_FOUND)

    try:
        updated_item = crud_bought_item.update_project(
            db, db_obj_user=current_user, db_obj_item=item, project_number=project_number
        )
    except ProjectNotFoundError as e:
        raise HTTPException(
            status_code=sc.HTTP_404_NOT_FOUND, detail=lang(current_user).API.BOUGHTITEM.PROJECT_NOT_FOUND
        )
    except ProjectInactiveError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.PROJECT_INACTIVE
        ) from e
    except BoughtItemAlreadyPlannedError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.CANNOT_CHANGE_PLANNED_ITEM
        ) from e
    except BoughtItemOfAnotherUserError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.CANNOT_CHANGE_OTHER_USER_ITEM
        ) from e
    except InsufficientPermissionsError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.UPDATE_NO_PERMISSION
        ) from e

    return updated_item


@router.put("/{item_id}/group-1", response_model=BoughtItemSchema)
def update_bought_item_group_1(
    *,
    db: Session = Depends(get_db),
    item_id: int,
    group: str,
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """Updates the group of an item."""
    item = crud_bought_item.get(db, id=item_id)
    if not item:
        raise HTTPException(status_code=sc.HTTP_404_NOT_FOUND, detail=lang(current_user).API.BOUGHTITEM.ITEM_NOT_FOUND)

    try:
        updated_item = crud_bought_item.update_field(
            db, db_obj_user=current_user, db_obj_item=item, db_field=BoughtItemModel.group_1, value=group
        )
    except BoughtItemAlreadyPlannedError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.CANNOT_CHANGE_PLANNED_ITEM
        ) from e
    except BoughtItemOfAnotherUserError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.CANNOT_CHANGE_OTHER_USER_ITEM
        ) from e
    except InsufficientPermissionsError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.UPDATE_NO_PERMISSION
        ) from e
    except ProjectInactiveError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.PROJECT_INACTIVE
        ) from e

    return updated_item


@router.put("/{item_id}/product-number", response_model=BoughtItemSchema)
def update_bought_item_product_number(
    *,
    db: Session = Depends(get_db),
    item_id: int,
    product_number: str,
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """Updates the product number of an item."""
    raise HTTPException(status_code=sc.HTTP_410_GONE, detail="Product number must be changed in the project.")


@router.put("/{item_id}/quantity", response_model=BoughtItemSchema)
def update_bought_item_quantity(
    *,
    db: Session = Depends(get_db),
    item_id: int,
    quantity: str,
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """Updates the quantity of an item."""
    item = crud_bought_item.get(db, id=item_id)
    if not item:
        raise HTTPException(status_code=sc.HTTP_404_NOT_FOUND, detail=lang(current_user).API.BOUGHTITEM.ITEM_NOT_FOUND)

    try:
        updated_item = crud_bought_item.update_required_field(
            db, db_obj_user=current_user, db_obj_item=item, db_field=BoughtItemModel.quantity, value=quantity
        )
    except BoughtItemRequiredFieldNotSetError as e:
        raise HTTPException(
            status_code=sc.HTTP_406_NOT_ACCEPTABLE, detail=lang(current_user).API.BOUGHTITEM.VALUE_MUST_BE_SET
        ) from e
    except BoughtItemAlreadyPlannedError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.CANNOT_CHANGE_PLANNED_ITEM
        ) from e
    except BoughtItemOfAnotherUserError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.CANNOT_CHANGE_OTHER_USER_ITEM
        ) from e
    except InsufficientPermissionsError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.UPDATE_NO_PERMISSION
        ) from e
    except ProjectInactiveError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.PROJECT_INACTIVE
        ) from e

    return updated_item


@router.put("/{item_id}/unit", response_model=BoughtItemSchema)
def update_bought_item_unit(
    *,
    db: Session = Depends(get_db),
    item_id: int,
    unit: str,
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """Updates the quantity of an item."""
    item = crud_bought_item.get(db, id=item_id)
    if not item:
        raise HTTPException(status_code=sc.HTTP_404_NOT_FOUND, detail=lang(current_user).API.BOUGHTITEM.ITEM_NOT_FOUND)

    try:
        updated_item = crud_bought_item.update_required_field(
            db, db_obj_user=current_user, db_obj_item=item, db_field=BoughtItemModel.unit, value=unit
        )
    except BoughtItemRequiredFieldNotSetError as e:
        raise HTTPException(
            status_code=sc.HTTP_406_NOT_ACCEPTABLE, detail=lang(current_user).API.BOUGHTITEM.VALUE_MUST_BE_SET
        ) from e
    except BoughtItemAlreadyPlannedError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.CANNOT_CHANGE_PLANNED_ITEM
        ) from e
    except BoughtItemOfAnotherUserError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.CANNOT_CHANGE_OTHER_USER_ITEM
        ) from e
    except InsufficientPermissionsError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.UPDATE_NO_PERMISSION
        ) from e
    except ProjectInactiveError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.PROJECT_INACTIVE
        ) from e

    return updated_item


@router.put("/{item_id}/partnumber", response_model=BoughtItemSchema)
def update_bought_item_partnumber(
    *,
    db: Session = Depends(get_db),
    item_id: int,
    partnumber: str,
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """Updates the partnumber of an item."""
    item = crud_bought_item.get(db, id=item_id)
    if not item:
        raise HTTPException(status_code=sc.HTTP_404_NOT_FOUND, detail=lang(current_user).API.BOUGHTITEM.ITEM_NOT_FOUND)

    try:
        updated_item = crud_bought_item.update_required_field(
            db, db_obj_user=current_user, db_obj_item=item, db_field=BoughtItemModel.partnumber, value=partnumber
        )
    except BoughtItemRequiredFieldNotSetError as e:
        raise HTTPException(
            status_code=sc.HTTP_406_NOT_ACCEPTABLE, detail=lang(current_user).API.BOUGHTITEM.VALUE_MUST_BE_SET
        ) from e
    except BoughtItemAlreadyPlannedError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.CANNOT_CHANGE_PLANNED_ITEM
        ) from e
    except BoughtItemOfAnotherUserError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.CANNOT_CHANGE_OTHER_USER_ITEM
        ) from e
    except InsufficientPermissionsError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.UPDATE_NO_PERMISSION
        ) from e
    except ProjectInactiveError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.PROJECT_INACTIVE
        ) from e

    return updated_item


@router.put("/{item_id}/order-number", response_model=BoughtItemSchema)
def update_bought_item_order_number(
    *,
    db: Session = Depends(get_db),
    item_id: int,
    order_number: str,
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """Updates the order number of an item."""
    item = crud_bought_item.get(db, id=item_id)
    if not item:
        raise HTTPException(status_code=sc.HTTP_404_NOT_FOUND, detail=lang(current_user).API.BOUGHTITEM.ITEM_NOT_FOUND)

    try:
        updated_item = crud_bought_item.update_required_field(
            db, db_obj_user=current_user, db_obj_item=item, db_field=BoughtItemModel.order_number, value=order_number
        )
    except BoughtItemRequiredFieldNotSetError as e:
        raise HTTPException(
            status_code=sc.HTTP_406_NOT_ACCEPTABLE, detail=lang(current_user).API.BOUGHTITEM.VALUE_MUST_BE_SET
        ) from e
    except BoughtItemAlreadyPlannedError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.CANNOT_CHANGE_PLANNED_ITEM
        ) from e
    except BoughtItemOfAnotherUserError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.CANNOT_CHANGE_OTHER_USER_ITEM
        ) from e
    except InsufficientPermissionsError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.UPDATE_NO_PERMISSION
        ) from e
    except ProjectInactiveError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.PROJECT_INACTIVE
        ) from e

    return updated_item


@router.put("/{item_id}/manufacturer", response_model=BoughtItemSchema)
def update_bought_item_manufacturer(
    *,
    db: Session = Depends(get_db),
    item_id: int,
    manufacturer: str,
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """Updates the manufacturer of an item."""
    item = crud_bought_item.get(db, id=item_id)
    if not item:
        raise HTTPException(status_code=sc.HTTP_404_NOT_FOUND, detail=lang(current_user).API.BOUGHTITEM.ITEM_NOT_FOUND)

    try:
        updated_item = crud_bought_item.update_required_field(
            db, db_obj_user=current_user, db_obj_item=item, db_field=BoughtItemModel.manufacturer, value=manufacturer
        )
    except BoughtItemRequiredFieldNotSetError as e:
        raise HTTPException(
            status_code=sc.HTTP_406_NOT_ACCEPTABLE, detail=lang(current_user).API.BOUGHTITEM.VALUE_MUST_BE_SET
        ) from e
    except BoughtItemAlreadyPlannedError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.CANNOT_CHANGE_PLANNED_ITEM
        ) from e
    except BoughtItemOfAnotherUserError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.CANNOT_CHANGE_OTHER_USER_ITEM
        ) from e
    except InsufficientPermissionsError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.UPDATE_NO_PERMISSION
        ) from e
    except ProjectInactiveError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.PROJECT_INACTIVE
        ) from e

    return updated_item


@router.put("/{item_id}/supplier", response_model=BoughtItemSchema)
def update_bought_item_supplier(
    *,
    db: Session = Depends(get_db),
    item_id: int,
    supplier: str,
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """Updates the supplier of an item."""
    item = crud_bought_item.get(db, id=item_id)
    if not item:
        raise HTTPException(status_code=sc.HTTP_404_NOT_FOUND, detail=lang(current_user).API.BOUGHTITEM.ITEM_NOT_FOUND)

    try:
        updated_item = crud_bought_item.update_field(
            db, db_obj_user=current_user, db_obj_item=item, db_field=BoughtItemModel.supplier, value=supplier
        )
    except BoughtItemAlreadyPlannedError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.CANNOT_CHANGE_PLANNED_ITEM
        ) from e
    except BoughtItemOfAnotherUserError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.CANNOT_CHANGE_OTHER_USER_ITEM
        ) from e
    except InsufficientPermissionsError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.UPDATE_NO_PERMISSION
        ) from e
    except ProjectInactiveError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.PROJECT_INACTIVE
        ) from e

    return updated_item


@router.put("/{item_id}/weblink", response_model=BoughtItemSchema)
def update_bought_item_weblink(
    *,
    db: Session = Depends(get_db),
    item_id: int,
    weblink: str,
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """Updates the weblink of an item."""
    item = crud_bought_item.get(db, id=item_id)
    if not item:
        raise HTTPException(status_code=sc.HTTP_404_NOT_FOUND, detail=lang(current_user).API.BOUGHTITEM.ITEM_NOT_FOUND)

    try:
        updated_item = crud_bought_item.update_field(
            db, db_obj_user=current_user, db_obj_item=item, db_field=BoughtItemModel.weblink, value=weblink
        )
    except BoughtItemAlreadyPlannedError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.CANNOT_CHANGE_PLANNED_ITEM
        ) from e
    except BoughtItemOfAnotherUserError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.CANNOT_CHANGE_OTHER_USER_ITEM
        ) from e
    except InsufficientPermissionsError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.UPDATE_NO_PERMISSION
        ) from e
    except ProjectInactiveError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.PROJECT_INACTIVE
        ) from e

    return updated_item


@router.put("/{item_id}/note-general", response_model=BoughtItemSchema)
def update_bought_item_note_general(
    *,
    db: Session = Depends(get_db),
    item_id: int,
    note: str,
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """Updates the general note of an item."""
    item = crud_bought_item.get(db, id=item_id)
    if not item:
        raise HTTPException(status_code=sc.HTTP_404_NOT_FOUND, detail=lang(current_user).API.BOUGHTITEM.ITEM_NOT_FOUND)

    try:
        updated_item = crud_bought_item.update_field(
            db, db_obj_user=current_user, db_obj_item=item, db_field=BoughtItemModel.note_general, value=note
        )
    except BoughtItemAlreadyPlannedError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.CANNOT_CHANGE_PLANNED_ITEM
        ) from e
    except BoughtItemOfAnotherUserError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.CANNOT_CHANGE_OTHER_USER_ITEM
        ) from e
    except InsufficientPermissionsError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.UPDATE_NO_PERMISSION
        ) from e
    except ProjectInactiveError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.PROJECT_INACTIVE
        ) from e

    return updated_item


@router.put("/{item_id}/note-supplier", response_model=BoughtItemSchema)
def update_bought_item_note_supplier(
    *,
    db: Session = Depends(get_db),
    item_id: int,
    note: str,
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """Updates the supplier note of an item."""
    item = crud_bought_item.get(db, id=item_id)
    if not item:
        raise HTTPException(status_code=sc.HTTP_404_NOT_FOUND, detail=lang(current_user).API.BOUGHTITEM.ITEM_NOT_FOUND)

    try:
        updated_item = crud_bought_item.update_field(
            db, db_obj_user=current_user, db_obj_item=item, db_field=BoughtItemModel.note_supplier, value=note
        )
    except BoughtItemAlreadyPlannedError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.CANNOT_CHANGE_PLANNED_ITEM
        ) from e
    except BoughtItemOfAnotherUserError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.CANNOT_CHANGE_OTHER_USER_ITEM
        ) from e
    except InsufficientPermissionsError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.UPDATE_NO_PERMISSION
        ) from e
    except ProjectInactiveError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.PROJECT_INACTIVE
        ) from e

    return updated_item


@router.put("/{item_id}/desired-delivery-date", response_model=BoughtItemSchema)
def update_bought_item_desired_delivery_date(
    *,
    db: Session = Depends(get_db),
    item_id: int,
    date: datetime.date,
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """Updates the desired delivery date of an item."""
    item = crud_bought_item.get(db, id=item_id)
    if not item:
        raise HTTPException(status_code=sc.HTTP_404_NOT_FOUND, detail=lang(current_user).API.BOUGHTITEM.ITEM_NOT_FOUND)

    try:
        updated_item = crud_bought_item.update_field(
            db, db_obj_user=current_user, db_obj_item=item, db_field=BoughtItemModel.desired_delivery_date, value=date
        )
    except BoughtItemAlreadyPlannedError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.CANNOT_CHANGE_PLANNED_ITEM
        ) from e
    except BoughtItemOfAnotherUserError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.CANNOT_CHANGE_OTHER_USER_ITEM
        ) from e
    except InsufficientPermissionsError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.UPDATE_NO_PERMISSION
        ) from e
    except ProjectInactiveError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.PROJECT_INACTIVE
        ) from e

    return updated_item


@router.put("/{item_id}/expected-delivery-date", response_model=BoughtItemSchema)
def update_bought_item_expected_delivery_date(
    *,
    db: Session = Depends(get_db),
    item_id: int,
    date: datetime.date,
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """Updates the expected delivery date of an item."""
    item = crud_bought_item.get(db, id=item_id)
    if not item:
        raise HTTPException(status_code=sc.HTTP_404_NOT_FOUND, detail=lang(current_user).API.BOUGHTITEM.ITEM_NOT_FOUND)

    try:
        updated_item = crud_bought_item.update_field(
            db, db_obj_user=current_user, db_obj_item=item, db_field=BoughtItemModel.expected_delivery_date, value=date
        )
    except BoughtItemAlreadyPlannedError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.CANNOT_CHANGE_PLANNED_ITEM
        ) from e
    except BoughtItemOfAnotherUserError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.CANNOT_CHANGE_OTHER_USER_ITEM
        ) from e
    except InsufficientPermissionsError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.UPDATE_NO_PERMISSION
        ) from e
    except ProjectInactiveError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.PROJECT_INACTIVE
        ) from e

    return updated_item


@router.put("/{item_id}/storage", response_model=BoughtItemSchema)
def update_bought_item_storage(
    *,
    db: Session = Depends(get_db),
    item_id: int,
    storage_place: str,
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """Updates the storage of an item."""
    item = crud_bought_item.get(db, id=item_id)
    if not item:
        raise HTTPException(status_code=sc.HTTP_404_NOT_FOUND, detail=lang(current_user).API.BOUGHTITEM.ITEM_NOT_FOUND)

    try:
        updated_item = crud_bought_item.update_field(
            db, db_obj_user=current_user, db_obj_item=item, db_field=BoughtItemModel.storage_place, value=storage_place
        )
    except BoughtItemAlreadyPlannedError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.CANNOT_CHANGE_PLANNED_ITEM
        ) from e
    except BoughtItemOfAnotherUserError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.CANNOT_CHANGE_OTHER_USER_ITEM
        ) from e
    except InsufficientPermissionsError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.UPDATE_NO_PERMISSION
        ) from e
    except ProjectInactiveError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.PROJECT_INACTIVE
        ) from e

    return updated_item


@router.delete("/{item_id}", response_model=BoughtItemSchema)
def delete_bought_item(
    *,
    db: Session = Depends(get_db),
    item_id: int,
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """Delete an item."""
    item = crud_bought_item.get(db, id=item_id)
    if not item:
        raise HTTPException(status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.ITEM_NOT_FOUND)
    try:
        deleted_item = crud_bought_item.delete(db, db_obj_item=item, db_obj_user=current_user)
    except BoughtItemAlreadyPlannedError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.CANNOT_DELETE_PLANNED_ITEM
        ) from e
    except BoughtItemOfAnotherUserError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.CANNOT_DELETE_OTHER_USER_ITEM
        ) from e
    except InsufficientPermissionsError as e:
        raise HTTPException(
            status_code=sc.HTTP_403_FORBIDDEN, detail=lang(current_user).API.BOUGHTITEM.DELETE_NO_PERMISSION
        ) from e

    return deleted_item
