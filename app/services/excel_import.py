from __future__ import annotations

import logging
from io import BytesIO
from typing import Any

import pandas as pd
from pydantic import BaseModel, ValidationError, field_validator
from sqlalchemy.orm import Session

from app.models.import_batch import ImportBatch
from app.models.import_error import ImportError
from app.models.purchase import Purchase
from app.utils.normalizers import (
    compact_spaces,
    extract_email,
    extract_inn,
    extract_status_name,
    normalize_column_name,
    normalize_column_names,
    normalize_empty,
    split_classifier,
)
from app.utils.parsers import make_json_safe, parse_amount, parse_date

logger = logging.getLogger(__name__)


COLUMN_ALIASES: dict[str, set[str]] = {
    "item_name": {"наименование продукции", "наименование товара", "товар", "продукция"},
    "item_code": {"артикул", "код товара", "код продукции", "обозначение", "артикул товара"},
    "supplier_name": {"наименование поставщика", "поставщик", "supplier", "поставщик/контрагент"},
    "category": {"классификатор окпд2", "окпд2", "код окпд2"},
    "category_mtrio": {"классификатор мтрио", "мтрио", "класс мтрио"},
    "unit_name": {"базовая единица измерения", "единица измерения", "ед. изм"},
    "origin_country": {"страна происхождения", "страна"},
    "status_text": {"статус продукции", "статус", "состояние"},
    "amount": {"цена exw без ндс", "сумма", "стоимость", "цена", "amount"},
    "delivery_date": {
        "дата окончания действия цены",
        "дата поставки",
        "срок поставки",
        "delivery date",
    },
    "manufacturer_name": {"наименование изготовителя", "изготовитель", "manufacturer"},
    "developer_name": {"разработчик", "developer"},
    "customer_inn": {"инн заказчика", "заказчик инн", "customer inn"},
    "supplier_contact": {"контакт поставщика", "supplier contact", "контакт"},
    "supplier_email": {"email", "e-mail", "почта поставщика", "supplier email"},
}


class PurchasePayload(BaseModel):
    item_code: str | None
    item_name: str
    category_code: str | None
    category_name: str | None
    purchase_date: Any | None
    supplier_name: str
    supplier_inn: str | None
    supplier_contact: str | None
    supplier_email: str | None
    customer_inn: str | None
    amount: Any | None
    delivery_date: Any | None
    status: str | None
    unit_name: str | None
    origin_country: str | None
    manufacturer_name: str | None
    developer_name: str | None

    @field_validator("item_name", "supplier_name")
    @classmethod
    def validate_required_strings(cls, value: str) -> str:
        normalized = compact_spaces(value)
        if not normalized:
            raise ValueError("Field is required")
        return normalized

    @field_validator("amount", mode="before")
    @classmethod
    def validate_amount(cls, value: Any) -> Any:
        return parse_amount(value)

    @field_validator("purchase_date", "delivery_date", mode="before")
    @classmethod
    def validate_date(cls, value: Any) -> Any:
        return parse_date(value)

    @field_validator(
        "item_code",
        "category_code",
        "category_name",
        "supplier_inn",
        "supplier_contact",
        "supplier_email",
        "customer_inn",
        "status",
        "unit_name",
        "origin_country",
        "manufacturer_name",
        "developer_name",
        mode="before",
    )
    @classmethod
    def normalize_optional_strings(cls, value: Any) -> Any:
        return compact_spaces(value)


class ExcelImportService:
    def __init__(self, db: Session):
        self.db = db

    def import_excel(self, file_name: str, content: bytes) -> ImportBatch:
        if not file_name.lower().endswith(".xlsx"):
            raise ValueError("Only .xlsx files are supported")

        batch = ImportBatch(file_name=file_name, status="processing")
        self.db.add(batch)
        self.db.flush()

        try:
            data_frame, header_row_number = self._read_excel(content)
            batch.rows_total = len(data_frame.index)
            column_mapping = self._build_column_mapping(list(data_frame.columns))

            rows_success = 0
            rows_error = 0

            for offset, row in enumerate(data_frame.to_dict(orient="records"), start=1):
                excel_row_number = header_row_number + offset
                raw_row_json = self._serialize_row(row)
                try:
                    mapped_row = map_row_to_purchase(row, column_mapping)
                    payload = PurchasePayload.model_validate(mapped_row)
                    purchase = Purchase(
                        batch_id=batch.id,
                        raw_row_json=raw_row_json,
                        **payload.model_dump(),
                    )
                    self.db.add(purchase)
                    rows_success += 1
                except (ValidationError, ValueError) as exc:
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

            batch.rows_success = rows_success
            batch.rows_error = rows_error
            batch.status = "completed" if rows_error == 0 else "completed_with_errors"
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

    def _read_excel(self, content: bytes) -> tuple[pd.DataFrame, int]:
        raw_df = pd.read_excel(
            BytesIO(content),
            sheet_name=0,
            header=None,
            dtype=object,
            engine="openpyxl",
        )
        header_idx = self._detect_header_row(raw_df)
        if header_idx is None:
            raise ValueError("Failed to detect header row in Excel sheet")

        headers = normalize_column_names(raw_df.iloc[header_idx].tolist())
        data_frame = raw_df.iloc[header_idx + 1 :].copy()
        data_frame.columns = headers
        data_frame = data_frame.dropna(how="all").reset_index(drop=True)
        return data_frame, header_idx + 1

    def _detect_header_row(self, raw_df: pd.DataFrame) -> int | None:
        best_match: tuple[int, int] | None = None
        for index in range(min(len(raw_df.index), 15)):
            normalized_row = normalize_column_names(raw_df.iloc[index].tolist())
            score = 0
            for header in normalized_row:
                if any(header in aliases for aliases in COLUMN_ALIASES.values()):
                    score += 1
            if best_match is None or score > best_match[1]:
                best_match = (index, score)
        if best_match and best_match[1] >= 3:
            return best_match[0]
        return None

    def _build_column_mapping(self, columns: list[str]) -> dict[str, str]:
        mapping: dict[str, str] = {}
        for column in columns:
            normalized_column = normalize_column_name(column)
            for field_name, aliases in COLUMN_ALIASES.items():
                if normalized_column in aliases and field_name not in mapping:
                    mapping[field_name] = column
        return mapping

    def _serialize_row(self, row: dict[str, Any]) -> dict[str, Any]:
        return {str(key): make_json_safe(value) for key, value in row.items()}


def map_row_to_purchase(row: dict[str, Any], column_mapping: dict[str, str]) -> dict[str, Any]:
    def get(field_name: str) -> Any:
        column = column_mapping.get(field_name)
        if column is None:
            return None
        return row.get(column)

    item_name = compact_spaces(get("item_name"))
    supplier_name = compact_spaces(get("supplier_name"))
    status_text = compact_spaces(get("status_text"))
    category_code, category_name = split_classifier(get("category"))

    manufacturer_name = compact_spaces(get("manufacturer_name"))
    developer_name = compact_spaces(get("developer_name"))
    supplier_contact = compact_spaces(get("supplier_contact"))
    supplier_email = compact_spaces(get("supplier_email")) or extract_email(status_text)

    supplier_inn = (
        extract_inn(get("supplier_name"))
        or extract_inn(manufacturer_name)
        or extract_inn(developer_name)
    )

    purchase_date = parse_date(status_text) if status_text else None

    return {
        "item_code": normalize_empty(get("item_code")),
        "item_name": item_name,
        "category_code": category_code,
        "category_name": category_name,
        "purchase_date": purchase_date,
        "supplier_name": supplier_name,
        "supplier_inn": supplier_inn,
        "supplier_contact": supplier_contact,
        "supplier_email": supplier_email,
        "customer_inn": normalize_empty(get("customer_inn")),
        "amount": get("amount"),
        "delivery_date": get("delivery_date"),
        "status": extract_status_name(status_text),
        "unit_name": normalize_empty(get("unit_name")),
        "origin_country": normalize_empty(get("origin_country")),
        "manufacturer_name": manufacturer_name,
        "developer_name": developer_name,
    }
