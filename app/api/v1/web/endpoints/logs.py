"""
    Handles all routes to the logs-resource.
"""

from typing import Any

from api.deps import get_current_active_adminuser
from db.models import UserModel
from fastapi import status
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends
from fastapi.routing import APIRouter
from locales import lang
from starlette.requests import Request
from utilities.log_files import gather_logs
from utilities.log_files import read_logfile

router = APIRouter()


@router.get("/", response_model=list)
def get_logs(request: Request, current_user: UserModel = Depends(get_current_active_adminuser)) -> Any:
    """Returns a list all log files."""
    log_files = gather_logs()
    return log_files


@router.get("/{logfile}", response_model=list)
def get_log(
    request: Request,
    logfile: str,
    current_user: UserModel = Depends(get_current_active_adminuser),
) -> Any:
    """Returns the content of a given logfile as a list."""
    file_content = read_logfile(logfile)
    if file_content:
        return file_content
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=lang(current_user).API.LOGS.FILE_NOT_FOUND)
