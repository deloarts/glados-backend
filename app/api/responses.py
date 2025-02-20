"""
    Default responses for the API
"""

from typing import Any
from typing import Dict

from fastapi import status
from pydantic import BaseModel

ResponseType = Dict[int | str, Dict[str, Any]]


class ResponseModelDetail(BaseModel):
    detail: str


HTTP_401_RESPONSE: ResponseType = {
    status.HTTP_401_UNAUTHORIZED: {"model": ResponseModelDetail, "description": "Authentication failed"}
}
