"""
    Handles all routes to the pat-login-resource.
"""

from typing import Any

from api import deps
from fastapi.param_functions import Depends
from fastapi.routing import APIRouter
from models import model_user
from schemas import schema_user

router = APIRouter()


@router.post("/login/test-personal-access-token", response_model=schema_user.User)
def test_personal_access_token(
    current_user: model_user.User = Depends(
        deps.get_current_user_personal_access_token
    ),
) -> Any:
    """Test personal access token: This token must be provided as api key header."""
    return current_user
