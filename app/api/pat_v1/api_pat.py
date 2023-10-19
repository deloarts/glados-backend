"""
    Includes all web-endpoint-routes to the api router.
"""

from api.pat_v1.endpoints import bought_items
from api.pat_v1.endpoints import login
from fastapi.routing import APIRouter

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(
    bought_items.router, prefix="/items/bought", tags=["bought-items"]
)
