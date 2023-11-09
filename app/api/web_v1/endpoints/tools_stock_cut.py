"""
    Handles all routes to the tools-resource.
"""

from typing import Any

from api import deps
from config import cfg
from fastapi.param_functions import Depends
from fastapi.routing import APIRouter
from tools.stock_cut.job import Job
from tools.stock_cut.result import Result
from tools.stock_cut.solver import distribute

router = APIRouter()


@router.post("/solve", response_model=Result)
def post_solve(
    job: Job,
    verified: bool = Depends(deps.verify_token),
) -> Any:
    """Solves the stock cutting problem."""
    job.assert_valid()
    solved: Result = distribute(job)
    solved.assert_valid()
    return solved
