"""
    TEST WEB API -- BOUGHT ITEMS -- READ
"""

from api.schemas import PageSchema
from config import cfg
from fastapi.testclient import TestClient

READ_ITEMS_API = f"{cfg.server.api.web}/items/bought"


def test_read_items__unauthorized(client: TestClient) -> None:
    """
    Test the unauthorized access to the read items API endpoint.
    This test verifies that an unauthorized request to the read items API
    endpoint returns a 401 status code and the appropriate error message.

    Args:
        client (TestClient): The test client used to make the API request.

    Assertions:
        - The response object is not None.
        - The response status code is 401 (Unauthorized).
        - The response JSON contains the expected error message indicating
          that the access token is not valid.
    """

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.get(READ_ITEMS_API, headers={})

    # ----------------------------------------------
    # GET OWN USER: VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 401
    assert response.json()["detail"] == "Access token not valid"


def test_read_items__normal_user(client: TestClient, normal_user_token_headers: dict) -> None:
    """
    Test the read items API endpoint for a normal user.
    This test verifies that a normal user can successfully retrieve a list of items
    with a specified limit using the read items API endpoint.

    Args:
        client (TestClient): The test client used to make requests to the API.
        normal_user_token_headers (dict): The headers containing the authentication token for a normal user.

    Assertions:
        - The response is not None.
        - The response status code is 200 (OK).
        - The response schema is valid.
        - The limit in the response schema matches the requested limit.
        - The total number of items in the response schema is greater than or equal to the requested limit.
        - The number of pages in the response schema is greater than or equal to 1.
        - The number of items in the response schema matches the requested limit.
    """

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    response = client.get(READ_ITEMS_API, headers=normal_user_token_headers, params={"limit": 2})
    responseScheme = PageSchema(**response.json())

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    assert response
    assert response.status_code == 200

    assert responseScheme
    assert responseScheme.limit == 2
    assert responseScheme.total >= 2
    assert responseScheme.pages >= 1
    assert len(responseScheme.items) == 2
