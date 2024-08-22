"""
    Stock cut schema.
"""

from tools.stock_cut_1d.models import JobModel
from tools.stock_cut_1d.models import ResultModel


class StockCut1DJobSchema(JobModel):
    ...


class StockCut1DResultSchema(ResultModel):
    ...
