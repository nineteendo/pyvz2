"""Dependencies of PyVZ2."""
# Copyright (C) 2024 Nice Zombies
# mypy: disable-error-code=import-untyped
from __future__ import annotations

__all__: list[str] = []
__author__: str = "Nice Zombies"

from setuptools import find_packages, setup

if __name__ == "__main__":
    setup(
        name="pyvz2-dependencies",
        version="0.1.0",
        packages=find_packages(),  # Exclude forked packages
        py_modules=[],
        author="Nice Zombies",
        author_email="nineteendo19d0@gmail.com",
        description="Dependencies of PyVZ2",
        license="GPL-3.0",
        url="https://github.com/nineteendo/pyvz2/tree/alpha",
    )
