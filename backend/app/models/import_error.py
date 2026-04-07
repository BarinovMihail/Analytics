from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.import_batch import ImportBatch


class ImportError(Base):
    __tablename__ = "import_errors"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    batch_id: Mapped[int] = mapped_column(ForeignKey("import_batches.id"), nullable=False, index=True)
    row_number: Mapped[int] = mapped_column(nullable=False, index=True)
    error_message: Mapped[str] = mapped_column(Text, nullable=False)
    raw_row_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    batch: Mapped["ImportBatch"] = relationship(back_populates="import_errors")
