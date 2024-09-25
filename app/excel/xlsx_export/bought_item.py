from typing import List

from api.schemas.bought_item import BoughtItemExcelExportSchema
from db.models import BoughtItemModel
from excel.xlsx_export.base import BaseExcelExport


class BoughtItemExcelExport(BaseExcelExport[BoughtItemModel, BoughtItemExcelExportSchema]):
    def __init__(self, data: List[BoughtItemModel]) -> None:
        super().__init__(schema=BoughtItemExcelExportSchema)

        # The reason for this:
        # In the exported excel file the user wants the project number, not the project ID.
        # But the number is an association proxy which points to the project_table in the DB.
        # When converting the data (a.k.a the BoughtItemModel) to a dict, the `project_number` won't
        # be added to the dict's data. Therefor this extra step (or this extra module) is needed, to
        # preserve the `project_number` when converting from model to dict.
        # Same for all other manual added key-value pairs.

        extended_data = []
        for datum in data:
            datum_dict = datum.__dict__
            datum_dict["project_number"] = datum.project_number
            datum_dict["product_number"] = datum.product_number
            extended_data.append(datum_dict)

        self.import_data_by_dict(data=extended_data)
