from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ComparisonTask(Base):
    __tablename__ = "comparison_tasks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    filter_params_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    total_cards: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    matched_cards: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    output_file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="created", index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
