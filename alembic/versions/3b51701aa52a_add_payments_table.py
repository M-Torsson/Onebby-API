"""add_payments_table

Revision ID: 3b51701aa52a
Revises: z3a4b5c6d7e8
Create Date: 2026-02-24 12:30:11.705515

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON


# revision identifiers, used by Alembic.
revision: str = '3b51701aa52a'
down_revision: Union[str, None] = 'z3a4b5c6d7e8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create payments table
    op.create_table(
        'payments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('payment_method', sa.String(length=50), nullable=False),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False, server_default='EUR'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'),
        
        # Provider fields
        sa.Column('provider_payment_id', sa.String(length=255), nullable=True),
        sa.Column('provider_transaction_id', sa.String(length=255), nullable=True),
        sa.Column('payment_url', sa.Text(), nullable=True),
        sa.Column('provider_metadata', JSON, nullable=True),
        sa.Column('payment_info', JSON, nullable=True),
        
        # URLs
        sa.Column('return_url', sa.Text(), nullable=True),
        sa.Column('cancel_url', sa.Text(), nullable=True),
        sa.Column('webhook_url', sa.Text(), nullable=True),
        
        # Error tracking
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('error_code', sa.String(length=100), nullable=True),
        
        # Testing fields
        sa.Column('is_test', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('test_scenario', sa.String(length=50), nullable=True),
        
        # Refund fields
        sa.Column('refunded_amount', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('refund_reason', sa.Text(), nullable=True),
        sa.Column('refund_transaction_id', sa.String(length=255), nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('processing_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('failed_at', sa.DateTime(), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(), nullable=True),
        sa.Column('refunded_at', sa.DateTime(), nullable=True),
        
        # Constraints
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE'),
        sa.CheckConstraint('status IN (\'pending\', \'processing\', \'completed\', \'failed\', \'cancelled\', \'refunded\')', name='payment_status_check')
    )
    
    # Create indexes for better query performance
    op.create_index('ix_payments_order_id', 'payments', ['order_id'])
    op.create_index('ix_payments_provider_payment_id', 'payments', ['provider_payment_id'])
    op.create_index('ix_payments_status', 'payments', ['status'])
    op.create_index('ix_payments_created_at', 'payments', ['created_at'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_payments_created_at', table_name='payments')
    op.drop_index('ix_payments_status', table_name='payments')
    op.drop_index('ix_payments_provider_payment_id', table_name='payments')
    op.drop_index('ix_payments_order_id', table_name='payments')
    
    # Drop table
    op.drop_table('payments')
