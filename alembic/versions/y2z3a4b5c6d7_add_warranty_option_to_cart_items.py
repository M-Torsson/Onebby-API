"""add warranty option to cart items

Revision ID: y2z3a4b5c6d7
Revises: x1y2z3a4b5c6
Create Date: 2026-02-18 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'y2z3a4b5c6d7'
down_revision = 'x1y2z3a4b5c6'
branch_labels = None
depends_on = None


def upgrade():
    """Add warranty_option column to cart_items table"""
    op.add_column('cart_items', 
        sa.Column('warranty_option', postgresql.JSON(astext_type=sa.Text()), nullable=True)
    )


def downgrade():
    """Remove warranty_option column from cart_items table"""
    op.drop_column('cart_items', 'warranty_option')
