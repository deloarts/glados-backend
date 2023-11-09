"""
    Includes all web-endpoint-routes to the api router.
"""

from api.web_v1.endpoints import api_key
from api.web_v1.endpoints import bought_items
from api.web_v1.endpoints import host
from api.web_v1.endpoints import login
from api.web_v1.endpoints import logs
from api.web_v1.endpoints import tools_stock_cut
from api.web_v1.endpoints import users
from fastapi.routing import APIRouter

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(api_key.router, prefix="/api-keys", tags=["api-keys"])
api_router.include_router(host.router, prefix="/host", tags=["host"])
api_router.include_router(logs.router, prefix="/logs", tags=["logs"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(bought_items.router, prefix="/items/bought", tags=["bought-items"])
api_router.include_router(tools_stock_cut.router, prefix="/tools/stock-cut", tags=["tools-stock-cut"])
