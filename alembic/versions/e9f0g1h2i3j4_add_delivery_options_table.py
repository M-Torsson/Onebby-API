# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

"""add_delivery_options_table

Revision ID: e9f0g1h2i3j4
Revises: d7e8f9g0h1i2
Create Date: 2026-02-09 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e9f0g1h2i3j4'
down_revision: Union[str, None] = 'd7e8f9g0h1i2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create delivery_options table
    op.create_table(
        'delivery_options',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('delivery_id', sa.Integer(), nullable=False),
        sa.Column('icon', sa.String(500), nullable=True),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('price', sa.Float(), nullable=False, server_default='0'),
        sa.Column('position', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['delivery_id'], ['deliveries.id'], ondelete='CASCADE')
    )
    op.create_index('ix_delivery_options_id', 'delivery_options', ['id'])
    op.create_index('ix_delivery_options_delivery_id', 'delivery_options', ['delivery_id'])


def downgrade() -> None:
    op.drop_index('ix_delivery_options_delivery_id', 'delivery_options')
    op.drop_index('ix_delivery_options_id', 'delivery_options')
    op.drop_table('delivery_options')
