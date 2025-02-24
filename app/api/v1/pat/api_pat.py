"""
    Includes all pat-endpoint-routes to the api router.
"""

from api.v1.pat.endpoints import bought_items
from api.v1.pat.endpoints import login
from api.v1.pat.endpoints import projects
from api.v1.pat.endpoints import user_time
from api.v1.pat.endpoints import users
from fastapi.routing import APIRouter

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(bought_items.router, prefix="/items/bought", tags=["bought-items"])
api_router.include_router(user_time.router, prefix="/user-time", tags=["user-time"])
