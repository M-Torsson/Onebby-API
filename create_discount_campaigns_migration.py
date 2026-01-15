"""Create discount_campaigns table

Revision ID: create_discount_campaigns
Revises: 
Create Date: 2026-01-15

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'create_discount_campaigns'
down_revision = None  # أو آخر revision موجود
branch_labels = None
depends_on = None


def upgrade():
    # Create discount_campaigns table
    op.create_table(
        'discount_campaigns',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=1000), nullable=True),
        sa.Column('discount_type', sa.Enum('PERCENTAGE', 'FIXED_AMOUNT', name='discounttypeenum'), nullable=False),
        sa.Column('discount_value', sa.Float(), nullable=False),
        sa.Column('target_type', sa.Enum('PRODUCTS', 'CATEGORY', 'BRAND', 'ALL', name='targettypeenum'), nullable=False),
        sa.Column('target_ids', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create index on name
    op.create_index('ix_discount_campaigns_id', 'discount_campaigns', ['id'])
    op.create_index('ix_discount_campaigns_name', 'discount_campaigns', ['name'])


def downgrade():
    # Drop indexes
    op.drop_index('ix_discount_campaigns_name', table_name='discount_campaigns')
    op.drop_index('ix_discount_campaigns_id', table_name='discount_campaigns')
    
    # Drop table
    op.drop_table('discount_campaigns')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS targettypeenum')
    op.execute('DROP TYPE IF EXISTS discounttypeenum')
