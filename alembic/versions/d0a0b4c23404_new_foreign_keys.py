"""new_foreign_keys

Revision ID: d0a0b4c23404
Revises: f74f18d478ec
Create Date: 2024-09-05 07:04:23.188916

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "d0a0b4c23404"
down_revision = "f74f18d478ec"
branch_labels = None
depends_on = None
naming_convention = {
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
}


def upgrade() -> None:
    # Rename column
    with op.batch_alter_table("bought_item_table", schema=None) as batch_op:
        batch_op.alter_column("taken_over_id", new_column_name="receiver_id", server_default=None)

    # DB has an unnamed foreign key constraint, rename it with the naming convention.
    # The name should then be `fk_bought_item_table_creator_id_user_table`.
    # See: https://alembic.sqlalchemy.org/en/latest/batch.html#dropping-unnamed-or-named-foreign-key-constraints
    with op.batch_alter_table("bought_item_table", schema=None, naming_convention=naming_convention) as batch_op:
        batch_op.create_foreign_key(
            "fk_bought_item_table_requester_id_user_table", "user_table", ["requester_id"], ["id"]
        )
        batch_op.create_foreign_key("fk_bought_item_table_orderer_id_user_table", "user_table", ["orderer_id"], ["id"])
        batch_op.create_foreign_key(
            "fk_bought_item_table_receiver_id_user_table", "user_table", ["receiver_id"], ["id"]
        )


def downgrade() -> None:
    # Only drop newly created foreign key constraints and leave the name of ´fk_bought_item_table_creator_id_user_table`
    # because it's not necessary to delete the name when downgrading.
    with op.batch_alter_table("bought_item_table", schema=None) as batch_op:
        batch_op.drop_constraint("fk_bought_item_table_requester_id_user_table", type_="foreignkey")
        batch_op.drop_constraint("fk_bought_item_table_orderer_id_user_table", type_="foreignkey")
        batch_op.drop_constraint("fk_bought_item_table_receiver_id_user_table", type_="foreignkey")
        batch_op.alter_column("receiver_id", new_column_name="taken_over_id", server_default=None)
