"""add delivery option to cart items

Revision ID: x1y2z3a4b5c6
Revises: i5j6k7l8m9n0
Create Date: 2026-02-16 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'x1y2z3a4b5c6'
down_revision = 'i5j6k7l8m9n0'
branch_labels = None
depends_on = None


def upgrade():
    """Add delivery_option column to cart_items table"""
    op.add_column('cart_items', 
        sa.Column('delivery_option', postgresql.JSON(astext_type=sa.Text()), nullable=True)
    )


def downgrade():
    """Remove delivery_option column from cart_items table"""
    op.drop_column('cart_items', 'delivery_option')
