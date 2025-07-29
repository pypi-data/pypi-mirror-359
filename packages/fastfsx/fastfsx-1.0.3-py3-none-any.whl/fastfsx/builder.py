from pathlib import Path
from fastapi import APIRouter
from .loader import import_router_from_file
from .path_utils import path_from_dir


def build_router_tree(route_dir: Path) -> APIRouter:
    route_path = route_dir / "route.py"
    router = import_router_from_file(
        route_path) if route_path.exists() else None
    if router is None:
        router = APIRouter()

    for sub_dir in route_dir.iterdir():
        if sub_dir.is_dir():
            sub_router = build_router_tree(sub_dir)
            prefix = path_from_dir(sub_dir.relative_to(route_dir))
            router.include_router(sub_router, prefix=prefix)

    return router
