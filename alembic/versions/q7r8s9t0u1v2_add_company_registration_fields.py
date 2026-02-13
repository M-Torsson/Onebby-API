"""Add company registration fields to user model

Revision ID: q7r8s9t0u1v2
Revises: p1q2r3s4t5u6
Create Date: 2026-02-13 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'q7r8s9t0u1v2'
down_revision = 'p1q2r3s4t5u6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add company-specific columns
    op.add_column('users', sa.Column('company_name', sa.String(), nullable=True))
    op.add_column('users', sa.Column('vat_number', sa.String(), nullable=True))
    op.add_column('users', sa.Column('tax_code', sa.String(), nullable=True))
    op.add_column('users', sa.Column('sdi_code', sa.String(), nullable=True))
    op.add_column('users', sa.Column('pec', sa.String(), nullable=True))


def downgrade() -> None:
    # Remove company-specific columns
    op.drop_column('users', 'pec')
    op.drop_column('users', 'sdi_code')
    op.drop_column('users', 'tax_code')
    op.drop_column('users', 'vat_number')
    op.drop_column('users', 'company_name')
