"""CLInteract module for command line interaction."""
# Copyright (C) 2023-2024 Nice Zombies
# TODO(Nice Zombies): BasePicker
# TODO(Nice Zombies):  |-- BaseDictPicker
# TODO(Nice Zombies):  |    +-- DictPicker
# TODO(Nice Zombies):  +-- BaseSequencePicker
# TODO(Nice Zombies):       |-- SequencePicker
# TODO(Nice Zombies):       +-- InputPath
from __future__ import annotations

__all__: list[str] = ["input_str", "pause"]
__author__: str = "Nice Zombies"

from ._input_str import input_str
from ._pause import pause
