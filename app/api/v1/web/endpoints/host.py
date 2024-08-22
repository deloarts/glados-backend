"""
    Handles all routes to the host-resource.
"""

from datetime import datetime
from typing import Any

from api import deps
from api.deps import get_current_active_adminuser
from api.schemas.host import HostConfigItemsBoughtFilterAddSchema
from api.schemas.host import HostConfigItemsBoughtFilterSchema
from api.schemas.host import HostConfigItemsBoughtStatusSchema
from api.schemas.host import HostConfigItemsBoughtUnitsSchema
from api.schemas.host import HostConfigSchema
from api.schemas.host import HostInfoSchema
from api.schemas.host import HostTimeSchema
from api.schemas.host import HostVersionSchema
from config import cfg
from const import VERSION
from db.models import UserModel
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends
from fastapi.routing import APIRouter
from multilog import log
from utilities.config_editor.bought_items import bought_item_config
from utilities.disc_space import get_disc_space
from utilities.system import get_hostname
from utilities.system import get_os

router = APIRouter()


@router.get("/version", response_model=HostVersionSchema)
def get_host_version(verified: bool = Depends(deps.verify_token)) -> Any:
    """Returns server version."""
    return {"version": VERSION}


@router.get("/time", response_model=HostTimeSchema)
def get_host_time(verified: bool = Depends(deps.verify_token)) -> Any:
    """Returns server time."""
    return {"now": datetime.now(), "timezone": cfg.locale.tz}


@router.get("/info", response_model=HostInfoSchema)
def get_host_info(verified: bool = Depends(deps.verify_token_adminuser)) -> Any:
    """Returns vulnerable host information."""
    return {
        "now": datetime.now(),
        "version": VERSION,
        "os": get_os(),
        "hostname": get_hostname(),
        "disc_space": get_disc_space(),
    }


@router.get("/config", response_model=HostConfigSchema)
def get_host_config(verified: bool = Depends(deps.verify_token_adminuser)) -> Any:
    """Returns vulnerable host configuration."""
    return {
        "now": datetime.now(),
        "config": cfg,
    }


@router.get("/config/items/bought/status", response_model=HostConfigItemsBoughtStatusSchema)
def get_host_config_items_bought_status(verified: bool = Depends(deps.verify_token)) -> Any:
    """Returns available bought items status."""
    return cfg.items.bought.status


@router.get("/config/items/bought/units", response_model=HostConfigItemsBoughtUnitsSchema)
def get_host_config_items_bought_units(verified: bool = Depends(deps.verify_token)) -> Any:
    """Returns available bought items units."""
    return cfg.items.bought.units


@router.get("/config/items/bought/filters", response_model=HostConfigItemsBoughtFilterSchema)
def get_host_config_items_bought_filter(verified: bool = Depends(deps.verify_token)) -> Any:
    """Returns available bought items filters."""
    return bought_item_config.filters


@router.get("/config/items/bought/filters/default", response_model=HostConfigItemsBoughtFilterSchema)
def get_host_config_items_bought_filter_default(verified: bool = Depends(deps.verify_token)) -> Any:
    """Returns the default bought items filter."""
    return HostConfigItemsBoughtFilterSchema()


@router.post("/config/items/bought/filters/{filter_name}", response_model=HostConfigItemsBoughtFilterSchema)
def post_host_config_items_bought_filter(
    filter_name: str,
    filter_in: HostConfigItemsBoughtFilterAddSchema,
    current_user: UserModel = Depends(get_current_active_adminuser),
) -> Any:
    """Saves the given filter for bought items."""
    if filter_name in bought_item_config.filters:
        raise HTTPException(
            status_code=406,
            detail="A configuration with this name already exists in the system.",
        )
    bought_item_config.add_filter(name=filter_name, filter=filter_in)
    log.info(
        f"User {current_user.username} ({current_user.full_name}, ID={current_user.id}) "
        f"added a bought item filter: {filter_name}"
    )
    return bought_item_config.filters


@router.put("/config/items/bought/filters/{filter_name}", response_model=HostConfigItemsBoughtFilterSchema)
def update_host_config_items_bought_filter(
    filter_name: str,
    filter_in: HostConfigItemsBoughtFilterAddSchema,
    current_user: UserModel = Depends(get_current_active_adminuser),
) -> Any:
    """Updates the given filter for bought items."""
    if filter_name not in bought_item_config.filters:
        raise HTTPException(
            status_code=404,
            detail=f"Configuration {filter_name} not found.",
        )
    bought_item_config.add_filter(name=filter_name, filter=filter_in)
    log.info(
        f"User {current_user.username} ({current_user.full_name}, ID={current_user.id}) "
        f"updated a bought item filter: {filter_name!r}"
    )
    return bought_item_config.filters


@router.delete("/config/items/bought/filters/{filter_name}", response_model=HostConfigItemsBoughtFilterSchema)
def delete_host_config_items_bought_filter(
    filter_name: str, current_user: UserModel = Depends(get_current_active_adminuser)
) -> Any:
    """Deletes the given filter for bought items."""
    if filter_name not in bought_item_config.filters:
        raise HTTPException(
            status_code=404,
            detail=f"Configuration {filter_name} not found.",
        )
    bought_item_config.remove_filter(name=filter_name)
    log.info(
        f"User {current_user.username} ({current_user.full_name}, ID={current_user.id}) "
        f"deleted a bought item filter: {filter_name!r}"
    )
    return bought_item_config.filters
