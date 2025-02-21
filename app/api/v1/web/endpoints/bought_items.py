"""
    Handles all routes to the bought-items-resource web-API.
"""

# pylint: disable=R0913
# pylint: disable=R0914

import datetime
from enum import Enum
from pathlib import Path
from typing import Any
from typing import List
from typing import Literal

from api.deps import get_current_active_user
from api.deps import verify_token
from api.responses import HTTP_401_RESPONSE
from api.responses import ResponseModelDetail
from api.schemas import PageSchema
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


class RequiredFieldName(str, Enum):
    partnumber = "partnumber"
    order_number = "order-number"
    manufacturer = "manufacturer"


class OptionalFieldName(str, Enum):
    supplier = "supplier"
    group_1 = "group-1"
    weblink = "weblink"
    note_general = "note-general"
    note_supplier = "note-supplier"
    storage_place = "storage-place"


class DateFieldName(str, Enum):
    desired_delivery_date = "desired-delivery-date"
    expected_delivery_date = "expected-delivery-date"


@router.get(
    "/",
    response_model=PageSchema[BoughtItemSchema],
    responses={**HTTP_401_RESPONSE},
)
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
    count, bought_items = crud_bought_item.get_multi(**kwargs)
    return PageSchema(
        items=[BoughtItemSchema.model_validate(i) for i in bought_items],
        total=count,
        limit=limit if limit else count,
        skip=skip if skip else 0,
    )


@router.get(
    "/excel",
    response_class=FileResponse,
    responses={
        **HTTP_401_RESPONSE,
        sc.HTTP_403_FORBIDDEN: {"model": ResponseModelDetail, "description": "EXCEL generation failed"},
    },
)
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

    count, items = crud_bought_item.get_multi(**kwargs)
    export_handler = BoughtItemExcelExport(data=items)
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


@router.get(
    "/excel-template",
    response_class=FileResponse,
    responses={
        **HTTP_401_RESPONSE,
        sc.HTTP_404_NOT_FOUND: {"model": ResponseModelDetail, "description": "Template not found"},
    },
)
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


@router.get(
    "/{item_id}",
    response_model=BoughtItemSchema,
    responses={
        **HTTP_401_RESPONSE,
        sc.HTTP_404_NOT_FOUND: {"model": ResponseModelDetail, "description": "Item not found"},
    },
)
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


@router.get(
    "/{item_id}/changelog",
    response_model=List[str],
    responses={
        **HTTP_401_RESPONSE,
        sc.HTTP_404_NOT_FOUND: {"model": ResponseModelDetail, "description": "Item not found"},
    },
)
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


@router.post(
    "/validate",
    response_model=BoughtItemCreateWebSchema,
    responses={**HTTP_401_RESPONSE},
)
def validate_bought_item(
    *, obj_in: BoughtItemCreateWebSchema, current_user: UserModel = Depends(get_current_active_user)
) -> Any:
    return obj_in


@router.post(
    "/",
    response_model=BoughtItemSchema,
    responses={
        **HTTP_401_RESPONSE,
        sc.HTTP_403_FORBIDDEN: {
            "model": ResponseModelDetail,
            "description": "User has no permission or project is inactive",
        },
        sc.HTTP_404_NOT_FOUND: {"model": ResponseModelDetail, "description": "Project not found"},
    },
)
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


@router.post(
    "/excel",
    response_model=List[BoughtItemCreateWebSchema] | List[BoughtItemSchema] | List[dict],
    responses={
        **HTTP_401_RESPONSE,
        sc.HTTP_404_NOT_FOUND: {"model": ResponseModelDetail, "description": "EXCEL header not found in file"},
        sc.HTTP_406_NOT_ACCEPTABLE: {"model": ResponseModelDetail, "description": "EXCEL header invalid in file"},
    },
)
def create_bought_items_from_excel(
    *,
    db: Session = Depends(get_db),
    force_create: bool = False,
    skip_validation: bool = False,
    file: UploadFile,
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """ """
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


@router.put(
    "/{item_id}",
    response_model=BoughtItemSchema,
    responses={
        **HTTP_401_RESPONSE,
        sc.HTTP_403_FORBIDDEN: {
            "model": ResponseModelDetail,
            "description": (
                "Forbidden action\n"
                " - Project is inactive\n"
                " - User has no permission\n"
                " - Item is already planned\n"
                " - Item is from another user"
            ),
        },
        sc.HTTP_404_NOT_FOUND: {"model": ResponseModelDetail, "description": "Item or project not found"},
    },
)
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


@router.put(
    "/{item_id}/status",
    response_model=BoughtItemSchema,
    responses={
        **HTTP_401_RESPONSE,
        sc.HTTP_403_FORBIDDEN: {
            "model": ResponseModelDetail,
            "description": (
                "Forbidden action\n"
                " - Status is unknown\n"
                " - Cannot change to 'open'\n"
                " - User has no permission\n"
                " - Item is already planned\n"
                " - Item is from another user"
            ),
        },
        sc.HTTP_404_NOT_FOUND: {"model": ResponseModelDetail, "description": "Item not found"},
    },
)
def update_bought_item_status(
    *,
    db: Session = Depends(get_db),
    item_id: int,
    status: Literal[*cfg.items.bought.status.values],  # type: ignore
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


@router.put(
    "/{item_id}/project",
    response_model=BoughtItemSchema,
    responses={
        **HTTP_401_RESPONSE,
        sc.HTTP_403_FORBIDDEN: {
            "model": ResponseModelDetail,
            "description": (
                "Forbidden action\n"
                " - Project is inactive\n"
                " - User has no permission\n"
                " - Item is already planned\n"
                " - Item is from another user"
            ),
        },
        sc.HTTP_404_NOT_FOUND: {"model": ResponseModelDetail, "description": "Item or project not found"},
    },
)
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


@router.put(
    "/{item_id}/unit",
    response_model=BoughtItemSchema,
    responses={
        **HTTP_401_RESPONSE,
        sc.HTTP_403_FORBIDDEN: {
            "model": ResponseModelDetail,
            "description": (
                "Forbidden action\n"
                " - Project is inactive\n"
                " - User has no permission\n"
                " - Item is already planned\n"
                " - Item is from another user"
            ),
        },
        sc.HTTP_404_NOT_FOUND: {"model": ResponseModelDetail, "description": "Item not found"},
        sc.HTTP_406_NOT_ACCEPTABLE: {"model": ResponseModelDetail, "description": "Value is not set"},
    },
)
def update_bought_item_unit(
    *,
    db: Session = Depends(get_db),
    item_id: int,
    unit: Literal[*cfg.items.bought.units.values],  # type: ignore
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """Updates the unit of an item. The value must be set."""
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


@router.put(
    "/{item_id}/quantity",
    response_model=BoughtItemSchema,
    responses={
        **HTTP_401_RESPONSE,
        sc.HTTP_403_FORBIDDEN: {
            "model": ResponseModelDetail,
            "description": (
                "Forbidden action\n"
                " - Project is inactive\n"
                " - User has no permission\n"
                " - Item is already planned\n"
                " - Item is from another user"
            ),
        },
        sc.HTTP_404_NOT_FOUND: {"model": ResponseModelDetail, "description": "Item not found"},
        sc.HTTP_406_NOT_ACCEPTABLE: {"model": ResponseModelDetail, "description": "Value is not set"},
    },
)
def update_bought_item_quantity(
    *,
    db: Session = Depends(get_db),
    item_id: int,
    quantity: int | float,
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """Updates the quantity of an item. The value must be set."""
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


@router.put(
    "/{item_id}/field/required/{field_name}",
    response_model=BoughtItemSchema,
    responses={
        **HTTP_401_RESPONSE,
        sc.HTTP_403_FORBIDDEN: {
            "model": ResponseModelDetail,
            "description": (
                "Forbidden action\n"
                " - Project is inactive\n"
                " - User has no permission\n"
                " - Item is already planned\n"
                " - Item is from another user"
            ),
        },
        sc.HTTP_404_NOT_FOUND: {"model": ResponseModelDetail, "description": "Field not supported"},
        sc.HTTP_405_METHOD_NOT_ALLOWED: {"model": ResponseModelDetail, "description": "Item not found"},
        sc.HTTP_406_NOT_ACCEPTABLE: {"model": ResponseModelDetail, "description": "Value is not set"},
    },
)
def update_bought_item_required_field(
    *,
    db: Session = Depends(get_db),
    item_id: int,
    field_name: RequiredFieldName,
    value: str,
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """Updates a required field an item. The value must be set."""
    if field_name is RequiredFieldName.partnumber:
        db_field = BoughtItemModel.partnumber
    elif field_name is RequiredFieldName.order_number:
        db_field = BoughtItemModel.order_number
    elif field_name is RequiredFieldName.manufacturer:
        db_field = BoughtItemModel.manufacturer
    else:
        raise HTTPException(status_code=sc.HTTP_405_METHOD_NOT_ALLOWED, detail="Field not supported")

    item = crud_bought_item.get(db, id=item_id)
    if not item:
        raise HTTPException(status_code=sc.HTTP_404_NOT_FOUND, detail=lang(current_user).API.BOUGHTITEM.ITEM_NOT_FOUND)

    try:
        updated_item = crud_bought_item.update_required_field(
            db, db_obj_user=current_user, db_obj_item=item, db_field=db_field, value=value
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


@router.put(
    "/{item_id}/field/optional/{field_name}",
    response_model=BoughtItemSchema,
    responses={
        **HTTP_401_RESPONSE,
        sc.HTTP_403_FORBIDDEN: {
            "model": ResponseModelDetail,
            "description": (
                "Forbidden action\n"
                " - Project is inactive\n"
                " - User has no permission\n"
                " - Item is already planned\n"
                " - Item is from another user"
            ),
        },
        sc.HTTP_404_NOT_FOUND: {"model": ResponseModelDetail, "description": "Field not supported"},
        sc.HTTP_405_METHOD_NOT_ALLOWED: {"model": ResponseModelDetail, "description": "Item not found"},
    },
)
def update_bought_item_optional_field(
    *,
    db: Session = Depends(get_db),
    item_id: int,
    field_name: OptionalFieldName,
    value: str,
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """Updates an optional field an item. The value can be empty."""
    if field_name is OptionalFieldName.supplier:
        db_field = BoughtItemModel.supplier
    elif field_name is OptionalFieldName.group_1:
        db_field = BoughtItemModel.group_1
    elif field_name is OptionalFieldName.note_general:
        db_field = BoughtItemModel.note_general
    elif field_name is OptionalFieldName.note_supplier:
        db_field = BoughtItemModel.note_supplier
    elif field_name is OptionalFieldName.weblink:
        db_field = BoughtItemModel.weblink
    elif field_name is OptionalFieldName.storage_place:
        db_field = BoughtItemModel.storage_place
    else:
        raise HTTPException(status_code=sc.HTTP_405_METHOD_NOT_ALLOWED, detail="Field not supported")

    item = crud_bought_item.get(db, id=item_id)
    if not item:
        raise HTTPException(status_code=sc.HTTP_404_NOT_FOUND, detail=lang(current_user).API.BOUGHTITEM.ITEM_NOT_FOUND)

    try:
        updated_item = crud_bought_item.update_field(
            db, db_obj_user=current_user, db_obj_item=item, db_field=db_field, value=value
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


@router.put(
    "/{item_id}/field/date/{field_name}",
    response_model=BoughtItemSchema,
    responses={
        **HTTP_401_RESPONSE,
        sc.HTTP_403_FORBIDDEN: {
            "model": ResponseModelDetail,
            "description": (
                "Forbidden action\n"
                " - Project is inactive\n"
                " - User has no permission\n"
                " - Item is already planned\n"
                " - Item is from another user"
            ),
        },
        sc.HTTP_404_NOT_FOUND: {"model": ResponseModelDetail, "description": "Field not supported"},
        sc.HTTP_405_METHOD_NOT_ALLOWED: {"model": ResponseModelDetail, "description": "Item not found"},
    },
)
def update_bought_item_date_field(
    *,
    db: Session = Depends(get_db),
    item_id: int,
    field_name: DateFieldName,
    value: datetime.date,
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """Updates a date field an item."""
    if field_name is DateFieldName.desired_delivery_date:
        db_field = BoughtItemModel.desired_delivery_date
    elif field_name is DateFieldName.expected_delivery_date:
        db_field = BoughtItemModel.expected_delivery_date
    else:
        raise HTTPException(status_code=sc.HTTP_405_METHOD_NOT_ALLOWED, detail="Field not supported")

    item = crud_bought_item.get(db, id=item_id)
    if not item:
        raise HTTPException(status_code=sc.HTTP_404_NOT_FOUND, detail=lang(current_user).API.BOUGHTITEM.ITEM_NOT_FOUND)

    try:
        updated_item = crud_bought_item.update_field(
            db, db_obj_user=current_user, db_obj_item=item, db_field=db_field, value=value
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


@router.delete(
    "/{item_id}",
    response_model=BoughtItemSchema,
    responses={
        **HTTP_401_RESPONSE,
        sc.HTTP_403_FORBIDDEN: {
            "model": ResponseModelDetail,
            "description": (
                "Forbidden action\n"
                " - User has no permission\n"
                " - Item is already planned\n"
                " - Item is from another user"
            ),
        },
        sc.HTTP_405_METHOD_NOT_ALLOWED: {"model": ResponseModelDetail, "description": "Item not found"},
    },
)
def delete_bought_item(
    *,
    db: Session = Depends(get_db),
    item_id: int,
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """Delete an item."""
    item = crud_bought_item.get(db, id=item_id)
    if not item:
        raise HTTPException(status_code=sc.HTTP_404_NOT_FOUND, detail=lang(current_user).API.BOUGHTITEM.ITEM_NOT_FOUND)

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
