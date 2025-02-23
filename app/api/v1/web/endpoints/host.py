"""
    Handles all routes to the host-resource.
"""

from copy import deepcopy
from dataclasses import asdict
from datetime import datetime
from typing import Any
from typing import Dict

from api import deps
from api.deps import get_current_active_adminuser
from api.responses import HTTP_401_RESPONSE
from api.responses import ResponseModelDetail
from api.schemas.host import HostConfigItemsBoughtFilterAddSchema
from api.schemas.host import HostConfigItemsBoughtFilterSchema
from api.schemas.host import HostConfigItemsBoughtStatusSchema
from api.schemas.host import HostConfigItemsBoughtUnitsSchema
from api.schemas.host import HostConfigMailingSchema
from api.schemas.host import HostConfigSchema
from api.schemas.host import HostInfoSchema
from api.schemas.host import HostTimeSchema
from api.schemas.host import HostVersionSchema
from config import Config
from config import ConfigMailing
from config import cfg
from const import VERSION
from db.models import UserModel
from fastapi import status
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends
from fastapi.routing import APIRouter
from locales import lang
from mail.send import send_test_mail
from multilog import log
from pydantic import EmailStr
from utilities.config_editor.bought_items import bought_item_config
from utilities.disc_space import get_disc_space
from utilities.system import get_hostname
from utilities.system import get_os

router = APIRouter()


@router.get(
    "/version",
    response_model=HostVersionSchema,
    responses={**HTTP_401_RESPONSE},
)
def get_host_version(verified: bool = Depends(deps.verify_token)) -> Any:
    """Returns server version."""
    return HostVersionSchema(version=VERSION)


@router.get(
    "/time",
    response_model=HostTimeSchema,
    responses={**HTTP_401_RESPONSE},
)
def get_host_time(verified: bool = Depends(deps.verify_token)) -> Any:
    """Returns server time."""
    return HostTimeSchema(now=datetime.now(), timezone=cfg.locale.tz)


@router.get(
    "/info",
    response_model=HostInfoSchema,
    responses={**HTTP_401_RESPONSE},
)
def get_host_info(verified: bool = Depends(deps.verify_token_adminuser)) -> Any:
    """Returns vulnerable host information."""
    return HostInfoSchema(
        now=datetime.now(), version=VERSION, os=get_os(), hostname=get_hostname(), disc_space=get_disc_space()
    )


@router.get(
    "/config",
    response_model=HostConfigSchema,
    responses={**HTTP_401_RESPONSE},
)
def get_host_config(verified: bool = Depends(deps.verify_token_adminuser)) -> Any:
    """Returns vulnerable host configuration."""
    cfg_copy = asdict(deepcopy(cfg))
    cfg_copy["mailing"]["password"] = "********"
    cfg_copy["init"]["password"] = "********"
    return HostConfigSchema(now=datetime.now(), config=Config(**cfg_copy))


@router.get(
    "/config/mailing",
    response_model=HostConfigMailingSchema,
    responses={**HTTP_401_RESPONSE},
)
def get_host_config_mailing(verified: bool = Depends(deps.verify_token_adminuser)) -> Any:
    """Returns mailing configuration."""
    enabled = all([cfg.mailing.server, cfg.mailing.port, cfg.mailing.account, cfg.mailing.password])
    cfg_copy = asdict(deepcopy(cfg.mailing))
    cfg_copy["password"] = "********"
    return HostConfigMailingSchema(enabled=enabled, config=ConfigMailing(**cfg_copy))


@router.post(
    "/config/mailing/test",
    response_model=HostConfigMailingSchema,
    responses={**HTTP_401_RESPONSE},
)
def post_send_test_mail(receiver: EmailStr, verified: bool = Depends(deps.verify_token_adminuser)) -> Any:
    send_test_mail(receiver_mail=receiver)
    return get_host_config_mailing(verified=verified)


@router.get(
    "/config/items/bought/status",
    response_model=HostConfigItemsBoughtStatusSchema,
    responses={**HTTP_401_RESPONSE},
)
def get_host_config_items_bought_status(verified: bool = Depends(deps.verify_token)) -> Any:
    """Returns available bought items status."""
    return cfg.items.bought.status


@router.get(
    "/config/items/bought/units",
    response_model=HostConfigItemsBoughtUnitsSchema,
    responses={**HTTP_401_RESPONSE},
)
def get_host_config_items_bought_units(verified: bool = Depends(deps.verify_token)) -> Any:
    """Returns available bought items units."""
    return cfg.items.bought.units


@router.get(
    "/config/items/bought/filters",
    response_model=Dict[str, HostConfigItemsBoughtFilterSchema],
    responses={**HTTP_401_RESPONSE},
)
def get_host_config_items_bought_filter(verified: bool = Depends(deps.verify_token)) -> Any:
    """Returns available bought items filters."""
    return bought_item_config.filters


@router.get(
    "/config/items/bought/filters/default",
    response_model=HostConfigItemsBoughtFilterSchema,
    responses={**HTTP_401_RESPONSE},
)
def get_host_config_items_bought_filter_default(verified: bool = Depends(deps.verify_token)) -> Any:
    """Returns the default bought items filter."""
    return HostConfigItemsBoughtFilterSchema()


@router.post(
    "/config/items/bought/filters/{filter_name}",
    response_model=Dict[str, HostConfigItemsBoughtFilterSchema],
    responses={
        **HTTP_401_RESPONSE,
        status.HTTP_406_NOT_ACCEPTABLE: {"model": ResponseModelDetail, "description": "Configuration exists"},
    },
)
def post_host_config_items_bought_filter(
    filter_name: str,
    filter_in: HostConfigItemsBoughtFilterAddSchema,
    current_user: UserModel = Depends(get_current_active_adminuser),
) -> Any:
    """Saves the given filter for bought items."""
    if filter_name in bought_item_config.filters:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=lang(current_user).API.HOST.CONFIGURATION_ALREADY_EXISTS,
        )
    bought_item_config.add_filter(name=filter_name, filter=filter_in)
    log.info(
        f"User {current_user.username} ({current_user.full_name}, ID={current_user.id}) "
        f"added a bought item filter: {filter_name}"
    )
    return bought_item_config.filters


@router.put(
    "/config/items/bought/filters/{filter_name}",
    response_model=Dict[str, HostConfigItemsBoughtFilterSchema],
    responses={
        **HTTP_401_RESPONSE,
        status.HTTP_404_NOT_FOUND: {"model": ResponseModelDetail, "description": "Configuration not found"},
    },
)
def update_host_config_items_bought_filter(
    filter_name: str,
    filter_in: HostConfigItemsBoughtFilterAddSchema,
    current_user: UserModel = Depends(get_current_active_adminuser),
) -> Any:
    """Updates the given filter for bought items."""
    if filter_name not in bought_item_config.filters:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=lang(current_user).API.HOST.CONFIGURATION_NOT_FOUND,
        )
    bought_item_config.add_filter(name=filter_name, filter=filter_in)
    log.info(
        f"User {current_user.username} ({current_user.full_name}, ID={current_user.id}) "
        f"updated a bought item filter: {filter_name!r}"
    )
    return bought_item_config.filters


@router.delete(
    "/config/items/bought/filters/{filter_name}",
    response_model=Dict[str, HostConfigItemsBoughtFilterSchema],
    responses={
        **HTTP_401_RESPONSE,
        status.HTTP_404_NOT_FOUND: {"model": ResponseModelDetail, "description": "Configuration not found"},
    },
)
def delete_host_config_items_bought_filter(
    filter_name: str, current_user: UserModel = Depends(get_current_active_adminuser)
) -> Any:
    """Deletes the given filter for bought items."""
    if filter_name not in bought_item_config.filters:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=lang(current_user).API.HOST.CONFIGURATION_NOT_FOUND,
        )
    bought_item_config.remove_filter(name=filter_name)
    log.info(
        f"User {current_user.username} ({current_user.full_name}, ID={current_user.id}) "
        f"deleted a bought item filter: {filter_name!r}"
    )
    return bought_item_config.filters
