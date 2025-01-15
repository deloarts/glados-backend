from typing import Generic
from typing import List
from typing import TypeVar

from pydantic import BaseModel

SchemaType = TypeVar("SchemaType", bound=BaseModel)


class PageSchema(BaseModel, Generic[SchemaType]):
    items: List[SchemaType]
    total: int
    limit: int
    skip: int
    pages: int
