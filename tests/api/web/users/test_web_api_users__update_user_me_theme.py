"""
    TEST WEB API -- USERS -- UPDATE USER ME -- THEME
"""

from typing import Dict

from api.schemas.user import UserSchema
from config import cfg
from fastapi.testclient import TestClient
from locales import Locales

PUT_USER_ME_THEME_API = f"{cfg.server.api.web}/users/me/theme"


def test_update_user_theme__unauthorized(client: TestClient) -> None:

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.put(PUT_USER_ME_THEME_API, headers={})

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid access token"


def test_update_user_theme__normal_user(client: TestClient, normal_user_token_headers: Dict[str, str]) -> None:

    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_theme_light = "light"
    t_theme_dark = "dark"

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.put(PUT_USER_ME_THEME_API, headers=normal_user_token_headers, params={"theme": t_theme_light})
    responseSchema = UserSchema(**response.json())

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 200

    assert responseSchema
    assert responseSchema.theme == t_theme_light

    # ----------------------------------------------
    # RESET
    # ----------------------------------------------

    assert client.put(PUT_USER_ME_THEME_API, headers=normal_user_token_headers, params={"theme": t_theme_dark})


def test_update_user_theme__normal_user__invalid_theme(
    client: TestClient, normal_user_token_headers: Dict[str, str]
) -> None:

    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_theme_invalid = "darklight"

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.put(PUT_USER_ME_THEME_API, headers=normal_user_token_headers, params={"theme": t_theme_invalid})

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"][0] == "query"
    assert response.json()["detail"][0]["loc"][1] == "theme"
