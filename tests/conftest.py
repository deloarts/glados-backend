from typing import Dict
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.server import app
from tests.utils.user import TEST_MAIL
from tests.utils.user import authentication_token_from_email
from tests.utils.user import current_user_adminuser
from tests.utils.utils import get_systemuser_token_headers


@pytest.fixture(scope="session")
def db() -> Generator:
    yield SessionLocal()


@pytest.fixture(scope="module")
def client() -> Generator:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def systemuser_token_headers(client: TestClient) -> Dict[str, str]:
    return get_systemuser_token_headers(client)


@pytest.fixture(scope="module")
def normal_user_token_headers(client: TestClient, db: Session) -> Dict[str, str]:
    return authentication_token_from_email(client=client, email=TEST_MAIL, db=db)
