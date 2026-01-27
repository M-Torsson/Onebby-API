# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

"""allow_null_price

Revision ID: 66552411929d
Revises: d7d76accf25b
Create Date: 2026-01-08 13:17:53.671517

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '66552411929d'
down_revision: Union[str, None] = 'd7d76accf25b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Allow NULL for price_list and remove default
    op.alter_column('products', 'price_list', nullable=True, server_default=None)


def downgrade() -> None:
    # Revert: set default to 0.0 and NOT NULL
    op.alter_column('products', 'price_list', nullable=False, server_default='0.0')
