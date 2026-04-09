from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, Date, DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.card_characteristic import CardCharacteristic
    from app.models.import_batch import ImportBatch


class MtrCard(Base):
    __tablename__ = "mtr_cards"
    __table_args__ = (UniqueConstraint("guid", name="uq_mtr_cards_guid"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    batch_id: Mapped[int] = mapped_column(ForeignKey("import_batches.id"), nullable=False, index=True)
    guid: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    manufacturer_inn: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    manufacturer_inio: Mapped[str | None] = mapped_column(String(50), nullable=True)
    country_code: Mapped[str | None] = mapped_column(String(10), nullable=True, index=True)
    article: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    price: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True, index=True)
    price_date_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    price_date_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    description: Mapped[str | None] = mapped_column(LONGTEXT, nullable=True)
    raw_row_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    batch: Mapped["ImportBatch"] = relationship(back_populates="mtr_cards")
    characteristics: Mapped[list["CardCharacteristic"]] = relationship(
        back_populates="card",
        cascade="all, delete-orphan",
        order_by="CardCharacteristic.char_name.asc()",
    )
