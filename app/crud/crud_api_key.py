"""
    Create-Read-Update-Delete: Api-Key
"""

from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from api.schemas import schema_api_key
from crud.crud_base import CRUDBase
from db.models import model_api_key
from sqlalchemy.orm import Session


class CRUDAPIKey(CRUDBase[model_api_key.APIKey, schema_api_key.APIKeyCreate, schema_api_key.APIKeyUpdate]):
    """CRUDAPIKey class. Descendent of the CRUDBase class."""

    def get(self, db: Session, id: Any) -> Optional[model_api_key.APIKey]:  # pylint: disable=W0622
        """
        Retrieves an api key by its id.
        """
        return (
            db.query(model_api_key.APIKey)
            .filter(
                model_api_key.APIKey.id == id,
                model_api_key.APIKey.deleted is False,
            )
            .first()
        )

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[model_api_key.APIKey]:
        """
        Retrieves multiple api keys.
        """
        return (
            db.query(model_api_key.APIKey).filter(model_api_key.APIKey.deleted is False).offset(skip).limit(limit).all()
        )

    def get_by_api_key(self, db: Session, *, key: str) -> Optional[model_api_key.APIKey]:
        """
        Retrieves an api key by its key value.
        """
        return (
            db.query(model_api_key.APIKey)
            .filter(
                model_api_key.APIKey.api_key == key,
                model_api_key.APIKey.deleted is False,
            )
            .first()
        )

    def get_deleted(self, db: Session, *, id: int) -> Optional[model_api_key.APIKey]:  # pylint: disable=W0622
        """
        Retrieves an as deleted marked api key by its id.
        """
        return (
            db.query(model_api_key.APIKey)
            .filter(model_api_key.APIKey.id == id, model_api_key.APIKey.deleted is True)
            .first()
        )

    def get_deleted_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[model_api_key.APIKey]:
        """
        Retrieves multiple as deleted marked api keys.
        """
        return (
            db.query(model_api_key.APIKey).filter(model_api_key.APIKey.deleted is True).offset(skip).limit(limit).all()
        )

    def create(self, db: Session, *, obj_in: schema_api_key.APIKeyCreate) -> model_api_key.APIKey:
        """
        Creates a new api key.
        """
        db_obj = super().create(db, obj_in=obj_in)
        return db_obj

    def update(
        self, db: Session, *, db_obj: model_api_key.APIKey, obj_in: schema_api_key.APIKeyUpdate | Dict[str, Any]
    ) -> model_api_key.APIKey:
        """
        Updates an api key.
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def delete(self, db: Session, *, id: int) -> Optional[model_api_key.APIKey]:  # pylint: disable=W0622
        """
        Marks an api key as deleted. An api key will never be fully deleted.
        """
        obj = db.query(model_api_key.APIKey).filter(model_api_key.APIKey.id == id).first()
        setattr(obj, model_api_key.APIKey.deleted.name, True)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj


api_key = CRUDAPIKey(model_api_key.APIKey)
