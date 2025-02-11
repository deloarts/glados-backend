from typing import Dict
from typing import Generator

import pytest
from config import cfg
from const import SYSTEM_USER
from fastapi.testclient import TestClient

import alembic
import alembic.command
import alembic.config
from app.db.session import InitDatabase
from app.db.session import SessionLocal
from app.server import app
from tests.utils.user import TEST_ADMIN_USERNAME
from tests.utils.user import TEST_GUEST_USERNAME
from tests.utils.user import TEST_PASSWORD
from tests.utils.user import TEST_SUPER_USERNAME
from tests.utils.user import TEST_USER_USERNAME
from tests.utils.user import get_test_admin_user
from tests.utils.user import get_test_guest_user
from tests.utils.user import get_test_super_user
from tests.utils.user import get_test_user
from tests.utils.user import user_authentication_headers


@pytest.fixture(scope="session")
def db() -> Generator:
    yield SessionLocal()


@pytest.fixture(scope="module")
def client() -> Generator:
    with TestClient(app) as c:
        yield c


def pytest_sessionstart():
    assert cfg.debug is True

    alembic_config = alembic.config.Config("alembic.ini")
    alembic.command.upgrade(alembic_config, "head")

    InitDatabase()

    db = SessionLocal()
    assert get_test_user(db)
    assert get_test_super_user(db)
    assert get_test_admin_user(db)
    assert get_test_guest_user(db)


@pytest.fixture(scope="module")
def normal_user_token_headers(client: TestClient) -> Dict[str, str]:
    return user_authentication_headers(client=client, username=TEST_USER_USERNAME, password=TEST_PASSWORD)


@pytest.fixture(scope="module")
def super_user_token_headers(client: TestClient) -> Dict[str, str]:
    return user_authentication_headers(client=client, username=TEST_SUPER_USERNAME, password=TEST_PASSWORD)


@pytest.fixture(scope="module")
def admin_user_token_headers(client: TestClient) -> Dict[str, str]:
    return user_authentication_headers(client=client, username=TEST_ADMIN_USERNAME, password=TEST_PASSWORD)


@pytest.fixture(scope="module")
def guest_user_token_headers(client: TestClient) -> Dict[str, str]:
    return user_authentication_headers(client=client, username=TEST_GUEST_USERNAME, password=TEST_PASSWORD)


@pytest.fixture(scope="module")
def systemuser_token_headers(client: TestClient) -> Dict[str, str]:
    return user_authentication_headers(client=client, username=SYSTEM_USER, password=cfg.init.password)
