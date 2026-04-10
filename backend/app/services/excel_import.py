from __future__ import annotations

import hashlib
import logging
import math
import re
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from io import BytesIO
from typing import Any

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.card_characteristic import CardCharacteristic, CharacteristicType
from app.models.import_batch import ImportBatch
from app.models.import_error import ImportError
from app.models.mtr_card import MtrCard
from app.utils.normalizers import compact_spaces, normalize_column_name, normalize_empty
from app.utils.parsers import make_json_safe

logger = logging.getLogger(__name__)

MAIN_FIELDS = {
    "guid": {"guid"},
    "name": {"наименование"},
    "manufacturer_inn": {"инн изготовителя"},
    "manufacturer_inio": {"инио изготовителя"},
    "country_code": {"страна регистрации изготовителя код оксм", "страна регистрации изготовителя код оксм"},
    "article": {"артикул"},
    "price": {"цена exw без ндс"},
    "price_date_start": {"дата начала действия цены"},
    "price_date_end": {"плановая дата окончания действия цены"},
    "description": {"описание"},
}
MAIN_FIELD_LAST_INDEX = 10
CHARACTERISTICS_START_INDEX = 11
EMPTY_CHARACTERISTIC_MARKERS = {"", "-", "00", "00/00"}


class DuplicateImportError(ValueError):
    """Raised when the same Excel file content is uploaded more than once."""


@dataclass
class ParsedCharacteristic:
    char_name: str
    char_value_raw: str | None
    char_unit: str | None
    char_type: CharacteristicType
    value_numeric: Decimal | None = None
    range_min: Decimal | None = None
    range_max: Decimal | None = None
    value_text: str | None = None


class ExcelImportService:
    def __init__(self, db: Session):
        self.db = db

    def import_excel(self, file_name: str, content: bytes) -> ImportBatch:
        if not file_name.lower().endswith(".xlsx"):
            raise ValueError("Only .xlsx files are supported")

        file_checksum = hashlib.sha256(content).hexdigest()
        existing_batch = self.db.scalar(
            select(ImportBatch).where(ImportBatch.file_checksum == file_checksum)
        )
        if existing_batch is not None and existing_batch.status != "failed":
            raise DuplicateImportError("Этот Excel-файл уже был загружен ранее.")

        batch = ImportBatch(
            file_name=file_name,
            file_checksum=file_checksum,
            status="processing",
        )
        self.db.add(batch)
        self.db.flush()

        try:
            meta_info, header_row_number, headers, data_frame = self._read_excel(content)
            logger.info(
                "Importing BRIF cards for batch=%s class_meta=%s",
                batch.id,
                meta_info,
            )

            batch.rows_total = len(data_frame.index)
            field_indexes = self._build_main_field_indexes(headers)

            rows_success = 0
            rows_error = 0
            rows_duplicate = 0
            seen_guids: set[str] = set()
            characteristic_mappings: list[dict[str, Any]] = []

            for row_offset, row_values in enumerate(data_frame.values.tolist(), start=1):
                excel_row_number = header_row_number + row_offset + 1
                raw_row_json = self._serialize_row(headers, row_values)
                try:
                    card_payload = self._parse_card_row(row_values, field_indexes)
                    guid = card_payload["guid"]

                    if guid in seen_guids or self._guid_exists(guid):
                        rows_duplicate += 1
                        logger.info(
                            "Duplicate MTR card skipped for batch=%s row=%s guid=%s",
                            batch.id,
                            excel_row_number,
                            guid,
                        )
                        continue

                    seen_guids.add(guid)
                    card = MtrCard(batch_id=batch.id, raw_row_json=raw_row_json, **card_payload)
                    self.db.add(card)
                    self.db.flush()

                    parsed_characteristics = self._parse_characteristics(row_values, headers)
                    for characteristic in parsed_characteristics:
                        characteristic_mappings.append(
                            {
                                "card_id": card.id,
                                "char_name": characteristic.char_name,
                                "char_value_raw": characteristic.char_value_raw,
                                "char_unit": characteristic.char_unit,
                                "char_type": characteristic.char_type.value,
                                "value_numeric": characteristic.value_numeric,
                                "range_min": characteristic.range_min,
                                "range_max": characteristic.range_max,
                                "value_text": characteristic.value_text,
                            }
                        )

                    if len(characteristic_mappings) >= 1000:
                        self.db.bulk_insert_mappings(CardCharacteristic, characteristic_mappings)
                        characteristic_mappings.clear()

                    rows_success += 1
                except Exception as exc:
                    rows_error += 1
                    self.db.add(
                        ImportError(
                            batch_id=batch.id,
                            row_number=excel_row_number,
                            error_message=str(exc),
                            raw_row_json=raw_row_json,
                        )
                    )
                    logger.warning(
                        "Import row error for batch=%s row=%s: %s",
                        batch.id,
                        excel_row_number,
                        exc,
                    )

            if characteristic_mappings:
                self.db.bulk_insert_mappings(CardCharacteristic, characteristic_mappings)

            batch.rows_success = rows_success
            batch.rows_error = rows_error
            batch.rows_duplicate = rows_duplicate
            batch.status = self._resolve_batch_status(rows_error, rows_duplicate)
            self.db.commit()
            self.db.refresh(batch)
            return batch
        except Exception as exc:
            logger.exception("Import batch failed for file %s", file_name)
            batch.status = "failed"
            self.db.add(
                ImportError(
                    batch_id=batch.id,
                    row_number=0,
                    error_message=f"File import failed: {exc}",
                    raw_row_json={},
                )
            )
            self.db.commit()
            self.db.refresh(batch)
            return batch

    def _read_excel(self, content: bytes) -> tuple[dict[str, str | None], int, list[str], pd.DataFrame]:
        raw_df = pd.read_excel(
            BytesIO(content),
            sheet_name=0,
            header=None,
            dtype=object,
            engine="openpyxl",
        )
        header_idx = self._detect_header_row(raw_df)
        if header_idx is None:
            raise ValueError("Не удалось определить строку заголовков в Excel.")

        headers = [self._stringify_cell(value) or "" for value in raw_df.iloc[header_idx].tolist()]
        meta_info = self._extract_meta_info(raw_df, header_idx)
        data_frame = raw_df.iloc[header_idx + 1 :].copy()
        data_frame.columns = [str(index) for index in range(len(headers))]
        data_frame = data_frame.dropna(how="all").reset_index(drop=True)
        return meta_info, header_idx, headers, data_frame

    def _detect_header_row(self, raw_df: pd.DataFrame) -> int | None:
        max_scan_rows = min(len(raw_df.index), 10)
        for index in range(max_scan_rows):
            row = [normalize_column_name(value) for value in raw_df.iloc[index].tolist()]
            if "guid" in row and "наименование" in row:
                return index
        return None

    def _extract_meta_info(self, raw_df: pd.DataFrame, header_idx: int) -> dict[str, str | None]:
        if header_idx == 0:
            return {"class_name": None, "class_guid": None, "raw": None}

        raw_meta = " | ".join(
            filter(
                None,
                [self._stringify_cell(value) for value in raw_df.iloc[header_idx - 1].tolist()],
            )
        )
        if not raw_meta:
            return {"class_name": None, "class_guid": None, "raw": None}

        guid_match = re.search(r"([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})", raw_meta)
        class_name_match = re.search(r"Класс\s+МТР\s*\|?\s*(.+?)(?:\s*\|\s*[0-9a-fA-F-]{36})?$", raw_meta, flags=re.IGNORECASE)
        return {
            "class_name": compact_spaces(class_name_match.group(1)) if class_name_match else None,
            "class_guid": guid_match.group(1) if guid_match else None,
            "raw": raw_meta,
        }

    def _build_main_field_indexes(self, headers: list[str]) -> dict[str, int]:
        indexes: dict[str, int] = {}
        for index, header in enumerate(headers[: MAIN_FIELD_LAST_INDEX + 1]):
            normalized = normalize_column_name(header)
            for field_name, aliases in MAIN_FIELDS.items():
                if normalized in aliases and field_name not in indexes:
                    indexes[field_name] = index

        missing = [field for field in ("guid", "name") if field not in indexes]
        if missing:
            raise ValueError(f"В Excel отсутствуют обязательные колонки: {', '.join(missing)}")
        return indexes

    def _parse_card_row(self, row_values: list[Any], field_indexes: dict[str, int]) -> dict[str, Any]:
        guid = self._parse_guid(self._value_by_index(row_values, field_indexes.get("guid")))
        name = compact_spaces(self._value_by_index(row_values, field_indexes.get("name")))
        if not name:
            raise ValueError("Пустое наименование карточки.")

        return {
            "guid": guid,
            "name": name,
            "manufacturer_inn": self._clean_text(self._value_by_index(row_values, field_indexes.get("manufacturer_inn"))),
            "manufacturer_inio": self._clean_text(self._value_by_index(row_values, field_indexes.get("manufacturer_inio"))),
            "country_code": self._clean_text(self._value_by_index(row_values, field_indexes.get("country_code"))),
            "article": self._clean_text(self._value_by_index(row_values, field_indexes.get("article"))),
            "price": self._parse_price(self._value_by_index(row_values, field_indexes.get("price"))),
            "price_date_start": self._parse_brif_date(self._value_by_index(row_values, field_indexes.get("price_date_start"))),
            "price_date_end": self._parse_brif_date(self._value_by_index(row_values, field_indexes.get("price_date_end"))),
            "description": self._clean_text(self._value_by_index(row_values, field_indexes.get("description"))),
        }

    def _parse_characteristics(self, row_values: list[Any], headers: list[str]) -> list[ParsedCharacteristic]:
        characteristics: list[ParsedCharacteristic] = []
        for index in range(CHARACTERISTICS_START_INDEX, len(headers), 2):
            raw_header = headers[index] if index < len(headers) else ""
            char_name = self._cleanup_characteristic_name(raw_header)
            if not char_name:
                continue

            raw_value = self._stringify_cell(row_values[index] if index < len(row_values) else None)
            raw_unit = self._stringify_cell(row_values[index + 1] if index + 1 < len(row_values) else None)
            char_type = self._detect_characteristic_type(raw_header)

            try:
                characteristics.append(
                    self._parse_characteristic_value(
                        char_name=char_name,
                        raw_value=raw_value,
                        raw_unit=raw_unit,
                        char_type=char_type,
                    )
                )
            except Exception as exc:
                logger.warning(
                    "Characteristic parsing error: name=%s value=%s reason=%s",
                    char_name,
                    raw_value,
                    exc,
                )
                characteristics.append(
                    ParsedCharacteristic(
                        char_name=char_name,
                        char_value_raw=raw_value,
                        char_unit=raw_unit,
                        char_type=char_type,
                        value_text=raw_value,
                    )
                )
        return characteristics

    def _parse_characteristic_value(
        self,
        *,
        char_name: str,
        raw_value: str | None,
        raw_unit: str | None,
        char_type: CharacteristicType,
    ) -> ParsedCharacteristic:
        normalized_raw = self._normalize_characteristic_raw_value(raw_value)
        characteristic = ParsedCharacteristic(
            char_name=char_name,
            char_value_raw=normalized_raw,
            char_unit=self._clean_text(raw_unit),
            char_type=char_type,
        )
        if normalized_raw is None:
            return characteristic

        if char_type == CharacteristicType.NUMBER:
            characteristic.value_numeric = self._parse_decimal(normalized_raw)
            return characteristic

        if char_type == CharacteristicType.RANGE:
            characteristic.range_min, characteristic.range_max = self._parse_range(normalized_raw)
            return characteristic

        if char_type == CharacteristicType.MULTIVALUE:
            parts = [item.strip() for item in normalized_raw.split(";") if item.strip()]
            characteristic.value_text = ";".join(parts) if parts else None
            return characteristic

        characteristic.value_text = normalized_raw
        return characteristic

    def _normalize_characteristic_raw_value(self, value: str | None) -> str | None:
        text = self._clean_text(value)
        if text is None:
            return None
        if text in EMPTY_CHARACTERISTIC_MARKERS:
            return None
        return text

    def _cleanup_characteristic_name(self, raw_header: str | None) -> str:
        header = self._clean_text(raw_header)
        if header is None:
            return ""
        header = re.sub(r"\s*Тип данных\s*-\s*.*$", "", header, flags=re.IGNORECASE)
        header = re.sub(r"\s*\(.*?(диапазон|список|набор значений|вещественное число|строка).*?\)\s*$", "", header, flags=re.IGNORECASE)
        header = re.sub(r"\s*укажите.*$", "", header, flags=re.IGNORECASE)
        return header.strip(" -")

    def _detect_characteristic_type(self, raw_header: str | None) -> CharacteristicType:
        header = (raw_header or "").lower()
        if "вещественное число" in header or "(вещественное число)" in header:
            return CharacteristicType.NUMBER
        if "диапазон" in header or "(диапазон)" in header:
            return CharacteristicType.RANGE
        if "набор значений" in header or "мультивыбор" in header:
            return CharacteristicType.MULTIVALUE
        if "список" in header:
            return CharacteristicType.LIST
        if "строка" in header:
            return CharacteristicType.STRING
        return CharacteristicType.STRING

    def _parse_guid(self, value: Any) -> str:
        text = self._clean_text(value)
        if text is None:
            raise ValueError("GUID карточки отсутствует.")
        if not re.fullmatch(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}", text):
            raise ValueError(f"Некорректный GUID карточки: {text}")
        return text.lower()

    def _parse_price(self, value: Any) -> Decimal | None:
        text = self._clean_text(value)
        if text is None:
            return None
        normalized = text.replace("\xa0", "").replace(" ", "")
        if re.fullmatch(r"\d{1,3}(,\d{3})+", normalized):
            normalized = normalized.replace(",", "")
        elif "," in normalized and "." not in normalized:
            normalized = normalized.replace(",", ".")
        normalized = re.sub(r"[^0-9.\-]", "", normalized)
        if not normalized:
            return None
        try:
            return Decimal(normalized).quantize(Decimal("0.01"))
        except InvalidOperation as exc:
            raise ValueError(f"Некорректная цена: {value}") from exc

    def _parse_decimal(self, value: Any) -> Decimal | None:
        if value is None:
            return None
        if isinstance(value, Decimal):
            return value.quantize(Decimal("0.0001"))
        if isinstance(value, (int, float)):
            if isinstance(value, float) and math.isnan(value):
                return None
            return Decimal(str(value)).quantize(Decimal("0.0001"))

        text = self._clean_text(value)
        if text is None or text == "00":
            return None
        normalized = text.replace("\xa0", "").replace(" ", "").replace(",", ".")
        normalized = re.sub(r"[^0-9.\-]", "", normalized)
        if not normalized:
            return None
        try:
            return Decimal(normalized).quantize(Decimal("0.0001"))
        except InvalidOperation as exc:
            raise ValueError(f"Некорректное числовое значение: {value}") from exc

    def _parse_range(self, value: str) -> tuple[Decimal | None, Decimal | None]:
        text = self._clean_text(value)
        if text is None or text == "00/00":
            return None, None
        parts = [part.strip() for part in text.split("/", 1)]
        if len(parts) != 2:
            parsed = self._parse_decimal(text)
            return parsed, parsed
        range_min = None if parts[0] in {"", "00", "-"} else self._parse_decimal(parts[0])
        range_max = None if parts[1] in {"", "00", "-"} else self._parse_decimal(parts[1])
        return range_min, range_max

    def _parse_brif_date(self, value: Any) -> date | None:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value

        text = self._clean_text(value)
        if text is None:
            return None
        for pattern in ("%Y.%m.%d", "%Y-%m-%d", "%d.%m.%Y"):
            try:
                return datetime.strptime(text, pattern).date()
            except ValueError:
                continue
        raise ValueError(f"Некорректная дата: {value}")

    def _serialize_row(self, headers: list[str], row_values: list[Any]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for index, header in enumerate(headers):
            key = header or f"column_{index}"
            result[key] = make_json_safe(row_values[index] if index < len(row_values) else None)
        return result

    def _guid_exists(self, guid: str) -> bool:
        return self.db.scalar(select(MtrCard.id).where(MtrCard.guid == guid)) is not None

    @staticmethod
    def _value_by_index(row_values: list[Any], index: int | None) -> Any:
        if index is None or index >= len(row_values):
            return None
        return row_values[index]

    @staticmethod
    def _stringify_cell(value: Any) -> str | None:
        if value is None:
            return None
        if isinstance(value, float) and math.isnan(value):
            return None
        if isinstance(value, datetime):
            return value.strftime("%Y.%m.%d")
        if isinstance(value, date):
            return value.isoformat()
        return str(value).strip()

    @staticmethod
    def _clean_text(value: Any) -> str | None:
        text = normalize_empty(value)
        if text is None:
            return None
        return compact_spaces(text)

    @staticmethod
    def _resolve_batch_status(rows_error: int, rows_duplicate: int) -> str:
        if rows_error > 0:
            return "completed_with_errors"
        if rows_duplicate > 0:
            return "completed_with_duplicates"
        return "completed"
