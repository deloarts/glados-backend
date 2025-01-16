from math import ceil
from math import floor
from typing import Generic
from typing import List
from typing import TypeVar

from pydantic import BaseModel
from pydantic import computed_field

SchemaType = TypeVar("SchemaType", bound=BaseModel)


class PageSchema(BaseModel, Generic[SchemaType]):
    items: List[SchemaType]
    total: int
    limit: int
    skip: int

    @computed_field
    @property
    def pages(self) -> int:
        return ceil(self.total / (self.limit if self.limit > 0 else self.total)) if self.total > 0 else 1

    @computed_field
    @property
    def current(self) -> int:
        return floor(self.skip / (self.limit if self.limit > 0 else 1) + 1) if self.skip > 0 else 1
