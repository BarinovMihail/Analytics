from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, Date, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.import_batch import ImportBatch


class Purchase(Base):
    __tablename__ = "purchases"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    batch_id: Mapped[int] = mapped_column(ForeignKey("import_batches.id"), nullable=False, index=True)

    item_code: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    item_name: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    category_code: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    category_name: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    purchase_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    supplier_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    supplier_inn: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    supplier_contact: Mapped[str | None] = mapped_column(String(255), nullable=True)
    supplier_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    customer_inn: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True, index=True)
    delivery_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    unit_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    origin_country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    manufacturer_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    developer_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    raw_row_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    batch: Mapped["ImportBatch"] = relationship(back_populates="purchases")
