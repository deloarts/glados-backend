"""
    PWD Crypt module
"""

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_hash(plain_password: str, hashed_password: str) -> bool:
    """
    Returns True if the plain_password matches the hashed_password, otherwise False.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_hash(password: str) -> str:
    """Returns the hash from the given password."""
    return pwd_context.hash(password)
