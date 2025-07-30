from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class BaseQueryFilter(BaseModel):       
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    include_deleted: bool = Field(default=False)
