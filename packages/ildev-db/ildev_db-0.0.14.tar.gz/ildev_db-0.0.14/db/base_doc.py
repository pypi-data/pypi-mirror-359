from beanie import Document
from datetime import datetime, timezone
from typing import Optional
from pydantic import Field


class BaseDoc(Document):
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_deleted: bool = Field(default=False)

    class Settings:
        use_state_management = True