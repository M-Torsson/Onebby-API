# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

"""Merge migration heads

Revision ID: f8d09aa8411a
Revises: 66552411929d, 7c8b1a4f3c32
Create Date: 2026-01-27 15:28:07.839732

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f8d09aa8411a'
down_revision: Union[str, None] = ('66552411929d', '7c8b1a4f3c32')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
