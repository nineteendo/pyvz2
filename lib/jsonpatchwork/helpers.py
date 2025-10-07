"""
JSONPatchwork helper functions
"""
# Standard libraries
from hashlib import sha256 as sha256_hash
from types import FunctionType as function

# 3th party libraries
from .constants import JSONPatchWarning


def get_patch_hash(patches: list):
    """
    Get sha 256 hash of patches
    """
    return sha256_hash(
        f"{patches!r}".encode()
    ).hexdigest()


def get_required_field(obj: dict, key: str):
    """
    Get required field from a dict
    """
    if key not in obj:
        raise JSONPatchWarning(
            f"Missing required field: {key!r}"
        )
    return obj[key]


def get_function_name(func: function):
    """
    Get a human readable name of a function
    """
    return func.__name__.replace("_", " ")


def no_regex(_: str):
    """
    No regex
    """
    return True
