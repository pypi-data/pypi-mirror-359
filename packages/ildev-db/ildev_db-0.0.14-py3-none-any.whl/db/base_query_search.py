from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class BaseQuerySearch(BaseModel):
    search_text: str = Field(default="", description="Text to search in the database")
    projection_fields: Optional[List[str]] = None
