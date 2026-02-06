# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

"""add_priority_and_campaign_id_to_discounts

Revision ID: a1b2c3d4e5f6
Revises: f8d09aa8411a
Create Date: 2026-02-06 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'f8d09aa8411a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add priority column to discount_campaigns table
    op.add_column('discount_campaigns', 
        sa.Column('priority', sa.Integer(), nullable=False, server_default='1'))
    
    # Add campaign_id and priority columns to product_discounts table
    op.add_column('product_discounts', 
        sa.Column('campaign_id', sa.Integer(), nullable=True))
    op.add_column('product_discounts', 
        sa.Column('priority', sa.Integer(), nullable=False, server_default='1'))
    
    # Add foreign key constraint
    op.create_foreign_key(
        'fk_product_discounts_campaign_id',
        'product_discounts', 'discount_campaigns',
        ['campaign_id'], ['id'],
        ondelete='SET NULL'
    )


def downgrade() -> None:
    # Remove foreign key constraint
    op.drop_constraint('fk_product_discounts_campaign_id', 'product_discounts', type_='foreignkey')
    
    # Remove columns from product_discounts
    op.drop_column('product_discounts', 'priority')
    op.drop_column('product_discounts', 'campaign_id')
    
    # Remove column from discount_campaigns
    op.drop_column('discount_campaigns', 'priority')
