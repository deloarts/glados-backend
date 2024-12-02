"""
    DB token schema.
"""

from typing import Optional

from pydantic import BaseModel


class TokenSchema(BaseModel):
    """OAuth2 token schema."""

    access_token: str
    token_type: str


class TokenPayloadSchema(BaseModel):
    """OAuth2 token payload schema."""

    sub: Optional[str | int | bool] = None
