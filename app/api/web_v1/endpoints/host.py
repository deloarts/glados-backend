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
from utilities.disc_space import get_disc_space
from utilities.system import get_hostname
from utilities.system import get_os

router = APIRouter()


@router.get("/version", response_model=schema_host.HostVersion)
def get_host_version(verified: bool = Depends(deps.verify_token)) -> Any:
    """Returns server version."""
    return {"version": VERSION}


@router.get("/time", response_model=schema_host.HostTime)
def get_host_time(verified: bool = Depends(deps.verify_token)) -> Any:
    """Returns server time."""
    return {"now": datetime.now(), "timezone": cfg.locale.tz}


@router.get("/info", response_model=schema_host.HostInfo)
def get_host_info(
    verified: bool = Depends(deps.verify_token_adminuser),
) -> Any:
    """Returns vulnerable host information."""
    return {
        "now": datetime.now(),
        "version": VERSION,
        "os": get_os(),
        "hostname": get_hostname(),
        "disc_space": get_disc_space(),
    }


@router.get("/config", response_model=schema_host.HostConfig)
def get_host_config(
    verified: bool = Depends(deps.verify_token_adminuser),
) -> Any:
    """Returns vulnerable host configuration."""
    return {
        "now": datetime.now(),
        "config": cfg,
    }


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
