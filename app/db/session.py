"""
    DB session maker.
"""

# pylint: disable=R0903

import sys
from typing import Generator

from api.schemas.user import UserCreateSchema
from config import cfg
from const import ALEMBIC_VERSION
from const import DB_DEVELOPMENT
from const import DB_PRODUCTION
from const import SYSTEM_USER
from crud.user import crud_user
from db.base import Base
from db.models import UserModel
from multilog import log
from sqlalchemy import Column
from sqlalchemy import Table
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(
    f"sqlite:///{DB_DEVELOPMENT if cfg.debug else DB_PRODUCTION}",
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator:
    """Connects to the db."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class InitDatabase:
    """Database initialization."""

    def __init__(self):
        """
        Inits the database from all available models and starts the database watcher.
        Requires the filehandler for the db-folder to be initialized first.
        """
        # import all modules here that might define models so that
        # they will be registered properly on the metadata. Otherwise
        # you will have to import them first before calling this init.
        import db.models  # pylint: disable=W0611

        db = SessionLocal()
        # Check db revision
        version_num = db.query(Table("alembic_version", Base.metadata, Column("version_num"))).first()
        if version_num is None:
            log.error("Failed to fetch database version. Terminating the app.")
            sys.exit()
        if version_num[0] != ALEMBIC_VERSION:
            log.error(
                f"Database version differs from required version: DB={version_num[0]}, REQ={ALEMBIC_VERSION}. "
                "Terminating the app."
            )
            sys.exit()

        # Create system user if it doesn't exist
        user = crud_user.get_by_email(db, email=cfg.init.mail)
        if not user:
            log.info("System user not found in database. Creating system user.")
            user_in = UserCreateSchema(
                username=SYSTEM_USER,
                email=cfg.init.mail,
                password=cfg.init.password,
                full_name=cfg.init.full_name,
                is_active=True,
                is_superuser=True,
                is_adminuser=True,
                is_systemuser=True,
                is_guestuser=False,
            )

            creator = user_in.model_dump()
            del creator["password"]
            creator["username"] = "Glados Init"
            creator["full_name"] = "-"
            creator["id"] = 0
            creator["hashed_password"] = "not_relevant_because_temp"
            creator["is_systemuser"] = True

            user = crud_user.create(
                db,
                obj_in=user_in,
                current_user=UserModel(**creator),
            )
