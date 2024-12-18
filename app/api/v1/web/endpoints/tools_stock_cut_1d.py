"""
    Handles all routes to the tools-resource.
"""

from typing import Any

from api import deps
from api.schemas.stock_cut_1d import StockCut1DJobSchema
from api.schemas.stock_cut_1d import StockCut1DResultSchema
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends
from fastapi.routing import APIRouter
from tools.stock_cut_1d.models import JobModel
from tools.stock_cut_1d.models import ResultModel
from tools.stock_cut_1d.solver import distribute

router = APIRouter()


@router.post("/1d/solve", response_model=StockCut1DResultSchema)
def post_1d_solve(
    job_in: StockCut1DJobSchema,
    verified: bool = Depends(deps.verify_token),
) -> Any:
    """Solves the one dimensional stock cutting problem."""

    job = JobModel(**job_in.model_dump())
    try:
        job.assert_valid()
    except ValueError as e:
        raise HTTPException(status_code=406, detail=str(e)) from e

    try:
        solved: ResultModel = distribute(job)
    except OverflowError as e:
        raise HTTPException(status_code=507, detail=str(e)) from e

    try:
        solved.assert_valid()
    except ValueError as e:
        raise HTTPException(status_code=507, detail=str(e)) from e

    return solved
