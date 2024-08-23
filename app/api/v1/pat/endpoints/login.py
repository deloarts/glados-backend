"""
    Handles all routes to the pat-login-resource.
"""

from typing import Any

from api import deps
from api.schemas.user import UserSchema
from db.models import UserModel
from fastapi.param_functions import Depends
from fastapi.routing import APIRouter

router = APIRouter()


@router.post("/login/test-personal-access-token", response_model=UserSchema)
def test_personal_access_token(current_user: UserModel = Depends(deps.get_current_user_personal_access_token)) -> Any:
    """Test personal access token: This token must be provided as api key header."""
    return current_user
