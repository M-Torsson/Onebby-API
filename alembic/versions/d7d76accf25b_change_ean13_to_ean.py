# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

"""change_ean13_to_ean

Revision ID: d7d76accf25b
Revises: 993e7110da86
Create Date: 2026-01-08 12:58:29.140428

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd7d76accf25b'
down_revision: Union[str, None] = '993e7110da86'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop old indexes
    op.drop_index('ix_products_ean13', table_name='products')
    op.drop_index('ix_product_variants_ean13', table_name='product_variants')
    
    # Rename columns
    op.alter_column('products', 'ean13', new_column_name='ean', type_=sa.String(255))
    op.alter_column('product_variants', 'ean13', new_column_name='ean', type_=sa.String(255))
    
    # Create new indexes
    op.create_index('ix_products_ean', 'products', ['ean'], unique=True)
    op.create_index('ix_product_variants_ean', 'product_variants', ['ean'], unique=True)


def downgrade() -> None:
    # Drop new indexes
    op.drop_index('ix_products_ean', table_name='products')
    op.drop_index('ix_product_variants_ean', table_name='product_variants')
    
    # Rename columns back
    op.alter_column('products', 'ean', new_column_name='ean13', type_=sa.String(13))
    op.alter_column('product_variants', 'ean', new_column_name='ean13', type_=sa.String(13))
    
    # Create old indexes
    op.create_index('ix_products_ean13', 'products', ['ean13'], unique=True)
    op.create_index('ix_product_variants_ean13', 'product_variants', ['ean13'], unique=True)
