"""add_projects

Revision ID: 3d9027c47dd2
Revises: d0a0b4c23404
Create Date: 2024-09-05 16:15:19.876583

"""

from datetime import UTC
from datetime import datetime
from typing import Any
from typing import Optional

import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm.session import Session

from alembic import op

# revision identifiers, used by Alembic.
revision = "3d9027c47dd2"
down_revision = "d0a0b4c23404"
branch_labels = None
depends_on = None

session = Session(bind=op.get_bind())


class BaseSnapshot(DeclarativeBase):
    """Snapshot base class to ensure migration doesn't break on changes on the source"""

    id: Any
    __name__: str


class BoughtItemSnapshot(BaseSnapshot):
    __tablename__ = "bought_item_table"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(
        sa.Integer, primary_key=True, index=True, unique=True, nullable=False, autoincrement=True
    )
    project_id: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    project: Mapped[str] = mapped_column(sa.String, nullable=False)
    machine: Mapped[str] = mapped_column(sa.String, nullable=False)


class ProjectSnapshot(BaseSnapshot):
    __tablename__ = "project_table"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, index=True, unique=True, nullable=False)
    created: Mapped[datetime] = mapped_column(sa.DateTime, nullable=False)

    number: Mapped[str] = mapped_column(sa.String, index=True, unique=True, nullable=False)
    machine: Mapped[Optional[str]] = mapped_column(sa.String, nullable=True)
    customer: Mapped[str] = mapped_column(sa.String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(sa.String, nullable=True)
    is_active: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, default=True)
    deleted: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, default=False)

    designated_user_id: Mapped[int] = mapped_column(sa.Integer, nullable=False)


def upgrade() -> None:
    op.create_table(
        "project_table",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created", sa.DateTime(), nullable=False),
        sa.Column("number", sa.String(), nullable=False),
        sa.Column("machine", sa.String(), nullable=True),
        sa.Column("customer", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("deleted", sa.Boolean(), nullable=False),
        sa.Column("designated_user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["designated_user_id"], ["user_table.id"], name="fk_project_table_designated_user_id_user_table"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("project_table", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_project_table_id"), ["id"], unique=True)
        batch_op.create_index(batch_op.f("ix_project_table_number"), ["number"], unique=True)

    with op.batch_alter_table("bought_item_table", schema=None) as batch_op:
        # Project is nullable only for the migration, will be set to False later
        batch_op.add_column(sa.Column("project_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "fk_bought_item_table_project_id_project_table", "project_table", ["project_id"], ["id"]
        )

    items = session.query(BoughtItemSnapshot).all()
    for item in items:
        if not session.query(ProjectSnapshot).filter_by(number=item.project).first():
            project_data = {
                "created": datetime.now(UTC),
                "number": item.project,
                "machine": item.machine,
                "customer": "Unknown",
                "description": "Migration",
                "is_active": False,
                "designated_user_id": 1,  # = system user
            }
            session.add(ProjectSnapshot(**project_data))
            session.commit()

    q_projects = session.query(ProjectSnapshot).all()
    for project in q_projects:
        bought_items_by_project = session.query(BoughtItemSnapshot).filter_by(project=project.number).all()
        for item in bought_items_by_project:
            setattr(item, "project_id", project.id)
            session.add(item)
            session.commit()
            session.refresh(item)

    with op.batch_alter_table("bought_item_table", schema=None) as batch_op:
        batch_op.alter_column("project_id", nullable=False)
        batch_op.drop_column("project")
        batch_op.drop_column("machine")


def downgrade() -> None:
    with op.batch_alter_table("bought_item_table", schema=None) as batch_op:
        # Project is nullable only for the migration, will be set to False later
        batch_op.add_column(sa.Column("project", sa.VARCHAR(), nullable=True))
        batch_op.add_column(sa.Column("machine", sa.VARCHAR(), nullable=True))

    q_bought_items = session.query(BoughtItemSnapshot).all()
    for item in q_bought_items:
        project_by_id = session.query(ProjectSnapshot).filter_by(id=item.project_id).first()
        assert project_by_id
        setattr(item, "project", project_by_id.number)
        setattr(item, "machine", project_by_id.machine)
        session.add(item)
        session.commit()
        session.refresh(item)

    with op.batch_alter_table("bought_item_table", schema=None) as batch_op:
        batch_op.alter_column("project", nullable=False)
        batch_op.drop_constraint("fk_bought_item_table_project_id_project_table", type_="foreignkey")
        batch_op.drop_column("project_id")

    with op.batch_alter_table("project_table", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_project_table_number"))
        batch_op.drop_index(batch_op.f("ix_project_table_id"))

    op.drop_table("project_table")
