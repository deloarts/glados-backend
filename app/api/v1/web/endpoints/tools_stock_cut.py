"""
    Handles all routes to the tools-resource.
"""

from typing import Any

from api import deps
from config import cfg
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends
from fastapi.routing import APIRouter
from tools.stock_cut.models.model_job import Job
from tools.stock_cut.models.model_result import Result
from tools.stock_cut.solver import distribute

router = APIRouter()


@router.post("/solve", response_model=Result)
def post_solve(
    job: Job,
    verified: bool = Depends(deps.verify_token),
) -> Any:
    """Solves the stock cutting problem."""

    try:
        job.assert_valid()
    except ValueError as e:
        raise HTTPException(
            status_code=406,
            detail=str(e),
        )

    try:
        solved: Result = distribute(job)
    except OverflowError as e:
        raise HTTPException(
            status_code=507,
            detail=str(e),
        )

    try:
        solved.assert_valid()
    except ValueError as e:
        raise HTTPException(
            status_code=507,
            detail=str(e),
        )

    return solved
