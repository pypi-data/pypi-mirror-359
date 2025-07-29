from pathlib import Path


class InvalidRouterError(Exception):
    def __init__(self, path: Path):
        super().__init__(f"`router` not found or invalid in {path}")
