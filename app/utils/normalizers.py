from __future__ import annotations

import re
import unicodedata
from typing import Any


EMPTY_MARKERS = {"", "-", "nan", "none", "null", "nat"}


def normalize_empty(value: Any) -> Any | None:
    if value is None:
        return None
    if isinstance(value, str):
        cleaned = value.strip()
        if cleaned.lower() in EMPTY_MARKERS:
            return None
        return cleaned
    return value


def normalize_column_name(value: Any) -> str:
    if value is None:
        return ""
    normalized = normalize_empty(value)
    if normalized is None:
        return ""
    text = str(normalized).strip().lower()
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("ё", "е")
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^a-zа-я0-9\s%/()._-]", "", text)
    return text.strip(" ._-")


def normalize_column_names(values: list[Any]) -> list[str]:
    seen: dict[str, int] = {}
    result: list[str] = []
    for raw_value in values:
        normalized = normalize_column_name(raw_value)
        if not normalized:
            normalized = "unnamed"
        if normalized in seen:
            seen[normalized] += 1
            normalized = f"{normalized}_{seen[normalized]}"
        else:
            seen[normalized] = 0
        result.append(normalized)
    return result


def extract_inn(value: Any) -> str | None:
    text = normalize_empty(value)
    if text is None:
        return None
    match = re.search(r"\b(?:инн|inn)\s*[:.]?\s*(\d{10}|\d{12})\b", str(text), flags=re.IGNORECASE)
    if match:
        return match.group(1)
    digits = re.findall(r"\d{10,12}", str(text))
    return digits[0] if digits else None


def extract_email(value: Any) -> str | None:
    text = normalize_empty(value)
    if text is None:
        return None
    match = re.search(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", str(text), flags=re.IGNORECASE)
    return match.group(0) if match else None


def split_classifier(value: Any) -> tuple[str | None, str | None]:
    text = normalize_empty(value)
    if text is None:
        return None, None
    parts = [part.strip() for part in str(text).split(":", 1)]
    if len(parts) == 2:
        return parts[0] or None, parts[1] or None
    return None, str(text)


def compact_spaces(value: Any) -> str | None:
    text = normalize_empty(value)
    if text is None:
        return None
    return re.sub(r"\s+", " ", str(text)).strip()


def extract_status_name(value: Any) -> str | None:
    text = compact_spaces(value)
    if text is None:
        return None
    text = re.split(r"[.;]", text, maxsplit=1)[0].strip()
    if not text:
        return None
    match = re.match(r"^([^\d(]+)", text)
    if match:
        return match.group(1).strip()
    return text
