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
    """
    Test case for updating user theme without authorization.

    This test ensures that an unauthorized request to update the user's theme
    returns a 401 Unauthorized status code and the appropriate error message.

    Args:
        client (TestClient): The test client used to make the request.

    Assertions:
        - The response object is not None.
        - The response status code is 401.
        - The response JSON contains the detail message "Invalid access token".
    """
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
    """
    Test the update of a user's theme preference for a normal user.

    This test verifies that a normal user can successfully update their theme preference
    using the PUT_USER_ME_THEME_API endpoint.

    Args:
        client (TestClient): The test client to simulate API requests.
        normal_user_token_headers (Dict[str, str]): The headers containing the normal user's authentication token.

    Steps:
        1. Prepare the themes to be tested (light and dark).
        2. Send a PUT request to update the user's theme to 'light'.
        3. Validate the response status code and the updated theme in the response schema.
        4. Reset the user's theme back to 'dark' after the test.

    Assertions:
        - The response is not None.
        - The response status code is 200.
        - The response schema is valid and the theme is updated to 'light'.
        - The user's theme is reset to 'dark' after the test.
    """
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
    """
    Test updating user theme with an invalid theme value for a normal user.

    This test verifies that when a normal user attempts to update their theme
    to an invalid value, the API responds with a 422 Unprocessable Entity status
    code and the appropriate error details.

    Args:
        client (TestClient): The test client to simulate API requests.
        normal_user_token_headers (Dict[str, str]): The headers containing the
            normal user's authentication token.

    Assertions:
        - The response object is not None.
        - The response status code is 422.
        - The error detail in the response indicates that the 'theme' query
          parameter is invalid.
    """
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
