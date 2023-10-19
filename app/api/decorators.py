"""
    Decorator functions for endpoint routes.
"""

import functools
from ipaddress import ip_address
from ipaddress import ip_network
from typing import Any

from config import cfg
from fastapi import status
from multilog import log
from starlette.requests import Request
from starlette.responses import Response


def whitelist(func) -> Any:
    """
    Only allows whitelisted hosts to access the api.
    Requires the FastAPI class 'Request' passed as an argument within the
    path operation.
    E.g.: def get(request: Request)
    """

    # see: https://github.com/tiangolo/fastapi/issues/2662#issuecomment-761826593

    @functools.wraps(func)
    def wrapper_whitelist(*args, request: Request, **kwargs) -> Any:
        client = request.client
        if client is None:
            raise Exception("Failed fetching IP address of client.")

        client_ip = str(client.host)
        whitelisted = [ip_network(net) for net in cfg.server.whitelist]

        if any(ip_address(client_ip) in wl_ip for wl_ip in whitelisted):
            log.info(f"client IP {client_ip!r} is in whitelist.")
            value = func(*args, request=request, **kwargs)
        else:
            log.info(f"client IP {client_ip!r} not in whitelist.")
            value = Response(
                status_code=status.HTTP_403_FORBIDDEN, content="client not in whitelist"
            )

        return value

    return wrapper_whitelist
