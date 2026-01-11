"""Remove category grandchildren (max depth=2)

Revision ID: 6f1b4d2c9e10
Revises: 993e7110da86
Create Date: 2026-01-11

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "6f1b4d2c9e10"
down_revision: Union[str, None] = "993e7110da86"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Delete any categories whose parent is itself a child (grandchildren or deeper).
    # This keeps the hierarchy at: parent -> child only.
    # Note: category_translations and product/category join rows are expected to cascade.
    op.execute(
        """
        DELETE FROM categories
        WHERE id IN (
            SELECT c.id
            FROM categories c
            JOIN categories p ON c.parent_id = p.id
            WHERE p.parent_id IS NOT NULL
        );
        """
    )


def downgrade() -> None:
    # Irreversible: deleted rows cannot be restored automatically.
    pass
