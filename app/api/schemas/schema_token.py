"""
    DB token schema.
"""

from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    """OAuth2 token schema."""

    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    """OAuth2 token payload schema."""

    sub: Optional[int] = None
