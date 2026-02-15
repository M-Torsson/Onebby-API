"""Add addresses table

Revision ID: c9d0e1f2g3h4
Revises: w3x4y5z6a7b8
Create Date: 2026-02-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'c9d0e1f2g3h4'
down_revision = 'w3x4y5z6a7b8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create addresses table
    op.create_table(
        'addresses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('address_type', sa.String(), nullable=False),
        sa.Column('alias', sa.String(), nullable=True),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('last_name', sa.String(), nullable=True),
        sa.Column('company_name', sa.String(), nullable=True),
        sa.Column('company', sa.String(), nullable=True),
        sa.Column('address_house_number', sa.String(), nullable=False),
        sa.Column('house_number', sa.String(), nullable=False),
        sa.Column('city', sa.String(), nullable=False),
        sa.Column('postal_code', sa.String(), nullable=False),
        sa.Column('country', sa.String(), nullable=False),
        sa.Column('phone', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create index on user_id for faster queries
    op.create_index(op.f('ix_addresses_user_id'), 'addresses', ['user_id'], unique=False)


def downgrade() -> None:
    # Drop index
    op.drop_index(op.f('ix_addresses_user_id'), table_name='addresses')
    
    # Drop addresses table
    op.drop_table('addresses')
