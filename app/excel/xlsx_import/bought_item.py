from typing import Any
from typing import Dict
from typing import List

from api.schemas.bought_item import BoughtItemCreateSchema
from crud.project import crud_project
from db.models import BoughtItemModel
from db.models.user import User
from excel.xlsx_import.base import BaseExcelImport
from fastapi import HTTPException
from fastapi import UploadFile
from fastapi import status
from sqlalchemy.orm import Session


class BoughtItemExcelImport(BaseExcelImport[BoughtItemModel, BoughtItemCreateSchema]):
    def __init__(self, db: Session, db_obj_user: User, file: UploadFile) -> None:
        super().__init__(db, model=BoughtItemModel, schema=BoughtItemCreateSchema, db_obj_user=db_obj_user, file=file)

    # def _get_model_columns_by_name_convention(self) -> List[str]:
    #     model_cols = []
    #     for col in self.model.__table__.columns.keys():  # type: ignore
    #         if col == "project_id":
    #             col = "project_number"
    #         model_cols.append(" ".join(i.capitalize() for i in str(col).split("_")))
    #     return model_cols

    def _get_schema_columns_by_name_convention(self) -> List[str]:
        schema_cols = []
        for col in self.schema.model_fields.keys():  # type: ignore
            if col == "project_id":
                col = "project"  # Column in EXCEL file is named `Project`
            schema_cols.append(" ".join(i.capitalize() for i in str(col).split("_")))
        return schema_cols

    def _append_schema(self, db_obj_in: Dict[str, Any], db_objs_in: List[BoughtItemCreateSchema]) -> None:
        if "project" not in db_obj_in:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Column `Project` not found")

        project_number = db_obj_in["project"]
        project = crud_project.get_by_number(self.db, number=project_number)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"A project with the number {project_number} doesn't exists.",
            )
        if not project.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"The project with the number {project_number} is not active.",
            )

        del db_obj_in["project"]
        db_obj_in["project_id"] = project.id
        db_objs_in.append(self.schema(**db_obj_in))
