"""add orders and order_items tables

Revision ID: z3a4b5c6d7e8
Revises: y2z3a4b5c6d7
Create Date: 2026-02-23 15:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'z3a4b5c6d7e8'
down_revision = 'y2z3a4b5c6d7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create orders table
    op.create_table(
        'orders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        
        # User reference
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('session_id', sa.String(255), nullable=True),
        sa.Column('user_type', sa.String(50), nullable=False, server_default='customer'),
        
        # Customer/Company information
        sa.Column('customer_info', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        
        # Addresses
        sa.Column('billing_address', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('shipping_address', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        
        # Financial
        sa.Column('subtotal', sa.Numeric(10, 2), nullable=False),
        sa.Column('shipping_cost', sa.Numeric(10, 2), nullable=False, server_default='0.00'),
        sa.Column('tax', sa.Numeric(10, 2), nullable=False, server_default='0.00'),
        sa.Column('discount', sa.Numeric(10, 2), nullable=False, server_default='0.00'),
        sa.Column('total_amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('currency', sa.String(3), nullable=False, server_default='EUR'),
        
        # Payment
        sa.Column('payment_status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('payment_method', sa.String(50), nullable=True),
        sa.Column('payment_transaction_id', sa.String(255), nullable=True),
        
        # Shipping
        sa.Column('shipping_method', sa.String(100), nullable=True),
        sa.Column('shipping_status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('tracking_number', sa.String(255), nullable=True),
        
        # Status
        sa.Column('status', sa.String(50), nullable=False, server_default='pending'),
        
        # Notes
        sa.Column('customer_note', sa.Text(), nullable=True),
        sa.Column('admin_note', sa.Text(), nullable=True),
        
        # Event timestamps
        sa.Column('paid_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('confirmed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('shipped_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('delivered_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL')
    )
    
    # Create indexes for orders table
    op.create_index('idx_orders_user_id', 'orders', ['user_id'])
    op.create_index('idx_orders_session_id', 'orders', ['session_id'])
    op.create_index('idx_orders_status', 'orders', ['status'])
    op.create_index('idx_orders_payment_status', 'orders', ['payment_status'])
    op.create_index('idx_orders_shipping_status', 'orders', ['shipping_status'])
    op.create_index('idx_orders_created_at', 'orders', ['created_at'])
    
    # Create order_items table
    op.create_table(
        'order_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        
        # Relationships
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=True),
        sa.Column('product_variant_id', sa.Integer(), nullable=True),
        
        # Product information (stored for historical record)
        sa.Column('product_title', sa.String(500), nullable=False),
        sa.Column('product_sku', sa.String(100), nullable=True),
        sa.Column('product_type', sa.String(50), nullable=True),
        sa.Column('product_image', sa.Text(), nullable=True),
        
        # Pricing
        sa.Column('quantity', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('unit_price', sa.Numeric(10, 2), nullable=False),
        sa.Column('subtotal', sa.Numeric(10, 2), nullable=False),
        sa.Column('discount', sa.Numeric(10, 2), nullable=False, server_default='0.00'),
        
        # Options (JSON)
        sa.Column('delivery_option', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('warranty_option', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('variant_attributes', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['product_variant_id'], ['product_variants.id'], ondelete='SET NULL')
    )
    
    # Create indexes for order_items table
    op.create_index('idx_order_items_order_id', 'order_items', ['order_id'])
    op.create_index('idx_order_items_product_id', 'order_items', ['product_id'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_order_items_product_id', table_name='order_items')
    op.drop_index('idx_order_items_order_id', table_name='order_items')
    op.drop_index('idx_orders_created_at', table_name='orders')
    op.drop_index('idx_orders_shipping_status', table_name='orders')
    op.drop_index('idx_orders_payment_status', table_name='orders')
    op.drop_index('idx_orders_status', table_name='orders')
    op.drop_index('idx_orders_session_id', table_name='orders')
    op.drop_index('idx_orders_user_id', table_name='orders')
    
    # Drop tables
    op.drop_table('order_items')
    op.drop_table('orders')
