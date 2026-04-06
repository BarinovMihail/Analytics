"""add purchase fingerprint and duplicate counters

Revision ID: 20260406_0003
Revises: 20260406_0002
Create Date: 2026-04-06 00:10:00
"""

from __future__ import annotations

import hashlib
import json

from alembic import op
import sqlalchemy as sa


revision = "20260406_0003"
down_revision = "20260406_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "import_batches",
        sa.Column("rows_duplicate", sa.Integer(), nullable=False, server_default="0"),
    )
    op.alter_column("import_batches", "rows_duplicate", server_default=None)

    op.add_column(
        "purchases",
        sa.Column("row_fingerprint", sa.String(length=64), nullable=True),
    )
    connection = op.get_bind()
    rows = connection.execute(
        sa.text(
            """
            SELECT
                id,
                item_code,
                item_name,
                supplier_name,
                amount,
                purchase_date,
                delivery_date,
                status
            FROM purchases
            """
        )
    ).mappings()

    for row in rows:
        fingerprint_payload = {
            "item_code": row["item_code"] or "",
            "item_name": row["item_name"] or "",
            "supplier_name": row["supplier_name"] or "",
            "amount": str(row["amount"]) if row["amount"] is not None else "",
            "purchase_date": row["purchase_date"].isoformat() if row["purchase_date"] is not None else "",
            "delivery_date": row["delivery_date"].isoformat() if row["delivery_date"] is not None else "",
            "status": row["status"] or "",
        }
        serialized = json.dumps(
            fingerprint_payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        row_fingerprint = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        connection.execute(
            sa.text(
                """
                UPDATE purchases
                SET row_fingerprint = :row_fingerprint
                WHERE id = :purchase_id
                """
            ),
            {
                "row_fingerprint": row_fingerprint,
                "purchase_id": row["id"],
            },
        )

    op.create_index(
        "ix_purchases_row_fingerprint",
        "purchases",
        ["row_fingerprint"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_purchases_row_fingerprint", table_name="purchases")
    op.drop_column("purchases", "row_fingerprint")
    op.drop_column("import_batches", "rows_duplicate")
