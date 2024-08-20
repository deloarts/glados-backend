"""
    DB session maker.
"""

# pylint: disable=R0903

from typing import Generator

from api.schemas import schema_user
from config import cfg
from const import DB_DEVELOPMENT
from const import DB_PRODUCTION
from const import SYSTEM_USER
from crud.crud_user import crud_user
from db.models import model_user
from multilog import log
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
        user = crud_user.get_by_email(db, email=cfg.init.mail)
        if not user:
            log.info("Admin user not found in database. Creating admin user.")
            user_in = schema_user.UserCreate(
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
                current_user=model_user.User(**creator),
            )
