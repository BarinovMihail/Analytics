from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from sqlalchemy import and_, func, literal, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.card_characteristic import CardCharacteristic
from app.models.comparison_task import ComparisonTask
from app.models.mtr_card import MtrCard
from app.schemas.compare import CompareFilters
from app.services.excel_exporter import export_cards_to_excel

FILTER_TO_CHARACTERISTIC = {
    "dn": "Диаметр номинальный DN",
    "pressure_min": "Давление номинальное/расчетное",
    "temp_max": "Диапазон температур рабочей среды",
    "design_temp_max": "Температура расчетная",
    "connection_type": "Способ присоединения к трубопроводу",
    "valve_design": "Конструкция запорного или регулирующего органа",
    "control_type": "Исполнение по способу управления",
    "safety_class": "Класс безопасности",
    "quality_category": "Категория обеспечения качества",
    "seismic_category": "Категория сейсмостойкости",
    "power_max": "Мощность привода",
    "close_time_max": "Время закрытия",
    "open_time_max": "Время открытия",
    "body_material": "Материал корпуса",
    "working_medium": "Рабочая среда",
    "service_life_min": "Назначенный срок службы",
    "building_length_max": "Строительная длина арматуры",
}
NUMERIC_FILTER_KEYS = {
    "dn",
    "pressure_min",
    "temp_max",
    "design_temp_max",
    "power_max",
    "close_time_max",
    "open_time_max",
    "price_max",
    "service_life_min",
    "building_length_max",
}
DATE_FILTER_KEYS = {"price_date"}


def filter_cards(db: Session, filters: dict) -> list[MtrCard]:
    normalized_filters = _drop_empty_filters(filters)
    query = select(MtrCard).options(selectinload(MtrCard.characteristics))

    if "manufacturer_inn" in normalized_filters:
        query = query.where(MtrCard.manufacturer_inn == normalized_filters["manufacturer_inn"])
    if "country_code" in normalized_filters:
        query = query.where(MtrCard.country_code == normalized_filters["country_code"])
    if "price_max" in normalized_filters:
        query = query.where(MtrCard.price.is_not(None), MtrCard.price <= normalized_filters["price_max"])
    if "price_date" in normalized_filters:
        price_date = normalized_filters["price_date"]
        query = query.where(
            MtrCard.price_date_start.is_not(None),
            MtrCard.price_date_end.is_not(None),
            MtrCard.price_date_start <= price_date,
            MtrCard.price_date_end >= price_date,
        )

    for filter_name, value in normalized_filters.items():
        characteristic_name = FILTER_TO_CHARACTERISTIC.get(filter_name)
        if characteristic_name is None:
            continue
        query = query.where(_characteristic_predicate(filter_name, characteristic_name, value))

    query = query.order_by(MtrCard.created_at.desc(), MtrCard.id.desc())
    return list(db.scalars(query).unique().all())


def run_comparison_task(
    db: Session,
    *,
    task_name: str,
    filters: CompareFilters,
    export_dir: Path,
) -> ComparisonTask:
    python_filters = filters.model_dump()
    filter_payload = filters.model_dump(mode="json")
    total_cards = db.scalar(select(func.count(MtrCard.id))) or 0
    task = ComparisonTask(
        name=task_name,
        filter_params_json=filter_payload,
        total_cards=total_cards,
        matched_cards=0,
        status="running",
    )
    db.add(task)
    db.flush()

    try:
        cards = filter_cards(db, python_filters)
        task.matched_cards = len(cards)
        task.status = "done"
        task.finished_at = datetime.utcnow()

        export_dir.mkdir(parents=True, exist_ok=True)
        char_names = get_filter_characteristic_names(python_filters)
        file_path = export_dir / f"comparison_task_{task.id}.xlsx"
        file_path.write_bytes(export_cards_to_excel(cards, char_names))
        task.output_file_path = str(file_path)

        db.commit()
        db.refresh(task)
        return task
    except Exception:
        task.status = "error"
        task.finished_at = datetime.utcnow()
        db.commit()
        db.refresh(task)
        raise


def get_filter_characteristic_names(filters: dict) -> list[str]:
    return [
        FILTER_TO_CHARACTERISTIC[filter_name]
        for filter_name, value in _drop_empty_filters(filters).items()
        if filter_name in FILTER_TO_CHARACTERISTIC and value not in (None, "")
    ]


def _drop_empty_filters(filters: dict) -> dict:
    normalized: dict = {}
    for key, value in filters.items():
        if value in (None, "", []):
            continue
        if key in NUMERIC_FILTER_KEYS and isinstance(value, str):
            normalized[key] = Decimal(value)
        elif key in DATE_FILTER_KEYS and isinstance(value, str):
            normalized[key] = date.fromisoformat(value)
        elif isinstance(value, str):
            normalized[key] = value.strip()
        else:
            normalized[key] = value
    return normalized


def _characteristic_predicate(filter_name: str, characteristic_name: str, value: str | Decimal) -> object:
    if filter_name == "working_medium":
        return select(literal(1)).where(
            CardCharacteristic.card_id == MtrCard.id,
            CardCharacteristic.char_name == characteristic_name,
            CardCharacteristic.value_text.is_not(None),
            or_(
                CardCharacteristic.value_text == value,
                CardCharacteristic.value_text.like(f"{value};%"),
                CardCharacteristic.value_text.like(f"%;{value}"),
                CardCharacteristic.value_text.like(f"%;{value};%"),
            ),
        ).exists()

    conditions = [CardCharacteristic.card_id == MtrCard.id, CardCharacteristic.char_name == characteristic_name]
    if filter_name == "dn":
        conditions.append(CardCharacteristic.value_numeric == value)
    elif filter_name == "pressure_min":
        conditions.append(CardCharacteristic.value_numeric.is_not(None))
        conditions.append(CardCharacteristic.value_numeric >= value)
    elif filter_name == "building_length_max":
        conditions.append(CardCharacteristic.value_numeric.is_not(None))
        conditions.append(CardCharacteristic.value_numeric <= value)
    elif filter_name in {"temp_max", "design_temp_max"}:
        conditions.append(CardCharacteristic.range_max.is_not(None))
        conditions.append(CardCharacteristic.range_max >= value)
    elif filter_name in {"power_max", "open_time_max"}:
        conditions.append(CardCharacteristic.range_max.is_not(None))
        conditions.append(CardCharacteristic.range_max <= value)
    elif filter_name == "close_time_max":
        conditions.append(CardCharacteristic.value_numeric.is_not(None))
        conditions.append(CardCharacteristic.value_numeric <= value)
    elif filter_name == "service_life_min":
        conditions.append(CardCharacteristic.range_min.is_not(None))
        conditions.append(CardCharacteristic.range_min >= value)
    else:
        conditions.append(CardCharacteristic.value_text == value)

    return select(literal(1)).where(and_(*conditions)).exists()
