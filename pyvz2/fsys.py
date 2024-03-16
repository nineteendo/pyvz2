"""FSys module for file system operations."""
# Copyright (C) 2022-2024 Nice Zombies
from __future__ import annotations

__all__: list[str] = ["RES_DIR"]
__author__: str = "Nice Zombies"

import sys
from pathlib import Path
from sys import executable

RES_DIR: Path = Path(
    executable if getattr(sys, "frozen", False) else sys.path[0],
).parent
