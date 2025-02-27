"""
    Create-Read-Update-Delete: Base
"""

from typing import Any
from typing import Dict
from typing import Generic
from typing import List
from typing import Optional
from typing import Type
from typing import TypeVar

from db.base import Base
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType", bound=Base)  # pylint: disable=C0103
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)  # pylint: disable=C0103
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)  # pylint: disable=C0103


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Generic base class."""

    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:  # pylint: disable=W0622
        """
        Retrieves a db model by a given id.
        """
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(self, db: Session, *, skip: int | None = None, limit: int | None = None) -> List[ModelType]:
        """
        Retrieves many.
        """
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Creates an entry by a given model.
        """
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj  # type: ignore

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: UpdateSchemaType | Dict[str, Any],
    ) -> ModelType:
        """
        Updates an entry by a given model and object.
        """
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, id: int) -> Optional[ModelType]:  # pylint: disable=W0622
        """
        Deletes an db entry.
        """
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj
