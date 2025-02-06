from typing import Dict

from config import cfg
from const import SYSTEM_USER
from fastapi.testclient import TestClient


def test_get_access_token(client: TestClient) -> None:
    login_data = {
        "username": SYSTEM_USER,
        "password": cfg.init.password,
    }
    r = client.post(f"{cfg.server.api.web}/login/access-token", data=login_data)
    tokens = r.json()
    assert r.status_code == 200
    assert "access_token" in tokens
    assert tokens["access_token"]


def test_use_access_token(client: TestClient, systemuser_token_headers: Dict[str, str]) -> None:
    r = client.post(
        f"{cfg.server.api.web}/login/test-token",
        headers=systemuser_token_headers,
    )
    result = r.json()
    assert r.status_code == 200
    assert "email" in result
