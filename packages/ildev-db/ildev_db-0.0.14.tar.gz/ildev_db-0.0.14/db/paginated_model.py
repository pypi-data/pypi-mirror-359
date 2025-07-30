from pydantic import BaseModel, Field, ConfigDict
from typing import List, Generic, Optional, TypeVar

T = TypeVar("T")

class PaginatedModel(BaseModel, Generic[T]):
    data: List[T]
    total: int
    skip: int = Field(default=0, ge=0)
    limit: Optional[int] = Field(default=100, gt=0)
    count: int

    model_config = ConfigDict(arbitrary_types_allowed=True)
