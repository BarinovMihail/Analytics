from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.import_error import ImportError
    from app.models.purchase import Purchase


class ImportBatch(Base):
    __tablename__ = "import_batches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="processing")
    rows_total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rows_success: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rows_error: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    purchases: Mapped[list["Purchase"]] = relationship(
        back_populates="batch",
        cascade="all, delete-orphan",
    )
    import_errors: Mapped[list["ImportError"]] = relationship(
        back_populates="batch",
        cascade="all, delete-orphan",
    )
