# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

"""add_delivery_tables_and_product_delivery_id

Revision ID: d7e8f9g0h1i2
Revises: a1b2c3d4e5f6
Create Date: 2026-02-08 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision: str = 'd7e8f9g0h1i2'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create deliveries table
    op.create_table(
        'deliveries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('days_from', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('days_to', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('option_note', sa.Text(), nullable=True),
        sa.Column('is_free_delivery', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=func.now(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_deliveries_id', 'deliveries', ['id'])
    
    # Create delivery_translations table
    op.create_table(
        'delivery_translations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('delivery_id', sa.Integer(), nullable=False),
        sa.Column('lang', sa.String(5), nullable=False),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('option_note', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=func.now(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['delivery_id'], ['deliveries.id'], ondelete='CASCADE')
    )
    op.create_index('ix_delivery_translations_id', 'delivery_translations', ['id'])
    op.create_index('ix_delivery_translations_delivery_id', 'delivery_translations', ['delivery_id'])
    
    # Create delivery_categories association table
    op.create_table(
        'delivery_categories',
        sa.Column('delivery_id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('delivery_id', 'category_id'),
        sa.ForeignKeyConstraint(['delivery_id'], ['deliveries.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='CASCADE')
    )
    
    # Add delivery_id column to products table
    op.add_column('products', 
        sa.Column('delivery_id', sa.Integer(), nullable=True))
    
    # Add foreign key constraint
    op.create_foreign_key(
        'fk_products_delivery_id',
        'products', 'deliveries',
        ['delivery_id'], ['id'],
        ondelete='SET NULL'
    )
    op.create_index('ix_products_delivery_id', 'products', ['delivery_id'])


def downgrade() -> None:
    # Drop indexes and foreign key from products table
    op.drop_index('ix_products_delivery_id', 'products')
    op.drop_constraint('fk_products_delivery_id', 'products', type_='foreignkey')
    op.drop_column('products', 'delivery_id')
    
    # Drop delivery_categories table
    op.drop_table('delivery_categories')
    
    # Drop delivery_translations table  
    op.drop_index('ix_delivery_translations_delivery_id', 'delivery_translations')
    op.drop_index('ix_delivery_translations_id', 'delivery_translations')
    op.drop_table('delivery_translations')
    
    # Drop deliveries table
    op.drop_index('ix_deliveries_id', 'deliveries')
    op.drop_table('deliveries')
