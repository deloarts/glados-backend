"""
    Handles all routes to the tools-resource.
"""

from typing import Any

from api import deps
from fastapi import status
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends
from fastapi.routing import APIRouter

router = APIRouter()


@router.post("/2d/solve")
def post_2d_solve(verified: bool = Depends(deps.verify_token)) -> Any:
    """DEPRECATED! Solves the two dimensional stock cutting problem. Returns the result of the solver."""

    raise HTTPException(status_code=status.HTTP_410_GONE, detail="This feature is not available in this release")


@router.post("/2d/generate")
def post_2d_generate(verified: bool = Depends(deps.verify_token)) -> Any:
    """DEPRECATED! Returns a pdf or svg file for the given result of the 2d stock cutting problem."""

    raise HTTPException(status_code=status.HTTP_410_GONE, detail="This feature is not available in this release")
