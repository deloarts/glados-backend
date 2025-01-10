"""
    The fastapi init.
"""

import uvicorn
from api.v1.key import api_key
from api.v1.pat import api_pat
from api.v1.web import api_web
from config import cfg
from const import VERSION
from fastapi.applications import FastAPI
from fastapi.staticfiles import StaticFiles
from multilog import log
from starlette.middleware.cors import CORSMiddleware

# from starlette.responses import RedirectResponse

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

- WEB API: [{cfg.server.api.web}/docs]({cfg.server.api.web}/docs)
- PAT API: [{cfg.server.api.pat}/docs]({cfg.server.api.pat}/docs)
- KEY API: [{cfg.server.api.key}/docs]({cfg.server.api.key}/docs)

"""

app = FastAPI(
    title="GLADOS",
    version=VERSION,
    description=DESC_PROD if not cfg.debug else description_debug,
    servers=[
        {"url": cfg.server.api.web, "description": "WEB API"},
        {"url": cfg.server.api.pat, "description": "Personal Access Token API"},
        {"url": cfg.server.api.key, "description": "KEY API"},
    ],
)
app.mount(cfg.server.api.web, web_api)
app.mount(cfg.server.api.pat, pat_api)
app.mount(cfg.server.api.key, key_api)
if cfg.server.static.enable:
    app.mount(cfg.server.static.url, StaticFiles(directory=cfg.server.static.folder, html=True), name="static")
    log.info(f"Static files mounted at url {cfg.server.static.url!r} from {cfg.server.static.folder!r}")


# @app.get("/")
# async def route_root() -> RedirectResponse:
#     """Route to the server root. Redirects to /docs."""
#     return RedirectResponse(url="/docs")


def run():
    """Runs the uvicorn server."""
    uvicorn.run(
        "server:app",
        reload=cfg.debug,
        host=cfg.server.host,
        port=cfg.server.port,
        ssl_keyfile=cfg.server.ssl.keyfile,
        ssl_certfile=cfg.server.ssl.certfile,
        server_header=cfg.server.headers_server,
        proxy_headers=cfg.server.headers_proxy,
        forwarded_allow_ips=cfg.server.forwarded_allowed_ips,
    )
