from typing import Dict

from fastapi.testclient import TestClient

from app.config import cfg
from app.const import API_WEB_V1
from app.const import SYSTEM_USER


def test_get_access_token(client: TestClient) -> None:
    login_data = {
        "username": SYSTEM_USER,
        "password": cfg.init.password,
    }
    r = client.post(f"{API_WEB_V1}/login/access-token", data=login_data)
    tokens = r.json()
    assert r.status_code == 200
    assert "access_token" in tokens
    assert tokens["access_token"]


def test_use_access_token(client: TestClient, systemuser_token_headers: Dict[str, str]) -> None:
    r = client.post(
        f"{API_WEB_V1}/login/test-token",
        headers=systemuser_token_headers,
    )
    result = r.json()
    assert r.status_code == 200
    assert "email" in result
