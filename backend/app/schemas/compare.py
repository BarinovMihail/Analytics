from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict


class CompareFilters(BaseModel):
    dn: Decimal | None = None
    pressure_min: Decimal | None = None
    temp_max: Decimal | None = None
    design_temp_max: Decimal | None = None
    connection_type: str | None = None
    valve_design: str | None = None
    control_type: str | None = None
    safety_class: str | None = None
    quality_category: str | None = None
    seismic_category: str | None = None
    power_max: Decimal | None = None
    close_time_max: Decimal | None = None
    open_time_max: Decimal | None = None
    body_material: str | None = None
    working_medium: str | None = None
    manufacturer_inn: str | None = None
    country_code: str | None = None
    price_max: Decimal | None = None
    price_date: date | None = None
    service_life_min: Decimal | None = None
    building_length_max: Decimal | None = None


class CompareRequest(BaseModel):
    task_name: str
    filters: CompareFilters


class CompareResponse(BaseModel):
    task_id: int
    task_name: str
    matched_cards: int
    total_cards: int
    status: str
    created_at: datetime


class CompareTaskDetail(CompareResponse):
    filter_params_json: dict[str, Any]
    output_file_path: str | None
    finished_at: datetime | None
