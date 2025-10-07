"""19.io classes for command line input."""
# Linting arguments
# pylint: disable=unused-import

# Custom libraries
from ._classes import (ENUM, KEY, KEYINFO, RESULT, VALUE, VALUEINFO,
                       Representation)
from ._input_bytes import BaseInputStr, InputBytes, InputStr
from ._input_complex import InputFloat, InputInt
from ._input_enum import (BaseDictPicker, BasePicker, BaseSequencePicker,
                          DictPicker, SequencePicker)
from ._input_event import BaseInputEvent, InputEvent
from ._input_path import ConfigPicker, InputPath

__all__: list[str] = ['ENUM', 'KEY', 'KEYINFO', 'RESULT', 'VALUE', 'VALUEINFO']
__all__ += [
    'BaseDictPicker', 'BaseInputEvent', 'BasePicker', 'BaseSequencePicker',
    'ConfigPicker', 'DictPicker', 'InputBytes', 'InputEvent', 'InputFloat',
    'InputInt', 'InputPath', 'BaseInputStr', 'Representation',
    'SequencePicker', 'InputStr'
]
