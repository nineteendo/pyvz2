"""19.io sub module for console input."""
# InputHandler hierarchy:
# DONE: BaseInputHandler
# DONE:  |-- Pause
# DONE:  +-- BaseInputStr
# DONE:       |-- InputStr
# TODO:       +-- BasePicker
# TODO:            |-- BaseDictPicker
# TODO:            |    +-- DictPicker
# TODO:            +-- BaseSequencePicker
# TODO:                 |-- SequencePicker
# TODO:                 +-- InputPath

__all__: list[str] = [
    # snake_case
    'input_str', 'pause'
]

# Custom libraries
from ._input_str import input_str
from ._pause import pause
