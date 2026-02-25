"""add_warranty_registrations_table

Revision ID: fd09596ef9ad
Revises: e1b66b561cd0
Create Date: 2026-02-25 16:01:36.094654

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'fd09596ef9ad'
down_revision: Union[str, None] = 'e1b66b561cd0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create warranty_registrations table
    op.create_table(
        'warranty_registrations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('warranty_id', sa.Integer(), nullable=False),
        sa.Column('customer_name', sa.String(length=100), nullable=False),
        sa.Column('customer_lastname', sa.String(length=100), nullable=False),
        sa.Column('customer_email', sa.String(length=255), nullable=False),
        sa.Column('customer_phone', sa.String(length=20), nullable=False),
        sa.Column('product_ean13', sa.String(length=13), nullable=False),
        sa.Column('product_name', sa.String(length=255), nullable=False),
        sa.Column('g3_transaction_id', sa.String(length=100), nullable=True),
        sa.Column('g3_pin', sa.String(length=50), nullable=True),
        sa.Column('g3_response', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('error_code', sa.String(length=50), nullable=True),
        sa.Column('is_test', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('registered_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('failed_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['warranty_id'], ['warranties.id'], ondelete='CASCADE')
    )
    
    # Create indexes
    op.create_index('ix_warranty_registrations_id', 'warranty_registrations', ['id'])
    op.create_index('ix_warranty_registrations_order_id', 'warranty_registrations', ['order_id'])
    op.create_index('ix_warranty_registrations_product_id', 'warranty_registrations', ['product_id'])
    op.create_index('ix_warranty_registrations_warranty_id', 'warranty_registrations', ['warranty_id'])
    op.create_index('ix_warranty_registrations_status', 'warranty_registrations', ['status'])
    op.create_index('ix_warranty_registrations_g3_transaction_id', 'warranty_registrations', ['g3_transaction_id'], unique=True)
    op.create_index('ix_warranty_registrations_created_at', 'warranty_registrations', ['created_at'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_warranty_registrations_created_at', table_name='warranty_registrations')
    op.drop_index('ix_warranty_registrations_g3_transaction_id', table_name='warranty_registrations')
    op.drop_index('ix_warranty_registrations_status', table_name='warranty_registrations')
    op.drop_index('ix_warranty_registrations_warranty_id', table_name='warranty_registrations')
    op.drop_index('ix_warranty_registrations_product_id', table_name='warranty_registrations')
    op.drop_index('ix_warranty_registrations_order_id', table_name='warranty_registrations')
    op.drop_index('ix_warranty_registrations_id', table_name='warranty_registrations')
    
    # Drop table
    op.drop_table('warranty_registrations')

