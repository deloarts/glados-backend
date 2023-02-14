"""
    Handles all routes to the logs-resource.
"""

from typing import Any

from api import deps
from api.worker import gather_logs, read_logfile
from fastapi import status
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends
from fastapi.routing import APIRouter
from starlette.requests import Request

router = APIRouter()


@router.get("/", response_model=list)
# @whitelist
def get_logs(
    request: Request, verified: bool = Depends(deps.verify_token_superuser)
) -> Any:
    """Returns a list all log files."""
    log_files = gather_logs()
    return log_files


@router.get("/{logfile}", response_model=list)
# @whitelist
def get_log(
    request: Request,
    logfile: str,
    verified: bool = Depends(deps.verify_token_superuser),
) -> Any:
    """Returns the content of a given logfile as a list."""
    file_content = read_logfile(logfile)
    if file_content:
        return file_content
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="file not found")
