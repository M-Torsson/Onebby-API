# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

"""Backfill EAN from reference and ensure index

Revision ID: 7c8b1a4f3c32
Revises: 6f1b4d2c9e10
Create Date: 2026-01-11
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "7c8b1a4f3c32"
down_revision: Union[str, None] = "6f1b4d2c9e10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Backfill ean from numeric reference when ean is null
    op.execute(
        """
        UPDATE products
        SET ean = reference
        WHERE ean IS NULL
          AND reference ~ '^[0-9]{8,14}$';
        """
    )

    # Ensure index/unique on ean (allows NULLs)
    try:
        op.create_index("ix_products_ean_unique", "products", ["ean"], unique=True)
    except Exception:
        # Ignore if index already exists or duplicate rows block creation
        pass


def downgrade() -> None:
    try:
        op.drop_index("ix_products_ean_unique", table_name="products")
    except Exception:
        pass
