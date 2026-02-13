"""Add customer registration fields to user model

Revision ID: p1q2r3s4t5u6
Revises: k1l2m3n4o5p6
Create Date: 2026-02-13 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'p1q2r3s4t5u6'
down_revision = 'k1l2m3n4o5p6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns for customer registration
    op.add_column('users', sa.Column('reg_type', sa.String(), nullable=True))
    op.add_column('users', sa.Column('title', sa.String(), nullable=True))
    op.add_column('users', sa.Column('first_name', sa.String(), nullable=True))
    op.add_column('users', sa.Column('last_name', sa.String(), nullable=True))
    
    # Update existing rows to have default reg_type
    op.execute("UPDATE users SET reg_type = 'user' WHERE reg_type IS NULL")
    
    # Make reg_type non-nullable after setting defaults
    op.alter_column('users', 'reg_type', nullable=False)
    
    # Make username nullable (optional for customers)
    op.alter_column('users', 'username', nullable=True)


def downgrade() -> None:
    # Revert changes
    op.alter_column('users', 'username', nullable=False)
    op.drop_column('users', 'last_name')
    op.drop_column('users', 'first_name')
    op.drop_column('users', 'title')
    op.drop_column('users', 'reg_type')
