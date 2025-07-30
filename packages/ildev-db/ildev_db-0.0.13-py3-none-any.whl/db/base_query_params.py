from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class BaseQueryParams(BaseModel):
    skip: int = Field(default=0, ge=0)
    limit: Optional[int] = Field(default=100, gt=0)
    sort: Optional[List[tuple]] = None
