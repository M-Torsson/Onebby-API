"""Add approval_status for companies

Revision ID: w3x4y5z6a7b8
Revises: q7r8s9t0u1v2
Create Date: 2026-02-13 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'w3x4y5z6a7b8'
down_revision = 'q7r8s9t0u1v2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add approval_status column for companies
    op.add_column('users', sa.Column('approval_status', sa.String(), nullable=True))
    
    # Set default value for existing companies
    op.execute("UPDATE users SET approval_status = 'pending' WHERE reg_type = 'company' AND approval_status IS NULL")


def downgrade() -> None:
    # Remove approval_status column
    op.drop_column('users', 'approval_status')
