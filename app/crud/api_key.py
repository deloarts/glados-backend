"""
    Create-Read-Update-Delete: Api-Key
"""

import secrets
from datetime import UTC
from datetime import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from api.schemas.api_key import APIKeyCreateSchema
from api.schemas.api_key import APIKeyUpdateSchema
from crud.base import CRUDBase
from db.models import APIKeyModel
from sqlalchemy.orm import Session

from app.security import create_access_token


class CRUDAPIKey(CRUDBase[APIKeyModel, APIKeyCreateSchema, APIKeyUpdateSchema]):
    """CRUDAPIKey class. Descendent of the CRUDBase class."""

    def get(self, db: Session, id: int) -> Optional[APIKeyModel]:  # pylint: disable=W0622
        """
        Retrieves an api key by its id.
        """
        return db.query(self.model).filter_by(deleted=False).filter(self.model.id == id).first()

    def get_by_name(self, db: Session, *, name: str) -> Optional[APIKeyModel]:
        """
        Retrieves an api key by its name.
        """
        return db.query(self.model).filter(self.model.name == name).first()

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[APIKeyModel]:
        """
        Retrieves multiple api keys.
        """
        return db.query(self.model).filter_by(deleted=False).offset(skip).limit(limit).all()

    def get_deleted(self, db: Session, *, id: int) -> Optional[APIKeyModel]:  # pylint: disable=W0622
        """
        Retrieves an as deleted marked api key by its id.
        """
        return db.query(self.model).filter_by(deleted=True).filter(self.model.id == id).first()

    def get_deleted_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[APIKeyModel]:
        """
        Retrieves multiple as deleted marked api keys.
        """
        return db.query(self.model).filter_by(deleted=True).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: APIKeyCreateSchema) -> APIKeyModel:
        """
        Creates a new api key.
        """
        data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)
        data["created"] = datetime.now(UTC)
        data["api_key"] = secrets.token_urlsafe(32)  # This is a temp value, required for creation

        db_obj = APIKeyModel(**data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        delta = db_obj.expiration_date - datetime.now()
        api_key = create_access_token(subject=db_obj.id, persistent=True, expires_delta=delta)
        setattr(db_obj, self.model.api_key.name, api_key)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

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

    def delete(self, db: Session, *, id: int, forever: bool = False) -> Optional[APIKeyModel]:  # pylint: disable=W0622
        """
        Deletes an api key.
        If forever is `False` the key will only be marked for deletion. It then will be deleted by schedule at midnight.

        Args:
            db (Session): DB session.
            id (int): The key id.
            forever (bool, optional): If `True`, the key will be deleted from the db, marked for deletion of `False`.
                Defaults to `False`.

        Returns:
            Optional[APIKeyModel]: The API key model, if found.
        """
        obj = db.query(self.model).filter(self.model.id == id).first()
        if forever:
            db.delete(obj)
            db.commit()
        else:
            setattr(obj, self.model.deleted.name, True)
            db.add(obj)
            db.commit()
            db.refresh(obj)
        return obj


crud_api_key = CRUDAPIKey(APIKeyModel)
