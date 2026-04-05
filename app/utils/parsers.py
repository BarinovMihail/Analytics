from __future__ import annotations

import math
import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any

from app.utils.normalizers import normalize_empty


def parse_amount(value: Any) -> Decimal | None:
    normalized = normalize_empty(value)
    if normalized is None:
        return None
    if isinstance(normalized, Decimal):
        return normalized
    if isinstance(normalized, (int, float)):
        if isinstance(normalized, float) and math.isnan(normalized):
            return None
        return Decimal(str(normalized)).quantize(Decimal("0.01"))

    text = str(normalized)
    text = text.replace("\xa0", " ").replace(" ", "")
    text = text.replace(",", ".")
    text = re.sub(r"[^0-9.\-]", "", text)
    if not text:
        return None
    try:
        return Decimal(text).quantize(Decimal("0.01"))
    except InvalidOperation as exc:
        raise ValueError(f"Invalid amount value: {value}") from exc


def parse_date(value: Any) -> date | None:
    normalized = normalize_empty(value)
    if normalized is None:
        return None
    if isinstance(normalized, datetime):
        return normalized.date()
    if isinstance(normalized, date):
        return normalized

    text = str(normalized).strip()
    if text.lower() in {"бессрочно", "не указано"}:
        return None

    date_patterns = [
        "%d.%m.%Y",
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%d.%m.%y",
    ]
    for pattern in date_patterns:
        try:
            return datetime.strptime(text, pattern).date()
        except ValueError:
            continue

    embedded = re.search(r"\b(\d{2}\.\d{2}\.\d{4})\b", text)
    if embedded:
        return datetime.strptime(embedded.group(1), "%d.%m.%Y").date()

    raise ValueError(f"Invalid date value: {value}")


def make_json_safe(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, float) and math.isnan(value):
        return None
    return value
