"""FSys tests."""
# Copyright (C) 2024 Nice Zombies
from __future__ import annotations

__all__: list[str] = []
__author__: str = "Nice Zombies"

from . import RES_DIR


def test_res_dir() -> None:
    """Test RES_DIR."""
    assert RES_DIR.is_dir()
