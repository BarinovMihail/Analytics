from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class UploadResponse(BaseModel):
    batch_id: int
    file_name: str
    status: str
    rows_total: int
    rows_success: int
    rows_error: int


class UploadBatchListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    file_name: str
    uploaded_at: datetime
    status: str
    rows_total: int
    rows_success: int
    rows_error: int


class ImportErrorItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    batch_id: int
    row_number: int
    error_message: str
    raw_row_json: dict[str, Any]
    created_at: datetime
