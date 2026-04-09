from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.mtr_card import MtrCard
    from app.models.import_error import ImportError


class ImportBatch(Base):
    __tablename__ = "import_batches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_checksum: Mapped[str | None] = mapped_column(String(64), nullable=True, unique=True, index=True)
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="processing")
    rows_total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rows_success: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rows_error: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rows_duplicate: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    mtr_cards: Mapped[list["MtrCard"]] = relationship(
        back_populates="batch",
        cascade="all, delete-orphan",
    )
    import_errors: Mapped[list["ImportError"]] = relationship(
        back_populates="batch",
        cascade="all, delete-orphan",
    )
