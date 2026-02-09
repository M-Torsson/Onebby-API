# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

"""add_warranty_tables_and_product_warranty_id

Revision ID: k1l2m3n4o5p6
Revises: j5k6l7m8n9o0
Create Date: 2026-02-09 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision: str = 'k1l2m3n4o5p6'
down_revision: Union[str, None] = 'j5k6l7m8n9o0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create warranties table
    op.create_table(
        'warranties',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('subtitle', sa.String(500), nullable=True),
        sa.Column('meta_description', sa.Text(), nullable=True),
        sa.Column('price', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('image', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=func.now(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_warranties_id', 'warranties', ['id'])
    
    # Create warranty_translations table
    op.create_table(
        'warranty_translations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('warranty_id', sa.Integer(), nullable=False),
        sa.Column('lang', sa.String(5), nullable=False),
        sa.Column('title', sa.String(255), nullable=True),
        sa.Column('subtitle', sa.String(500), nullable=True),
        sa.Column('meta_description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=func.now(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['warranty_id'], ['warranties.id'], ondelete='CASCADE')
    )
    op.create_index('ix_warranty_translations_id', 'warranty_translations', ['id'])
    op.create_index('ix_warranty_translations_warranty_id', 'warranty_translations', ['warranty_id'])
    
    # Create warranty_features table
    op.create_table(
        'warranty_features',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('warranty_id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(255), nullable=False),
        sa.Column('value', sa.Text(), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['warranty_id'], ['warranties.id'], ondelete='CASCADE')
    )
    op.create_index('ix_warranty_features_id', 'warranty_features', ['id'])
    op.create_index('ix_warranty_features_warranty_id', 'warranty_features', ['warranty_id'])
    
    # Create warranty_categories association table
    op.create_table(
        'warranty_categories',
        sa.Column('warranty_id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('warranty_id', 'category_id'),
        sa.ForeignKeyConstraint(['warranty_id'], ['warranties.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='CASCADE')
    )
    
    # Add warranty_id column to products table
    op.add_column('products', 
        sa.Column('warranty_id', sa.Integer(), nullable=True))
    
    # Add foreign key constraint
    op.create_foreign_key(
        'fk_products_warranty_id',
        'products', 'warranties',
        ['warranty_id'], ['id'],
        ondelete='SET NULL'
    )
    op.create_index('ix_products_warranty_id', 'products', ['warranty_id'])


def downgrade() -> None:
    # Drop indexes and foreign key from products table
    op.drop_index('ix_products_warranty_id', 'products')
    op.drop_constraint('fk_products_warranty_id', 'products', type_='foreignkey')
    op.drop_column('products', 'warranty_id')
    
    # Drop warranty_categories table
    op.drop_table('warranty_categories')
    
    # Drop warranty_features table
    op.drop_index('ix_warranty_features_warranty_id', 'warranty_features')
    op.drop_index('ix_warranty_features_id', 'warranty_features')
    op.drop_table('warranty_features')
    
    # Drop warranty_translations table  
    op.drop_index('ix_warranty_translations_warranty_id', 'warranty_translations')
    op.drop_index('ix_warranty_translations_id', 'warranty_translations')
    op.drop_table('warranty_translations')
    
    # Drop warranties table
    op.drop_index('ix_warranties_id', 'warranties')
    op.drop_table('warranties')
