"""
    Handles all routes to the tools-resource.
"""

from typing import Any
from typing import Literal

from api import deps
from api.schemas.stock_cut_2d import StockCut2DJobSchema
from api.schemas.stock_cut_2d import StockCut2DResultSchema
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends
from fastapi.responses import FileResponse
from fastapi.routing import APIRouter
from opcut.common import OutputFormat
from tools.stock_cut_2d.models import JobModel
from tools.stock_cut_2d.models import ResultModel
from tools.stock_cut_2d.solver import Solver

router = APIRouter()


@router.post("/2d/solve", response_model=StockCut2DResultSchema)
def post_2d_solve(
    job_in: StockCut2DJobSchema,
    verified: bool = Depends(deps.verify_token),
) -> Any:
    """Solves the two dimensional stock cutting problem. Returns the result of the solver."""

    solver = Solver()
    try:
        return solver.calculate(job=JobModel(**job_in.model_dump()))
    except ValueError as e:
        raise HTTPException(status_code=406, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e)) from e


@router.post("/2d/generate", response_class=FileResponse)
def post_2d_generate(
    result_in: StockCut2DResultSchema,
    output_format: OutputFormat,
    verified: bool = Depends(deps.verify_token),
) -> Any:
    """Returns a pdf or svg file for the given result of the 2d stock cutting problem."""

    solver = Solver()
    try:
        path = solver.generate(result=ResultModel(**result_in.model_dump()), output_format=output_format)
        return FileResponse(
            path=str(path),
            headers={"Content-Disposition": f'attachment; filename="{path.name}"'},
        )
    except NotImplementedError as e:
        raise HTTPException(status_code=501, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
