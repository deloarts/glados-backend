"""
    Handles all routes to the uses-resource.
"""

from typing import Any

from api.deps import get_current_user_personal_access_token
from api.responses import HTTP_401_RESPONSE
from api.schemas.user import UserSchema
from db.models import UserModel
from db.session import get_db
from fastapi.param_functions import Depends
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

router = APIRouter()


@router.get(
    "/me",
    response_model=UserSchema,
    responses={**HTTP_401_RESPONSE},
)
def read_user_me(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user_personal_access_token),
) -> Any:
    """Get current user from the personal access token."""
    return current_user
