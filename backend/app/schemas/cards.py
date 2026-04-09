from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class CardCharacteristicOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    char_name: str
    char_value_raw: str | None
    char_unit: str | None
    char_type: str
    value_numeric: Decimal | None
    range_min: Decimal | None
    range_max: Decimal | None
    value_text: str | None


class MtrCardShort(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    guid: str
    name: str
    manufacturer_inn: str | None
    article: str | None
    price: Decimal | None
    price_date_start: date | None
    price_date_end: date | None


class MtrCardDetail(MtrCardShort):
    batch_id: int
    manufacturer_inio: str | None
    country_code: str | None
    description: str | None
    raw_row_json: dict[str, object]
    created_at: datetime
    characteristics: list[CardCharacteristicOut]


class CardListResponse(BaseModel):
    total: int
    page: int
    per_page: int
    items: list[MtrCardShort]
