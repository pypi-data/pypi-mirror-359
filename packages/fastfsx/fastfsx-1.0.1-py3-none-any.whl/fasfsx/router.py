from pathlib import Path
from fastapi import APIRouter
from .builder import build_router_tree


class FileRouter:
    def __init__(self, pages_dir: str = "pages"):
        self.pages_dir = Path(pages_dir).resolve()

    def build(self) -> APIRouter:
        return build_router_tree(self.pages_dir)
