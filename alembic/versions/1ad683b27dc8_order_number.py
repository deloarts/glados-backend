"""order_number

Revision ID: 1ad683b27dc8
Revises: 3d9027c47dd2
Create Date: 2024-09-24 13:58:34.023933

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "1ad683b27dc8"
down_revision = "3d9027c47dd2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("bought_item_table", schema=None) as batch_op:
        batch_op.alter_column("definition", new_column_name="order_number")


def downgrade() -> None:
    with op.batch_alter_table("bought_item_table", schema=None) as batch_op:
        batch_op.alter_column("order_number", new_column_name="definition")
