"""
    Authentication & Security.
"""

from datetime import UTC
from datetime import datetime
from datetime import timedelta
from typing import Any
from typing import Optional

from api.schemas.token import TokenPayloadSchema
from config import cfg
from const import SECRET_KEY_NON_PERSISTENT
from const import SECRET_KEY_PERSISTENT
from jose import jwt
from multilog import log
from pydantic import ValidationError


def get_secret_key(persistent: bool) -> str:
    """
    Returns the secret key for jwt encoding.
    If debug is enabled, the persistent key will be used.
    """
    if cfg.debug or persistent:
        log.debug("Using PERSISTENT key")
        return SECRET_KEY_PERSISTENT
    log.debug("Using NON PERSISTENT key")
    return SECRET_KEY_NON_PERSISTENT


def create_access_token(subject: str | Any, persistent: bool, expires_delta: Optional[timedelta] = None) -> str:
    """Creates and returns a new reusable OAuth2 access token.

    Args:
        subject (str | Any): The subject to encode (most times the model ID).
        persistent (bool): Whether or not to use the persistent jwt encoding key.
        expires_delta (Optional[timedelta], optional): The expiration time in minutes. \
            Defaults to None. If None, the value from the config file is used.

    Returns:
        str: A jwt encoded access token.
    """
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=cfg.security.expire_minutes)

    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, get_secret_key(persistent), algorithm=cfg.security.algorithm)
    return encoded_jwt


def get_subject_from_access_token(token: str, persistent: bool) -> Optional[str | int | bool]:
    """Extracts the subject from the access token.

    Args:
        token (_type_): A jwt access token.
        persistent (bool): Whether or not to use the persistent jwt decoding key.

    Returns:
        Optional[int]: The subject (user id) from the given token.
    """
    if not token:
        return None
    try:
        payload = jwt.decode(token, get_secret_key(persistent), algorithms=[cfg.security.algorithm])
        token_data = TokenPayloadSchema(**payload)
    except (ValidationError, Exception):
        return None
    return token_data.sub  # a.k.a the id
