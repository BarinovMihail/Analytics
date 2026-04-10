"""replace purchases with mtr cards

Revision ID: 20260410_0004
Revises: 20260406_0003
Create Date: 2026-04-10 00:00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
from sqlalchemy.engine.reflection import Inspector


revision = "20260410_0004"
down_revision = "20260406_0003"
branch_labels = None
depends_on = None


characteristic_type_enum = sa.Enum(
    "number",
    "range",
    "list",
    "multivalue",
    "string",
    name="characteristic_type_enum",
)


def _inspector() -> Inspector:
    return sa.inspect(op.get_bind())


def _has_table(table_name: str) -> bool:
    return table_name in _inspector().get_table_names()


def _has_index(table_name: str, index_name: str) -> bool:
    if not _has_table(table_name):
        return False
    return any(index["name"] == index_name for index in _inspector().get_indexes(table_name))


def _drop_index_if_exists(table_name: str, index_name: str) -> None:
    if _has_index(table_name, index_name):
        op.drop_index(index_name, table_name=table_name)


def upgrade() -> None:
    if _has_table("purchases"):
        _drop_index_if_exists("purchases", "ix_purchases_row_fingerprint")
        _drop_index_if_exists("purchases", "ix_purchases_status")
        _drop_index_if_exists("purchases", "ix_purchases_amount")
        _drop_index_if_exists("purchases", "ix_purchases_customer_inn")
        _drop_index_if_exists("purchases", "ix_purchases_supplier_inn")
        _drop_index_if_exists("purchases", "ix_purchases_supplier_name")
        _drop_index_if_exists("purchases", "ix_purchases_purchase_date")
        _drop_index_if_exists("purchases", "ix_purchases_category_name")
        _drop_index_if_exists("purchases", "ix_purchases_category_code")
        _drop_index_if_exists("purchases", "ix_purchases_item_name")
        _drop_index_if_exists("purchases", "ix_purchases_item_code")
        _drop_index_if_exists("purchases", "ix_purchases_batch_id")
        _drop_index_if_exists("purchases", "ix_purchases_id")
        op.drop_table("purchases")

    if not _has_table("mtr_cards"):
        op.create_table(
            "mtr_cards",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("batch_id", sa.Integer(), sa.ForeignKey("import_batches.id"), nullable=False),
            sa.Column("guid", sa.String(length=36), nullable=False),
            sa.Column("name", sa.Text(), nullable=False),
            sa.Column("manufacturer_inn", sa.String(length=20), nullable=True),
            sa.Column("manufacturer_inio", sa.String(length=50), nullable=True),
            sa.Column("country_code", sa.String(length=10), nullable=True),
            sa.Column("article", sa.String(length=255), nullable=True),
            sa.Column("price", sa.Numeric(precision=18, scale=2), nullable=True),
            sa.Column("price_date_start", sa.Date(), nullable=True),
            sa.Column("price_date_end", sa.Date(), nullable=True),
            sa.Column("description", mysql.LONGTEXT(), nullable=True),
            sa.Column("raw_row_json", sa.JSON(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.UniqueConstraint("guid", name="uq_mtr_cards_guid"),
        )
    if not _has_index("mtr_cards", "ix_mtr_cards_id"):
        op.create_index("ix_mtr_cards_id", "mtr_cards", ["id"])
    if not _has_index("mtr_cards", "ix_mtr_cards_batch_id"):
        op.create_index("ix_mtr_cards_batch_id", "mtr_cards", ["batch_id"])
    if not _has_index("mtr_cards", "ix_mtr_cards_guid"):
        op.create_index("ix_mtr_cards_guid", "mtr_cards", ["guid"])
    if not _has_index("mtr_cards", "ix_mtr_cards_country_code"):
        op.create_index("ix_mtr_cards_country_code", "mtr_cards", ["country_code"])
    if not _has_index("mtr_cards", "ix_mtr_cards_manufacturer_inn"):
        op.create_index("ix_mtr_cards_manufacturer_inn", "mtr_cards", ["manufacturer_inn"])
    if not _has_index("mtr_cards", "ix_mtr_cards_article"):
        op.create_index("ix_mtr_cards_article", "mtr_cards", ["article"])
    if not _has_index("mtr_cards", "ix_mtr_cards_price"):
        op.create_index("ix_mtr_cards_price", "mtr_cards", ["price"])
    if not _has_index("mtr_cards", "ix_mtr_cards_name"):
        op.create_index("ix_mtr_cards_name", "mtr_cards", ["name"], mysql_length=255)

    characteristic_type_enum.create(op.get_bind(), checkfirst=True)
    if not _has_table("card_characteristics"):
        op.create_table(
            "card_characteristics",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("card_id", sa.Integer(), sa.ForeignKey("mtr_cards.id"), nullable=False),
            sa.Column("char_name", sa.String(length=500), nullable=False),
            sa.Column("char_value_raw", sa.Text(), nullable=True),
            sa.Column("char_unit", sa.String(length=100), nullable=True),
            sa.Column("char_type", characteristic_type_enum, nullable=False),
            sa.Column("value_numeric", sa.Numeric(precision=18, scale=4), nullable=True),
            sa.Column("range_min", sa.Numeric(precision=18, scale=4), nullable=True),
            sa.Column("range_max", sa.Numeric(precision=18, scale=4), nullable=True),
            sa.Column("value_text", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        )
    if not _has_index("card_characteristics", "ix_card_characteristics_id"):
        op.create_index("ix_card_characteristics_id", "card_characteristics", ["id"])
    if not _has_index("card_characteristics", "ix_card_characteristics_card_id"):
        op.create_index("ix_card_characteristics_card_id", "card_characteristics", ["card_id"])
    if not _has_index("card_characteristics", "ix_card_characteristics_char_name"):
        op.create_index("ix_card_characteristics_char_name", "card_characteristics", ["char_name"], mysql_length=255)
    if not _has_index("card_characteristics", "ix_card_characteristics_value_numeric"):
        op.create_index("ix_card_characteristics_value_numeric", "card_characteristics", ["value_numeric"])

    if not _has_table("comparison_tasks"):
        op.create_table(
            "comparison_tasks",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("filter_params_json", sa.JSON(), nullable=False),
            sa.Column("total_cards", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("matched_cards", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("output_file_path", sa.String(length=500), nullable=True),
            sa.Column("status", sa.String(length=20), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        )
    if not _has_index("comparison_tasks", "ix_comparison_tasks_id"):
        op.create_index("ix_comparison_tasks_id", "comparison_tasks", ["id"])
    if not _has_index("comparison_tasks", "ix_comparison_tasks_name"):
        op.create_index("ix_comparison_tasks_name", "comparison_tasks", ["name"])
    if not _has_index("comparison_tasks", "ix_comparison_tasks_status"):
        op.create_index("ix_comparison_tasks_status", "comparison_tasks", ["status"])


def downgrade() -> None:
    op.drop_index("ix_comparison_tasks_status", table_name="comparison_tasks")
    op.drop_index("ix_comparison_tasks_name", table_name="comparison_tasks")
    op.drop_index("ix_comparison_tasks_id", table_name="comparison_tasks")
    op.drop_table("comparison_tasks")

    op.drop_index("ix_card_characteristics_value_numeric", table_name="card_characteristics")
    op.drop_index("ix_card_characteristics_char_name", table_name="card_characteristics")
    op.drop_index("ix_card_characteristics_card_id", table_name="card_characteristics")
    op.drop_index("ix_card_characteristics_id", table_name="card_characteristics")
    op.drop_table("card_characteristics")
    characteristic_type_enum.drop(op.get_bind(), checkfirst=True)

    op.drop_index("ix_mtr_cards_name", table_name="mtr_cards")
    op.drop_index("ix_mtr_cards_price", table_name="mtr_cards")
    op.drop_index("ix_mtr_cards_article", table_name="mtr_cards")
    op.drop_index("ix_mtr_cards_manufacturer_inn", table_name="mtr_cards")
    op.drop_index("ix_mtr_cards_country_code", table_name="mtr_cards")
    op.drop_index("ix_mtr_cards_guid", table_name="mtr_cards")
    op.drop_index("ix_mtr_cards_batch_id", table_name="mtr_cards")
    op.drop_index("ix_mtr_cards_id", table_name="mtr_cards")
    op.drop_table("mtr_cards")

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
        sa.Column("row_fingerprint", sa.String(length=64), nullable=True),
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
    op.create_index("ix_purchases_row_fingerprint", "purchases", ["row_fingerprint"])
