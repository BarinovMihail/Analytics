from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.analytics import (
    AnalyticsSummaryResponse,
    CategoryAnalyticsItem,
    MonthAnalyticsItem,
    StatusAnalyticsItem,
    SupplierAnalyticsItem,
)
from app.services.analytics import AnalyticsService

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/summary", response_model=AnalyticsSummaryResponse)
def analytics_summary(
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    supplier_name: str | None = Query(default=None),
    category_name: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> AnalyticsSummaryResponse:
    service = AnalyticsService(db)
    return service.get_summary(date_from, date_to, supplier_name, category_name)


@router.get("/by-suppliers", response_model=list[SupplierAnalyticsItem])
def analytics_by_suppliers(
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    supplier_name: str | None = Query(default=None),
    category_name: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[SupplierAnalyticsItem]:
    service = AnalyticsService(db)
    return service.by_suppliers(date_from, date_to, supplier_name, category_name)


@router.get("/by-month", response_model=list[MonthAnalyticsItem])
def analytics_by_month(
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    supplier_name: str | None = Query(default=None),
    category_name: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[MonthAnalyticsItem]:
    service = AnalyticsService(db)
    return service.by_month(date_from, date_to, supplier_name, category_name)


@router.get("/by-category", response_model=list[CategoryAnalyticsItem])
def analytics_by_category(
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    supplier_name: str | None = Query(default=None),
    category_name: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[CategoryAnalyticsItem]:
    service = AnalyticsService(db)
    return service.by_category(date_from, date_to, supplier_name, category_name)


@router.get("/by-status", response_model=list[StatusAnalyticsItem])
def analytics_by_status(
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    supplier_name: str | None = Query(default=None),
    category_name: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[StatusAnalyticsItem]:
    service = AnalyticsService(db)
    return service.by_status(date_from, date_to, supplier_name, category_name)
