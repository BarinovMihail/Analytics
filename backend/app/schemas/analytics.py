from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class SummaryResponse(BaseModel):
    total_cards: int
    unique_manufacturers: int
    cards_with_price: int
    avg_price: Decimal | None
    last_upload_date: datetime | None


class ManufacturerStat(BaseModel):
    manufacturer_inn: str
    cards_count: int


class DnStat(BaseModel):
    dn_value: Decimal | None
    cards_count: int


class ConnectionTypeStat(BaseModel):
    connection_type: str
    cards_count: int


class SafetyClassStat(BaseModel):
    safety_class: str
    cards_count: int


class PriceRangeStat(BaseModel):
    range_label: str
    cards_count: int
