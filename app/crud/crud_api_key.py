"""
    Create-Read-Update-Delete: Api-Key
"""

from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from api.schemas.api_key import APIKeyCreateSchema
from api.schemas.api_key import APIKeyUpdateSchema
from crud.crud_base import CRUDBase
from db.models.api_key import APIKeyModel
from sqlalchemy.orm import Session


class CRUDAPIKey(CRUDBase[APIKeyModel, APIKeyCreateSchema, APIKeyUpdateSchema]):
    """CRUDAPIKey class. Descendent of the CRUDBase class."""

    def get(self, db: Session, id: Any) -> Optional[APIKeyModel]:  # pylint: disable=W0622
        """
        Retrieves an api key by its id.
        """
        return (
            db.query(APIKeyModel)
            .filter(
                APIKeyModel.id == id,
                APIKeyModel.deleted is False,
            )
            .first()
        )

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[APIKeyModel]:
        """
        Retrieves multiple api keys.
        """
        return db.query(APIKeyModel).filter(APIKeyModel.deleted is False).offset(skip).limit(limit).all()

    def get_by_api_key(self, db: Session, *, key: str) -> Optional[APIKeyModel]:
        """
        Retrieves an api key by its key value.
        """
        return (
            db.query(APIKeyModel)
            .filter(
                APIKeyModel.api_key == key,
                APIKeyModel.deleted is False,
            )
            .first()
        )

    def get_deleted(self, db: Session, *, id: int) -> Optional[APIKeyModel]:  # pylint: disable=W0622
        """
        Retrieves an as deleted marked api key by its id.
        """
        return db.query(APIKeyModel).filter(APIKeyModel.id == id, APIKeyModel.deleted is True).first()

    def get_deleted_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[APIKeyModel]:
        """
        Retrieves multiple as deleted marked api keys.
        """
        return db.query(APIKeyModel).filter(APIKeyModel.deleted is True).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: APIKeyCreateSchema) -> APIKeyModel:
        """
        Creates a new api key.
        """
        db_obj = super().create(db, obj_in=obj_in)
        return db_obj

    def update(self, db: Session, *, db_obj: APIKeyModel, obj_in: APIKeyUpdateSchema | Dict[str, Any]) -> APIKeyModel:
        """
        Updates an api key.
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def delete(self, db: Session, *, id: int) -> Optional[APIKeyModel]:  # pylint: disable=W0622
        """
        Marks an api key as deleted. An api key will never be fully deleted.
        """
        obj = db.query(APIKeyModel).filter(APIKeyModel.id == id).first()
        setattr(obj, APIKeyModel.deleted.name, True)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj


api_key = CRUDAPIKey(APIKeyModel)
