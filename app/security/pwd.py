"""
    PWD Crypt module
"""

from bcrypt import checkpw
from bcrypt import gensalt
from bcrypt import hashpw


def verify_hash(plain_password: str, hashed_password: str) -> bool:
    """
    Returns True if the plain_password matches the hashed_password, otherwise False.
    """
    return checkpw(password=plain_password.encode("utf-8"), hashed_password=hashed_password.encode("utf-8"))


def get_hash(password: str) -> str:
    """Returns the hash from the given password."""
    pwd_bytes = password.encode("utf-8")
    salt = gensalt()
    hashed_password = hashpw(password=pwd_bytes, salt=salt).decode("utf-8")
    return hashed_password
