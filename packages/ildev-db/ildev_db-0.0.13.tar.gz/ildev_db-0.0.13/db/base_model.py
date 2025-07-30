from datetime import datetime, timezone
from sqlalchemy import Integer, Boolean, DateTime
from sqlalchemy.orm import as_declarative, mapped_column, Mapped

@as_declarative()
class BaseModel:
    __name__: str  # Required by as_declarative

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
