"""product_number

Revision ID: 824d657001b8
Revises: 1ad683b27dc8
Create Date: 2024-09-25 08:48:51.215382

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "824d657001b8"
down_revision = "1ad683b27dc8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("project_table", schema=None) as batch_op:
        batch_op.alter_column("machine", new_column_name="product_number")


def downgrade() -> None:
    with op.batch_alter_table("project_table", schema=None) as batch_op:
        batch_op.alter_column("product_number", new_column_name="machine")
