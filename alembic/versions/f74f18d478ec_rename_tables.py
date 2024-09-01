"""rename tables

Revision ID: f74f18d478ec
Revises: 7e368bdcfd1c
Create Date: 2024-08-31 15:26:30.827114

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "f74f18d478ec"
down_revision = "7e368bdcfd1c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Remove table indices
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.drop_index("ix_user_email")
        batch_op.drop_index("ix_user_full_name")
        batch_op.drop_index("ix_user_id")
        batch_op.drop_index("ix_user_username")

    with op.batch_alter_table("emailnotification", schema=None) as batch_op:
        batch_op.drop_index("ix_emailnotification_id")

    with op.batch_alter_table("boughtitem", schema=None) as batch_op:
        batch_op.drop_index("ix_boughtitem_id")
        batch_op.drop_index("ix_boughtitem_project")

    with op.batch_alter_table("apikey", schema=None) as batch_op:
        batch_op.drop_index("ix_apikey_id")

    # Rename tables
    op.rename_table(old_table_name="apikey", new_table_name="api_key_table")
    op.rename_table(old_table_name="boughtitem", new_table_name="bought_item_table")
    op.rename_table(old_table_name="emailnotification", new_table_name="email_notification_table")
    op.rename_table(old_table_name="user", new_table_name="user_table")

    # Create new indices
    with op.batch_alter_table("api_key_table", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_api_key_table_id"), ["id"], unique=True)

    with op.batch_alter_table("email_notification_table", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_email_notification_table_id"), ["id"], unique=True)

    with op.batch_alter_table("user_table", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_user_table_email"), ["email"], unique=True)
        batch_op.create_index(batch_op.f("ix_user_table_id"), ["id"], unique=True)
        batch_op.create_index(batch_op.f("ix_user_table_username"), ["username"], unique=True)

    with op.batch_alter_table("bought_item_table", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_bought_item_table_id"), ["id"], unique=True)


def downgrade() -> None:
    # Remove table indices
    with op.batch_alter_table("bought_item_table", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_bought_item_table_id"))

    with op.batch_alter_table("user_table", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_user_table_username"))
        batch_op.drop_index(batch_op.f("ix_user_table_id"))
        batch_op.drop_index(batch_op.f("ix_user_table_email"))

    with op.batch_alter_table("email_notification_table", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_email_notification_table_id"))

    with op.batch_alter_table("api_key_table", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_api_key_table_id"))

    # Rename tables
    op.rename_table(new_table_name="apikey", old_table_name="api_key_table")
    op.rename_table(new_table_name="boughtitem", old_table_name="bought_item_table")
    op.rename_table(new_table_name="emailnotification", old_table_name="email_notification_table")
    op.rename_table(new_table_name="user", old_table_name="user_table")

    # Create new indices
    with op.batch_alter_table("apikey", schema=None) as batch_op:
        batch_op.create_index("ix_apikey_id", ["id"], unique=1)

    with op.batch_alter_table("boughtitem", schema=None) as batch_op:
        batch_op.create_index("ix_boughtitem_project", ["project"], unique=False)
        batch_op.create_index("ix_boughtitem_id", ["id"], unique=1)

    with op.batch_alter_table("emailnotification", schema=None) as batch_op:
        batch_op.create_index("ix_emailnotification_id", ["id"], unique=1)

    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.create_index("ix_user_username", ["username"], unique=1)
        batch_op.create_index("ix_user_id", ["id"], unique=1)
        batch_op.create_index("ix_user_full_name", ["full_name"], unique=False)
        batch_op.create_index("ix_user_email", ["email"], unique=1)
