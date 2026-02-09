# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

"""change_delivery_option_icon_to_text

Revision ID: j5k6l7m8n9o0
Revises: e9f0g1h2i3j4
Create Date: 2026-02-09 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'j5k6l7m8n9o0'
down_revision: Union[str, None] = 'e9f0g1h2i3j4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Change icon column from VARCHAR(500) to TEXT to support base64 images
    op.alter_column('delivery_options', 'icon',
                    existing_type=sa.String(500),
                    type_=sa.Text(),
                    existing_nullable=True)


def downgrade() -> None:
    # Revert back to VARCHAR(500)
    op.alter_column('delivery_options', 'icon',
                    existing_type=sa.Text(),
                    type_=sa.String(500),
                    existing_nullable=True)
