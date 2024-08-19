"""
    Handles all routes to the tools-resource.
"""

from typing import Any

from api import deps
from api.schemas import schema_stock_cut_1d
from config import cfg
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends
from fastapi.routing import APIRouter
from tools.stock_cut_1d.models import model_job
from tools.stock_cut_1d.models import model_result
from tools.stock_cut_1d.solver import distribute

router = APIRouter()


@router.post("/1d/solve", response_model=schema_stock_cut_1d.Result)
def post_1d_solve(
    job_in: schema_stock_cut_1d.Job,
    verified: bool = Depends(deps.verify_token),
) -> Any:
    """Solves the one dimensional stock cutting problem."""

    job = model_job.Job(**job_in.model_dump())
    try:
        job.assert_valid()
    except ValueError as e:
        raise HTTPException(status_code=406, detail=str(e))

    try:
        solved: model_result.Result = distribute(job)
    except OverflowError as e:
        raise HTTPException(status_code=507, detail=str(e))

    try:
        solved.assert_valid()
    except ValueError as e:
        raise HTTPException(status_code=507, detail=str(e))

    return solved
