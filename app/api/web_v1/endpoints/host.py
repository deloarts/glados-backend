"""
    Handles all routes to the host-resource.
"""

from dataclasses import asdict
from datetime import datetime
from typing import Any

from api import deps
from config import cfg
from const import VERSION
from fastapi.param_functions import Depends
from fastapi.routing import APIRouter
from schemas import schema_host

router = APIRouter()


@router.get("/version", response_model=schema_host.HostVersion)
def get_host_version(verified: bool = Depends(deps.verify_token)) -> Any:
    """Returns server version."""
    return {"version": VERSION}


@router.get("/time", response_model=schema_host.HostTime)
def get_host_time(verified: bool = Depends(deps.verify_token)) -> Any:
    """Returns server time."""
    return {"now": datetime.now(), "timezone": cfg.locale.tz}


@router.get("/config", response_model=schema_host.HostConfig)
def get_host_config(
    verified: bool = Depends(deps.verify_token_adminuser),
) -> Any:
    """Returns vulnerable host information."""
    return {"now": datetime.now(), "config": cfg}


@router.get(
    "/config/items/bought/status",
    response_model=schema_host.HostConfigItemsBoughtStatus,
)
def get_host_config_items_bought_status(
    verified: bool = Depends(deps.verify_token),
) -> Any:
    """Returns available bought items status."""
    return cfg.items.bought.status


@router.get(
    "/config/items/bought/units",
    response_model=schema_host.HostConfigItemsBoughtUnits,
)
def get_host_config_items_bought_units(
    verified: bool = Depends(deps.verify_token),
) -> Any:
    """Returns available bought items units."""
    return cfg.items.bought.units
