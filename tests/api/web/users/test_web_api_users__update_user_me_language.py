"""
    TEST WEB API -- USERS -- UPDATE USER ME -- LANGUAGE
"""

from typing import Dict

from api.schemas.user import UserSchema
from config import cfg
from fastapi.testclient import TestClient
from locales import Locales

PUT_USER_ME_LANGUAGE_API = f"{cfg.server.api.web}/users/me/language"


def test_update_user_language__unauthorized(client: TestClient) -> None:

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.put(PUT_USER_ME_LANGUAGE_API, headers={})

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid access token"


def test_update_user_language__normal_user(client: TestClient, normal_user_token_headers: Dict[str, str]) -> None:

    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_language_enGB = Locales.EN_GB.value
    t_language_deAT = Locales.DE_AT.value

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.put(
        PUT_USER_ME_LANGUAGE_API, headers=normal_user_token_headers, params={"language": t_language_deAT}
    )
    responseSchema = UserSchema(**response.json())

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 200

    assert responseSchema
    assert responseSchema.language == t_language_deAT

    # ----------------------------------------------
    # RESET
    # ----------------------------------------------

    assert client.put(PUT_USER_ME_LANGUAGE_API, headers=normal_user_token_headers, params={"language": t_language_enGB})


def test_update_user_language__normal_user__invalid_language(
    client: TestClient, normal_user_token_headers: Dict[str, str]
) -> None:

    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_language_invalid = "deDE"

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.put(
        PUT_USER_ME_LANGUAGE_API, headers=normal_user_token_headers, params={"language": t_language_invalid}
    )

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"][0] == "query"
    assert response.json()["detail"][0]["loc"][1] == "language"
