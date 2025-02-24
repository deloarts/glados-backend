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
    """
    Test the update user language endpoint for unauthorized access.

    This test ensures that when an unauthorized request is made to update the user's language,
    the API responds with a 401 Unauthorized status code and the appropriate error message.

    Args:
        client (TestClient): The test client used to make the request.

    Assertions:
        - The response is not None.
        - The response status code is 401.
        - The response JSON contains a "detail" key with the value "Invalid access token".
    """

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
    """
    Test the update of a user's language preference for a normal user.

    This test performs the following steps:
    1. Preparation: Define the target languages for the test.
    2. Methods to Test: Send a PUT request to update the user's language.
    3. Validation: Verify that the response is successful and the language is updated correctly.
    4. Reset: Reset the user's language to the original value.

    Args:
        client (TestClient): The test client to send requests.
        normal_user_token_headers (Dict[str, str]): The headers containing the normal user's authentication token.

    Asserts:
        - The response is not None.
        - The response status code is 200.
        - The response schema is valid.
        - The user's language is updated to the target language.
        - The user's language is reset to the original value.
    """

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
    """
    Test updating user language with an invalid language code for a normal user.

    This test verifies that when a normal user attempts to update their language
    preference with an invalid language code, the API responds with a 422 status
    code and the appropriate error details.

    Args:
        client (TestClient): The test client used to make API requests.
        normal_user_token_headers (Dict[str, str]): The headers containing the
            authentication token for a normal user.

    Asserts:
        - The response object is not None.
        - The response status code is 422.
        - The error details in the response indicate that the 'language' query
          parameter is invalid.
    """

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
