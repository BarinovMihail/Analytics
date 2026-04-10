from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import distinct, func, select
from sqlalchemy.orm import Session, selectinload

from app.core.database import get_db
from app.models.card_characteristic import CardCharacteristic
from app.models.mtr_card import MtrCard
from app.schemas.cards import CardCharacteristicOut, CardListResponse, MtrCardDetail, MtrCardShort

router = APIRouter(prefix="/api", tags=["cards"])


@router.get(
    "/cards",
    response_model=CardListResponse,
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {
                        "total": 120,
                        "page": 1,
                        "per_page": 20,
                        "items": [
                            {
                                "id": 5,
                                "guid": "123e4567-e89b-12d3-a456-426614174000",
                                "name": "Клапан запорный DN20",
                                "manufacturer_inn": "7701234567",
                                "article": "KV-20",
                                "price": "1481412.00",
                                "price_date_start": "2026-02-06",
                                "price_date_end": "2026-12-31",
                            }
                        ],
                    }
                }
            }
        }
    },
)
def list_cards(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    name: str | None = Query(default=None),
    manufacturer_inn: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> CardListResponse:
    filters = []
    if name:
        filters.append(MtrCard.name.ilike(f"%{name.strip()}%"))
    if manufacturer_inn:
        filters.append(MtrCard.manufacturer_inn == manufacturer_inn.strip())

    total = db.scalar(select(func.count(MtrCard.id)).where(*filters)) or 0
    query = (
        select(MtrCard)
        .where(*filters)
        .order_by(MtrCard.created_at.desc(), MtrCard.id.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    items = list(db.scalars(query))
    return CardListResponse(total=total, page=page, per_page=per_page, items=items)


@router.get(
    "/cards/{guid}",
    response_model=MtrCardDetail,
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {
                        "id": 5,
                        "batch_id": 12,
                        "guid": "123e4567-e89b-12d3-a456-426614174000",
                        "name": "Клапан запорный DN20",
                        "manufacturer_inn": "7701234567",
                        "manufacturer_inio": None,
                        "country_code": "643",
                        "article": "KV-20",
                        "price": "1481412.00",
                        "price_date_start": "2026-02-06",
                        "price_date_end": "2026-12-31",
                        "description": "Полное описание карточки",
                        "raw_row_json": {"GUID": "123e4567-e89b-12d3-a456-426614174000"},
                        "created_at": "2026-04-10T08:10:00Z",
                        "characteristics": [
                            {
                                "char_name": "Диаметр номинальный DN",
                                "char_value_raw": "20",
                                "char_unit": "мм",
                                "char_type": "number",
                                "value_numeric": "20.0000",
                                "range_min": None,
                                "range_max": None,
                                "value_text": None,
                            }
                        ],
                    }
                }
            }
        }
    },
)
def get_card_detail(guid: str, db: Session = Depends(get_db)) -> MtrCardDetail:
    query = (
        select(MtrCard)
        .where(MtrCard.guid == guid.lower())
        .options(selectinload(MtrCard.characteristics))
    )
    card = db.scalar(query)
    if card is None:
        raise HTTPException(status_code=404, detail="Card not found")
    return card


@router.get(
    "/cards/{guid}/characteristics",
    response_model=list[CardCharacteristicOut],
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": [
                        {
                            "char_name": "Рабочая среда",
                            "char_value_raw": "вода;пар;",
                            "char_unit": None,
                            "char_type": "multivalue",
                            "value_numeric": None,
                            "range_min": None,
                            "range_max": None,
                            "value_text": "вода;пар",
                        }
                    ]
                }
            }
        }
    },
)
def get_card_characteristics(guid: str, db: Session = Depends(get_db)) -> list[CardCharacteristic]:
    card_id = db.scalar(select(MtrCard.id).where(MtrCard.guid == guid.lower()))
    if card_id is None:
        raise HTTPException(status_code=404, detail="Card not found")
    query = (
        select(CardCharacteristic)
        .where(CardCharacteristic.card_id == card_id)
        .order_by(CardCharacteristic.char_name.asc())
    )
    return list(db.scalars(query))


@router.get(
    "/characteristics/names",
    response_model=list[str],
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": [
                        "Диаметр номинальный DN",
                        "Способ присоединения к трубопроводу",
                        "Рабочая среда",
                    ]
                }
            }
        }
    },
)
def list_characteristic_names(db: Session = Depends(get_db)) -> list[str]:
    query = select(distinct(CardCharacteristic.char_name)).order_by(CardCharacteristic.char_name.asc())
    return [row for row in db.scalars(query)]
