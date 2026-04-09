from __future__ import annotations

from decimal import Decimal

from sqlalchemy import case, distinct, func, select
from sqlalchemy.orm import Session, aliased

from app.models.card_characteristic import CardCharacteristic
from app.models.import_batch import ImportBatch
from app.models.mtr_card import MtrCard
from app.schemas.analytics import (
    ConnectionTypeStat,
    DnStat,
    ManufacturerStat,
    PriceRangeStat,
    SafetyClassStat,
    SummaryResponse,
)

DN_CHAR_NAME = "Диаметр номинальный DN"
CONNECTION_TYPE_CHAR_NAME = "Способ присоединения к трубопроводу"
SAFETY_CLASS_CHAR_NAME = "Класс безопасности"


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def get_summary(self) -> SummaryResponse:
        query = select(
            func.count(MtrCard.id),
            func.count(distinct(MtrCard.manufacturer_inn)),
            func.count(MtrCard.price),
            func.avg(MtrCard.price),
            func.max(ImportBatch.uploaded_at),
        ).select_from(MtrCard).join(ImportBatch, ImportBatch.id == MtrCard.batch_id)
        total_cards, unique_manufacturers, cards_with_price, avg_price, last_upload_date = self.db.execute(query).one()
        return SummaryResponse(
            total_cards=total_cards or 0,
            unique_manufacturers=unique_manufacturers or 0,
            cards_with_price=cards_with_price or 0,
            avg_price=Decimal(str(avg_price)).quantize(Decimal("0.01")) if avg_price is not None else None,
            last_upload_date=last_upload_date,
        )

    def by_manufacturer(self) -> list[ManufacturerStat]:
        query = (
            select(
                MtrCard.manufacturer_inn,
                func.count(MtrCard.id).label("cards_count"),
            )
            .where(MtrCard.manufacturer_inn.is_not(None))
            .group_by(MtrCard.manufacturer_inn)
            .order_by(func.count(MtrCard.id).desc(), MtrCard.manufacturer_inn.asc())
            .limit(20)
        )
        return [
            ManufacturerStat(manufacturer_inn=row.manufacturer_inn, cards_count=row.cards_count)
            for row in self.db.execute(query)
        ]

    def by_dn(self) -> list[DnStat]:
        dn_char = aliased(CardCharacteristic)
        query = (
            select(
                dn_char.value_numeric.label("dn_value"),
                func.count(MtrCard.id).label("cards_count"),
            )
            .join(dn_char, dn_char.card_id == MtrCard.id)
            .where(dn_char.char_name == DN_CHAR_NAME)
            .group_by(dn_char.value_numeric)
            .order_by(dn_char.value_numeric.asc())
        )
        return [
            DnStat(dn_value=row.dn_value, cards_count=row.cards_count)
            for row in self.db.execute(query)
        ]

    def by_connection_type(self) -> list[ConnectionTypeStat]:
        characteristic = aliased(CardCharacteristic)
        query = (
            select(
                characteristic.value_text.label("connection_type"),
                func.count(MtrCard.id).label("cards_count"),
            )
            .join(characteristic, characteristic.card_id == MtrCard.id)
            .where(characteristic.char_name == CONNECTION_TYPE_CHAR_NAME)
            .where(characteristic.value_text.is_not(None))
            .group_by(characteristic.value_text)
            .order_by(func.count(MtrCard.id).desc(), characteristic.value_text.asc())
        )
        return [
            ConnectionTypeStat(connection_type=row.connection_type, cards_count=row.cards_count)
            for row in self.db.execute(query)
        ]

    def by_safety_class(self) -> list[SafetyClassStat]:
        characteristic = aliased(CardCharacteristic)
        query = (
            select(
                characteristic.value_text.label("safety_class"),
                func.count(MtrCard.id).label("cards_count"),
            )
            .join(characteristic, characteristic.card_id == MtrCard.id)
            .where(characteristic.char_name == SAFETY_CLASS_CHAR_NAME)
            .where(characteristic.value_text.is_not(None))
            .group_by(characteristic.value_text)
            .order_by(func.count(MtrCard.id).desc(), characteristic.value_text.asc())
        )
        return [
            SafetyClassStat(safety_class=row.safety_class, cards_count=row.cards_count)
            for row in self.db.execute(query)
        ]

    def price_range(self) -> list[PriceRangeStat]:
        range_label = case(
            (MtrCard.price.is_(None), "Без цены"),
            (MtrCard.price < Decimal("10000"), "до 10 000"),
            (MtrCard.price < Decimal("100000"), "10 000 - 99 999"),
            (MtrCard.price < Decimal("1000000"), "100 000 - 999 999"),
            else_="1 000 000+",
        )
        query = (
            select(range_label.label("range_label"), func.count(MtrCard.id).label("cards_count"))
            .group_by(range_label)
            .order_by(func.count(MtrCard.id).desc(), range_label.asc())
        )
        return [
            PriceRangeStat(range_label=row.range_label, cards_count=row.cards_count)
            for row in self.db.execute(query)
        ]
