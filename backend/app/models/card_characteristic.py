from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.mtr_card import MtrCard


class CharacteristicType(str, Enum):
    NUMBER = "number"
    RANGE = "range"
    LIST = "list"
    MULTIVALUE = "multivalue"
    STRING = "string"


class CardCharacteristic(Base):
    __tablename__ = "card_characteristics"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    card_id: Mapped[int] = mapped_column(ForeignKey("mtr_cards.id"), nullable=False, index=True)
    char_name: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    char_value_raw: Mapped[str | None] = mapped_column(Text, nullable=True)
    char_unit: Mapped[str | None] = mapped_column(String(100), nullable=True)
    char_type: Mapped[CharacteristicType] = mapped_column(
        SqlEnum(
            CharacteristicType,
            name="characteristic_type_enum",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        nullable=False,
    )
    value_numeric: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True, index=True)
    range_min: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    range_max: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    value_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    card: Mapped["MtrCard"] = relationship(back_populates="characteristics")
