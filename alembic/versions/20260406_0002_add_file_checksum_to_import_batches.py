"""add file checksum to import batches

Revision ID: 20260406_0002
Revises: 20260405_0001
Create Date: 2026-04-06 00:00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260406_0002"
down_revision = "20260405_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "import_batches",
        sa.Column("file_checksum", sa.String(length=64), nullable=True),
    )
    op.create_index(
        "ix_import_batches_file_checksum",
        "import_batches",
        ["file_checksum"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_import_batches_file_checksum", table_name="import_batches")
    op.drop_column("import_batches", "file_checksum")
