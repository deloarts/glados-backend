from typing import Dict

from config import cfg
from const import SYSTEM_USER
from fastapi.testclient import TestClient


def test_get_access_token(client: TestClient) -> None:
    """
    Test the access token retrieval endpoint.
    This test sends a POST request to the login endpoint with the provided
    username and password, and checks if the response contains a valid
    access token.

    Args:
        client (TestClient): The test client used to make requests to the API.

    Asserts:
        The response status code is 200.
        The response contains an "access_token".
        The "access_token" is not empty.
    """

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
    """
    Test the use of an access token to authenticate and retrieve user information.

    Args:
        client (TestClient): The test client used to make requests to the API.
        systemuser_token_headers (Dict[str, str]): The headers containing the access token for authentication.

    Asserts:
        The response status code is 200.
        The response JSON contains the key "email".
    """

    r = client.post(
        f"{cfg.server.api.web}/login/test-token",
        headers=systemuser_token_headers,
    )
    result = r.json()
    assert r.status_code == 200
    assert "email" in result
