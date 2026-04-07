"""initial schema"""

from alembic import op
import sqlalchemy as sa


revision = "20260405_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "import_batches",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("rows_total", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("rows_success", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("rows_error", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index("ix_import_batches_id", "import_batches", ["id"])

    op.create_table(
        "purchases",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("batch_id", sa.Integer(), sa.ForeignKey("import_batches.id"), nullable=False),
        sa.Column("item_code", sa.String(length=255), nullable=True),
        sa.Column("item_name", sa.String(length=500), nullable=False),
        sa.Column("category_code", sa.String(length=100), nullable=True),
        sa.Column("category_name", sa.String(length=255), nullable=True),
        sa.Column("purchase_date", sa.Date(), nullable=True),
        sa.Column("supplier_name", sa.String(length=255), nullable=False),
        sa.Column("supplier_inn", sa.String(length=32), nullable=True),
        sa.Column("supplier_contact", sa.String(length=255), nullable=True),
        sa.Column("supplier_email", sa.String(length=255), nullable=True),
        sa.Column("customer_inn", sa.String(length=32), nullable=True),
        sa.Column("amount", sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column("delivery_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(length=255), nullable=True),
        sa.Column("unit_name", sa.String(length=100), nullable=True),
        sa.Column("origin_country", sa.String(length=100), nullable=True),
        sa.Column("manufacturer_name", sa.String(length=255), nullable=True),
        sa.Column("developer_name", sa.String(length=255), nullable=True),
        sa.Column("raw_row_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_purchases_id", "purchases", ["id"])
    op.create_index("ix_purchases_batch_id", "purchases", ["batch_id"])
    op.create_index("ix_purchases_item_code", "purchases", ["item_code"])
    op.create_index("ix_purchases_item_name", "purchases", ["item_name"])
    op.create_index("ix_purchases_category_code", "purchases", ["category_code"])
    op.create_index("ix_purchases_category_name", "purchases", ["category_name"])
    op.create_index("ix_purchases_purchase_date", "purchases", ["purchase_date"])
    op.create_index("ix_purchases_supplier_name", "purchases", ["supplier_name"])
    op.create_index("ix_purchases_supplier_inn", "purchases", ["supplier_inn"])
    op.create_index("ix_purchases_customer_inn", "purchases", ["customer_inn"])
    op.create_index("ix_purchases_amount", "purchases", ["amount"])
    op.create_index("ix_purchases_status", "purchases", ["status"])

    op.create_table(
        "import_errors",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("batch_id", sa.Integer(), sa.ForeignKey("import_batches.id"), nullable=False),
        sa.Column("row_number", sa.Integer(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=False),
        sa.Column("raw_row_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_import_errors_id", "import_errors", ["id"])
    op.create_index("ix_import_errors_batch_id", "import_errors", ["batch_id"])
    op.create_index("ix_import_errors_row_number", "import_errors", ["row_number"])


def downgrade() -> None:
    op.drop_index("ix_import_errors_row_number", table_name="import_errors")
    op.drop_index("ix_import_errors_batch_id", table_name="import_errors")
    op.drop_index("ix_import_errors_id", table_name="import_errors")
    op.drop_table("import_errors")

    op.drop_index("ix_purchases_status", table_name="purchases")
    op.drop_index("ix_purchases_amount", table_name="purchases")
    op.drop_index("ix_purchases_customer_inn", table_name="purchases")
    op.drop_index("ix_purchases_supplier_inn", table_name="purchases")
    op.drop_index("ix_purchases_supplier_name", table_name="purchases")
    op.drop_index("ix_purchases_purchase_date", table_name="purchases")
    op.drop_index("ix_purchases_category_name", table_name="purchases")
    op.drop_index("ix_purchases_category_code", table_name="purchases")
    op.drop_index("ix_purchases_item_name", table_name="purchases")
    op.drop_index("ix_purchases_item_code", table_name="purchases")
    op.drop_index("ix_purchases_batch_id", table_name="purchases")
    op.drop_index("ix_purchases_id", table_name="purchases")
    op.drop_table("purchases")

    op.drop_index("ix_import_batches_id", table_name="import_batches")
    op.drop_table("import_batches")
