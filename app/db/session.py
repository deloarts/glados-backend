"""
    DB session maker.
"""

# pylint: disable=R0903

from typing import Generator

from config import cfg
from const import DB_DEVELOPMENT, DB_PRODUCTION, SYSTEM_USER
from crud import crud_user
from multilog import log
from schemas import schema_user
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Base = declarative_base()


class Engine:
    engine = create_engine(
        f"sqlite:///{DB_DEVELOPMENT if cfg.debug else DB_PRODUCTION}",
        convert_unicode=True,
        connect_args={"check_same_thread": False},
    )

    @staticmethod
    def new_session(name: str) -> Session:
        Session = sessionmaker(autocommit=False, autoflush=False, bind=Engine.engine)
        log.info(f"Created new session {name!r}")
        return Session()


class DB:
    base_session = Engine.new_session(name="Base Session")

    @staticmethod
    def get() -> Generator:
        """Connects to the db."""
        db = DB.base_session
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
        import models  # pylint: disable=W0611

        # tables should be created with Alembic migrations.
        # if you don't want to use Alembic uncomment the following line and the above
        # line 'Base = declarative_base()'
        # Base.metadata.create_all(bind=engine)

        db = DB.base_session
        user = crud_user.user.get_by_email(db, email=cfg.init.mail)
        if not user:
            log.info("Admin user not found in database. Creating admin user.")
            user_in = schema_user.UserCreate(
                username=SYSTEM_USER,
                email=cfg.init.mail,
                password=cfg.init.password,
                full_name=cfg.init.full_name,
                is_superuser=True,
                is_active=True,
                is_systemuser=True,
            )
            user = crud_user.user.create(db, obj_in=user_in)
