"""
    Includes all web-endpoint-routes to the api router.
"""

from api.v1.key.endpoints import bought_items
from api.v1.key.endpoints import login
from api.v1.key.endpoints import projects
from fastapi.routing import APIRouter

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(bought_items.router, prefix="/items/bought", tags=["bought-items"])
