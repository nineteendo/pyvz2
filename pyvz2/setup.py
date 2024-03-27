"""Dependencies of PyVZ2."""
# Copyright (C) 2024 Nice Zombies
from __future__ import annotations

__all__: list[str] = []
__author__: str = "Nice Zombies"

# mypy: disable-error-code=import-untyped
from setuptools import find_packages, setup

if __name__ == "__main__":
    setup(
        name="pyvz2-dependencies",
        version="0.1.0",
        description="Dependencies of PyVZ2",
        author="Nice Zombies",
        author_email="nineteendo19d0@gmail.com",
        url="https://github.com/nineteendo/pyvz2/tree/alpha",
        packages=find_packages(),  # Exclude forked packages
        py_modules=[],  # Include python modules
        license="GPL-3.0",
        requires=[],  # Include forked packages
    )
