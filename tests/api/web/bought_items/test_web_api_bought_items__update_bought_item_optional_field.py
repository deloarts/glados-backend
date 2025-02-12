"""
    TEST WEB API -- BOUGHT ITEMS -- UPDATE OPTIONAL FIELD
"""

from string import Template
from typing import Dict
from typing import List
from typing import Tuple

from api.schemas.bought_item import BoughtItemSchema
from api.v1.web.endpoints.bought_items import OptionalFieldName
from config import cfg
from crud.bought_item import crud_bought_item
from crud.project import crud_project
from fastapi.testclient import TestClient
from httpx import Response
from locales import lang
from sqlalchemy.orm import Session

from tests.utils.bought_item import create_random_item
from tests.utils.project import create_random_project
from tests.utils.user import get_test_guest_user
from tests.utils.user import get_test_super_user
from tests.utils.user import get_test_user
from tests.utils.utils import random_lower_string

UPDATE_ITEM_OPTIONAL_FIELD = Template(f"{cfg.server.api.web}/items/bought/$item_id/field/optional/$field_name")


def test_update_item_optional_field__unauthorized(client: TestClient, db: Session) -> None:
    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_item = create_random_item(db)

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    responses: List[Response] = []
    for field in OptionalFieldName:
        responses.append(
            client.put(UPDATE_ITEM_OPTIONAL_FIELD.substitute(item_id=t_item.id, field_name=field.value), headers={})
        )

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    for response in responses:
        assert response
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid access token"


def test_update_item_optional_field__normal_user(
    client: TestClient, normal_user_token_headers: Dict[str, str], db: Session
) -> None:
    # ----------------------------------------------
    # PREPARATION
    # ----------------------------------------------

    t_item = create_random_item(db)
    t_value = random_lower_string()

    # ----------------------------------------------
    # METHODS TO TEST
    # ----------------------------------------------

    for field in OptionalFieldName:
        response = client.put(
            UPDATE_ITEM_OPTIONAL_FIELD.substitute(item_id=t_item.id, field_name=field.value),
            headers=normal_user_token_headers,
            params={"value": t_value},
        )
        responseSchema = BoughtItemSchema(**response.json())

        # ----------------------------------------------
        # VALIDATION
        # ----------------------------------------------

        assert response
        assert response.status_code == 200
        assert response.json()[str(field.value).replace("-", "_")] == t_value

        assert responseSchema
