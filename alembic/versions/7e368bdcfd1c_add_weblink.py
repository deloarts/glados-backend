"""add_weblink

Revision ID: 7e368bdcfd1c
Revises: 0c1f5dc9386c
Create Date: 2024-07-22 09:51:42.598830

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7e368bdcfd1c"
down_revision = "0c1f5dc9386c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("boughtitem", schema=None) as batch_op:
        batch_op.add_column(sa.Column("weblink", sa.String(), nullable=True))

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("boughtitem", schema=None) as batch_op:
        batch_op.drop_column("weblink")

    # ### end Alembic commands ###
