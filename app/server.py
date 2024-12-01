"""
    The fastapi init.
"""

import uvicorn
from api.v1.key import api_key
from api.v1.pat import api_pat
from api.v1.web import api_web
from config import cfg
from const import API_KEY_V1
from const import API_PAT_V1
from const import API_WEB_V1
from const import VERSION
from fastapi.applications import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

web_api = FastAPI(title="GLADOS WEB API", openapi_url="/docs.json" if cfg.debug else None)
web_api.include_router(api_web.api_router)
web_api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pat_api = FastAPI(title="GLADOS PAT API", openapi_url="/docs.json" if cfg.debug else None)
pat_api.include_router(api_pat.api_router)
pat_api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

key_api = FastAPI(title="GLADOS KEY API", openapi_url="/docs.json" if cfg.debug else None)
key_api.include_router(api_key.api_router)
key_api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DESC_PROD = "API documentation is not available in production."
description_debug = f"""
GLADOS API:

- WEB API: [{API_WEB_V1}/docs]({API_WEB_V1}/docs)
- PAT API: [{API_PAT_V1}/docs]({API_PAT_V1}/docs)
- KEY API: [{API_KEY_V1}/docs]({API_KEY_V1}/docs)

"""

app = FastAPI(
    title="GLADOS",
    version=VERSION,
    description=DESC_PROD if not cfg.debug else description_debug,
    servers=[
        {"url": API_WEB_V1, "description": "WEB API"},
        {"url": API_PAT_V1, "description": "Personal Access Token API"},
        {"url": API_KEY_V1, "description": "KEY API"},
    ],
)
app.mount(API_WEB_V1, web_api)
app.mount(API_PAT_V1, pat_api)
app.mount(API_KEY_V1, key_api)
# app.mount("/", StaticFiles(directory=static_folder), name="static")


@app.get("/")
async def route_root() -> RedirectResponse:
    """Route to the server root. Redirects to /docs."""
    return RedirectResponse(url="/docs")


def run():
    """Runs the uvicorn server."""
    uvicorn.run(
        "server:app",
        reload=cfg.debug,
        host=cfg.server.host,
        port=cfg.server.port,
    )
