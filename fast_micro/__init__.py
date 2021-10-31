import socket, time
from typing import List
from fastapi import FastAPI
from starlette.middleware import Middleware
from starlette_context import plugins
from starlette_context.middleware import RawContextMiddleware
from fast_micro.logger import setup_logging
from fast_micro.middleware import RequestEncrichMiddleware


def create_app(
        log_level: str = "INFO", skip_route_logging: List[str] = None, 
        health_url: str = "/health", middleware: List[Middleware] = None
    ) -> FastAPI:
    
    skip_route_logging = skip_route_logging if skip_route_logging else [health_url]
    middleware = [
        Middleware(RawContextMiddleware, plugins=(
            plugins.RequestIdPlugin(),
            plugins.CorrelationIdPlugin(),
        )),
        Middleware(RequestEncrichMiddleware, skip_routes=skip_route_logging),
    ].extend(middleware)

    app: FastAPI = FastAPI(middleware=middleware)

    @app.on_event("startup")
    async def _startup_event() -> None:
        setup_logging(log_level)

    @app.get(health_url)
    def _default_get_health():
        """Returns health information from the app
        """
        return {
            "hostname": socket.gethostname(),
            "status": "success",
            "timestamp": time.time()
        }

    return app