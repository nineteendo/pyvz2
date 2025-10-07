"""19.io functions to load data."""
# Standard libraries
from copy import deepcopy
from json import JSONDecodeError, load
from logging import warning
from os import fsdecode, rename
from os.path import basename, dirname, join
from typing import Any

# Custom libraries
from .path import StrOrBytesPath

__all__: list[str] = ['load_dict', 'load_json']


def load_dict(
    schema: dict[str, tuple[type, Any]], data: dict[str, Any]
) -> dict[str, Any]:
    """Load settings from arbitrary data."""
    settings: dict[str, Any] = {}
    for key, (value_type, default_value) in deepcopy(schema).items():
        value: Any = data.get(key, default_value)
        if isinstance(value, value_type):
            settings[key] = value
        else:
            settings[key] = default_value

    return settings


def load_json(
    path: StrOrBytesPath, schema: dict[str, tuple[type, Any]], *,
    strict: bool = False
) -> dict[str, Any]:
    """Load json with schema."""
    new_data: dict[str, Any] = {}
    newpath: str = fsdecode(path)
    try:
        with open(newpath, 'rb') as file:
            data: Any = load(file)
            if isinstance(data, dict):
                new_data = data
    except FileNotFoundError:
        # We're not interested in displaying FileNotFoundError
        pass
    except JSONDecodeError as err:
        if strict:
            raise

        warning(err)
        rename(newpath, join(dirname(newpath), 'broken_' + basename(newpath)))

    return load_dict(schema, new_data)
