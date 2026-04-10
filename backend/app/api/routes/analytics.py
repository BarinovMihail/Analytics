from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.analytics import (
    ConnectionTypeStat,
    DnStat,
    ManufacturerStat,
    PriceRangeStat,
    SafetyClassStat,
    SummaryResponse,
)
from app.services.analytics import AnalyticsService

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get(
    "/summary",
    response_model=SummaryResponse,
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {
                        "total_cards": 1500,
                        "unique_manufacturers": 32,
                        "cards_with_price": 1290,
                        "avg_price": "98124.33",
                        "last_upload_date": "2026-04-10T08:10:00Z",
                    }
                }
            }
        }
    },
)
def analytics_summary(db: Session = Depends(get_db)) -> SummaryResponse:
    return AnalyticsService(db).get_summary()


@router.get(
    "/by-manufacturer",
    response_model=list[ManufacturerStat],
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": [{"manufacturer_inn": "7701234567", "cards_count": 48}]
                }
            }
        }
    },
)
def analytics_by_manufacturer(db: Session = Depends(get_db)) -> list[ManufacturerStat]:
    return AnalyticsService(db).by_manufacturer()


@router.get(
    "/by-dn",
    response_model=list[DnStat],
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": [{"dn_value": "20.0000", "cards_count": 25}]
                }
            }
        }
    },
)
def analytics_by_dn(db: Session = Depends(get_db)) -> list[DnStat]:
    return AnalyticsService(db).by_dn()


@router.get(
    "/by-connection-type",
    response_model=list[ConnectionTypeStat],
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": [{"connection_type": "под приварку", "cards_count": 41}]
                }
            }
        }
    },
)
def analytics_by_connection_type(db: Session = Depends(get_db)) -> list[ConnectionTypeStat]:
    return AnalyticsService(db).by_connection_type()


@router.get(
    "/by-safety-class",
    response_model=list[SafetyClassStat],
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": [{"safety_class": "4", "cards_count": 58}]
                }
            }
        }
    },
)
def analytics_by_safety_class(db: Session = Depends(get_db)) -> list[SafetyClassStat]:
    return AnalyticsService(db).by_safety_class()


@router.get(
    "/price-range",
    response_model=list[PriceRangeStat],
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": [{"range_label": "100 000 - 999 999", "cards_count": 112}]
                }
            }
        }
    },
)
def analytics_price_range(db: Session = Depends(get_db)) -> list[PriceRangeStat]:
    return AnalyticsService(db).price_range()
