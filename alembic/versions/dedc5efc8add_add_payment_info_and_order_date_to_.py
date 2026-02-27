"""add_payment_info_and_order_date_to_orders

Revision ID: dedc5efc8add
Revises: e1b66b561cd0
Create Date: 2026-02-27 14:33:18.660712

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dedc5efc8add'
down_revision: Union[str, None] = 'e1b66b561cd0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add payment_info column (JSON) to orders table
    op.add_column('orders', sa.Column('payment_info', sa.JSON(), nullable=True))
    
    # Add order_date column (String) to orders table
    op.add_column('orders', sa.Column('order_date', sa.String(50), nullable=True, comment='Custom order date from request'))


def downgrade() -> None:
    # Remove the new columns
    op.drop_column('orders', 'order_date')
    op.drop_column('orders', 'payment_info')
