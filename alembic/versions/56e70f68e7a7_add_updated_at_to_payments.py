"""add_updated_at_to_payments

Revision ID: 56e70f68e7a7
Revises: 3b51701aa52a
Create Date: 2026-02-24 13:06:36.727774

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '56e70f68e7a7'
down_revision: Union[str, None] = '3b51701aa52a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add updated_at column to payments table
    op.add_column('payments', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    # Remove updated_at column from payments table
    op.drop_column('payments', 'updated_at')
