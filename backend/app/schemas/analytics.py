from __future__ import annotations

from datetime import date
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class AnalyticsSummaryResponse(BaseModel):
    total_purchases_count: int
    total_amount: Decimal
    unique_suppliers: int
    latest_purchase_date: date | None


class SupplierAnalyticsItem(BaseModel):
    supplier_name: str
    purchases_count: int
    total_amount: Decimal


class MonthAnalyticsItem(BaseModel):
    year_month: str
    purchases_count: int
    total_amount: Decimal


class CategoryAnalyticsItem(BaseModel):
    category_name: str
    purchases_count: int
    total_amount: Decimal


class StatusAnalyticsItem(BaseModel):
    status: str
    purchases_count: int
    total_amount: Decimal


class SupplierPurchaseItem(BaseModel):
    id: int
    batch_id: int
    item_name: str
    item_code: str | None
    category_name: str | None
    amount: Decimal | None
    purchase_date: date | None
    delivery_date: date | None
    status: str | None
    created_at: datetime
