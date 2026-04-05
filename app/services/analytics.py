from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import distinct, func, select
from sqlalchemy.orm import Session

from app.models.purchase import Purchase
from app.schemas.analytics import (
    AnalyticsSummaryResponse,
    CategoryAnalyticsItem,
    MonthAnalyticsItem,
    StatusAnalyticsItem,
    SupplierAnalyticsItem,
)


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def get_summary(
        self,
        date_from: date | None = None,
        date_to: date | None = None,
        supplier_name: str | None = None,
        category_name: str | None = None,
    ) -> AnalyticsSummaryResponse:
        filters = self._build_filters(date_from, date_to, supplier_name, category_name)
        query = select(
            func.count(Purchase.id),
            func.coalesce(func.sum(Purchase.amount), 0),
            func.count(distinct(Purchase.supplier_name)),
            func.max(Purchase.purchase_date),
        ).where(*filters)
        total_count, total_amount, unique_suppliers, latest_date = self.db.execute(query).one()
        return AnalyticsSummaryResponse(
            total_purchases_count=total_count or 0,
            total_amount=Decimal(total_amount or 0),
            unique_suppliers=unique_suppliers or 0,
            latest_purchase_date=latest_date,
        )

    def by_suppliers(
        self,
        date_from: date | None = None,
        date_to: date | None = None,
        supplier_name: str | None = None,
        category_name: str | None = None,
    ) -> list[SupplierAnalyticsItem]:
        filters = self._build_filters(date_from, date_to, supplier_name, category_name)
        query = (
            select(
                Purchase.supplier_name,
                func.count(Purchase.id).label("purchases_count"),
                func.coalesce(func.sum(Purchase.amount), 0).label("total_amount"),
            )
            .where(*filters)
            .where(Purchase.supplier_name.is_not(None))
            .group_by(Purchase.supplier_name)
            .order_by(func.sum(Purchase.amount).desc(), Purchase.supplier_name.asc())
        )
        return [
            SupplierAnalyticsItem(
                supplier_name=row.supplier_name,
                purchases_count=row.purchases_count,
                total_amount=Decimal(row.total_amount or 0),
            )
            for row in self.db.execute(query)
        ]

    def by_month(
        self,
        date_from: date | None = None,
        date_to: date | None = None,
        supplier_name: str | None = None,
        category_name: str | None = None,
    ) -> list[MonthAnalyticsItem]:
        filters = self._build_filters(date_from, date_to, supplier_name, category_name)
        year_month = func.date_format(Purchase.purchase_date, "%Y-%m")
        query = (
            select(
                year_month.label("year_month"),
                func.count(Purchase.id).label("purchases_count"),
                func.coalesce(func.sum(Purchase.amount), 0).label("total_amount"),
            )
            .where(*filters)
            .where(Purchase.purchase_date.is_not(None))
            .group_by(year_month)
            .order_by(year_month.asc())
        )
        return [
            MonthAnalyticsItem(
                year_month=row.year_month,
                purchases_count=row.purchases_count,
                total_amount=Decimal(row.total_amount or 0),
            )
            for row in self.db.execute(query)
        ]

    def by_category(
        self,
        date_from: date | None = None,
        date_to: date | None = None,
        supplier_name: str | None = None,
        category_name: str | None = None,
    ) -> list[CategoryAnalyticsItem]:
        filters = self._build_filters(date_from, date_to, supplier_name, category_name)
        query = (
            select(
                Purchase.category_name,
                func.count(Purchase.id).label("purchases_count"),
                func.coalesce(func.sum(Purchase.amount), 0).label("total_amount"),
            )
            .where(*filters)
            .where(Purchase.category_name.is_not(None))
            .group_by(Purchase.category_name)
            .order_by(func.sum(Purchase.amount).desc(), Purchase.category_name.asc())
        )
        return [
            CategoryAnalyticsItem(
                category_name=row.category_name,
                purchases_count=row.purchases_count,
                total_amount=Decimal(row.total_amount or 0),
            )
            for row in self.db.execute(query)
        ]

    def by_status(
        self,
        date_from: date | None = None,
        date_to: date | None = None,
        supplier_name: str | None = None,
        category_name: str | None = None,
    ) -> list[StatusAnalyticsItem]:
        filters = self._build_filters(date_from, date_to, supplier_name, category_name)
        query = (
            select(
                Purchase.status,
                func.count(Purchase.id).label("purchases_count"),
                func.coalesce(func.sum(Purchase.amount), 0).label("total_amount"),
            )
            .where(*filters)
            .where(Purchase.status.is_not(None))
            .group_by(Purchase.status)
            .order_by(func.sum(Purchase.amount).desc(), Purchase.status.asc())
        )
        return [
            StatusAnalyticsItem(
                status=row.status,
                purchases_count=row.purchases_count,
                total_amount=Decimal(row.total_amount or 0),
            )
            for row in self.db.execute(query)
        ]

    @staticmethod
    def _build_filters(
        date_from: date | None,
        date_to: date | None,
        supplier_name: str | None,
        category_name: str | None,
    ) -> list:
        filters = []
        if date_from is not None:
            filters.append(Purchase.purchase_date >= date_from)
        if date_to is not None:
            filters.append(Purchase.purchase_date <= date_to)
        if supplier_name:
            filters.append(Purchase.supplier_name.ilike(f"%{supplier_name.strip()}%"))
        if category_name:
            filters.append(Purchase.category_name.ilike(f"%{category_name.strip()}%"))
        return filters
