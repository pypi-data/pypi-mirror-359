import importlib.util
from pathlib import Path
from fastapi import APIRouter
from .exceptions import InvalidRouterError


def import_router_from_file(route_file: Path) -> APIRouter:
    spec = importlib.util.spec_from_file_location("route_module", route_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    router = getattr(module, "router", None)
    if not isinstance(router, APIRouter):
        raise InvalidRouterError(route_file)
    return router
