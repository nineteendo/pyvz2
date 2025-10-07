"""
JSONPatchwork comparisons
"""
# 3th party libraries
from .constants import JSONPatchWarning


def get_comparison(obj: dict, default: str):
    """
    Get comparison function
    """
    comparison_type = obj.get("type", default)
    if comparison_type not in comparisons:
        raise JSONPatchWarning(
            "Unknown comparison type: " +
            f"{comparison_type!r}"
        )
    return comparisons[comparison_type]


def contains(value_1, value_2):
    """
    Check if value 1 contains value 2
    """
    if isinstance(value_1, dict):
        return value_2 in value_1
    return -len(value_1) <= value_2 < len(value_1)


def contains_not(value_1, value_2):
    """
    Check if value 1 contains not value 2
    """
    if isinstance(value_2, dict):
        return value_2 not in value_1
    return not (
        -len(value_1) <= value_2 < len(value_1)
    )


def occurs_in(value_1, value_2):
    """
    Check if value 1 occurs in value 2
    """
    if isinstance(value_2, dict):
        return value_1 in value_2
    return -len(value_2) <= value_1 < len(value_2)


def occurs_not_in(value_1, value_2):
    """
    Check if value 1 occurs not in value 2
    """
    if isinstance(value_2, dict):
        return value_1 not in value_2
    return not (
        -len(value_2) <= value_1 < len(value_2)
    )


def is_less_than(value_1, value_2):
    """
    Check if value 1 is less than value 2
    """
    return value_1 < value_2


def is_less_than_or_equal_to(value_1, value_2):
    """
    Check if value 1 is less than or equal to value 2
    If correctly instantiated, lists & objects with
    NaN can also compare equal
    """
    # Special case to compare NaN
    if value_1 != value_1:
        return value_2 != value_2
    return value_1 <= value_2


def is_equal_to(value_1, value_2):
    """
    Check if value 1 is equal to value 2
    If correctly instantiated, lists & objects with
    NaN can also compare equal
    """
    # Special case to compare NaN
    if value_1 != value_1:
        return value_2 != value_2
    return value_1 == value_2


def is_not_equal_to(value_1, value_2):
    """
    Check if value 1 is not equal to value 2
    If correctly instantiated, lists & objects with
    NaN can also compare inequal
    """
    # Special case to compare NaN
    if value_1 != value_1:
        return value_2 == value_2
    return value_1 != value_2


def is_greater_than_or_equal_to(
        value_1, value_2
):
    """
    Check if value 1 is greater than or equal to
    value 2
    If correctly instiated, lists & objects with
    NaN can also compare equal
    """
    # Special case to compare NaN
    if value_1 != value_1:
        return value_2 != value_2
    return value_1 >= value_2


def is_greater_than(value_1, value_2):
    """
    Check if value 1 is greater than value 2
    """
    return value_1 > value_2


comparisons = {
    "co": contains,
    "cn": contains_not,
    "in": occurs_in,
    "ni": occurs_not_in,
    "lt": is_less_than,
    "le": is_less_than_or_equal_to,
    "eq": is_equal_to,
    "ne": is_not_equal_to,
    "ge": is_greater_than_or_equal_to,
    "gt": is_greater_than
}
