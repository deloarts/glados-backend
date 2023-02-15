"""
    Includes all web-endpoint-routes to the api router.
"""

from api.web_v1.endpoints import api_key, bought_items, host, login, logs, users
from fastapi.routing import APIRouter

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(api_key.router, prefix="/api-keys", tags=["api-keys"])
api_router.include_router(host.router, prefix="/host", tags=["host"])
api_router.include_router(logs.router, prefix="/logs", tags=["logs"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(
    bought_items.router, prefix="/items/bought", tags=["bought-items"]
)