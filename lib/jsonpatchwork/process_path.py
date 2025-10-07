"""
JSONPatchwork process path
"""
# Standard libraries
from re import compile as compile_regex
from types import FunctionType as function

# 3th party libraries
from .comparisons import get_comparison
from .constants import INFINITY, ROOT, JSONPatchError, JSONPatchWarning
from .helpers import no_regex


def process_path(original_obj, original_path):
    """
    Processes the object with the given path.
    """
    original_path_type = type(original_path)
    if original_path_type == dict:
        return _query_array(
            original_obj, [original_path]
        )
    if (
            original_path_type != list or
            original_path == ROOT
    ):
        return [(original_obj, original_path)]
    if len(original_path) == 1:
        path = original_path[0]
        return (
            _query_array(original_obj, path)
            if isinstance(path, list) else
            process_path(original_obj, path)
        )
    matches = []
    path = original_path[0]
    for target, key in (
            _query_array(original_obj, path)
            if isinstance(path, list) else
            process_path(original_obj, path)
    ):
        matches.extend(
            process_path(target[key], original_path[1:])
        )
    return matches


def _query_array(original_obj, original_path: list):
    matches = (
        original_obj.items()
        if isinstance(original_obj, dict) else
        enumerate(original_obj)
    )
    for query in original_path:
        if not isinstance(query, dict):
            raise JSONPatchWarning(
                f"Found {query!r} in query array, " +
                "expected object"
            )
        matches = _query(matches, query)
    return [
        (original_obj, index) for index, _ in matches
    ]


def _query(matches, original_path: dict):
    # By default it doesn't check the key'
    matched = (
        compile_regex(
            original_path["regex"]
        ).search if "regex" in original_path else
        no_regex
    )
    # By default it matches all elements
    key_path = original_path.get("key", ROOT)
    # By default it doesn't check the value
    has_value = original_path.get(
        "has_value", "value" in original_path
    )
    data = original_path.get("value", None)
    # By default it checks if key occurs when set
    comparison = get_comparison(
        original_path, "eq" if has_value else "in"
    )
    # By default the minimum is zero
    minimum = original_path.get("min", 0)
    # By default the cap is Infinity
    cap = original_path.get("cap", INFINITY)
    if cap < 1:
        raise JSONPatchError(
            f"capped matches below 1: {cap:f} < 1, " +
            "remove this operation instead"
        )
    if cap < minimum:
        raise JSONPatchError(
            "capped matches below minimum: " +
            f"{cap:f} < {minimum:f}, " +
            "remove this operation instead"
        )
    new_matches = []
    for match in matches:
        key, value = match
        # Allow checking for non string keys, & list
        # indexes
        if matched(str(key)) and any(
                _evaluate_entry(
                    target, path, comparison, has_value, data
                ) for target, path in process_path(
                    value, key_path
                )):
            new_matches.append(match)
            if cap <= len(new_matches):
                return new_matches
    if len(new_matches) < minimum:
        if key_path == ROOT:
            if not has_value:
                raise JSONPatchWarning(
                    f"found only {len(new_matches):d}/" +
                    f"{minimum:f} matches"
                )
            raise JSONPatchWarning(
                f"found only {len(new_matches):d}/" +
                f"{minimum:f} matches for value:" +
                f" {data!r}"
            )
        if not has_value:
            raise JSONPatchWarning(
                f"found only {len(new_matches):d}/" +
                f"{minimum:f} matches for key: " +
                f"{key_path!r}"
            )
        raise JSONPatchWarning(
            f"found only {len(new_matches):d}/" +
            f"{minimum:f} matches for key: " +
            f"{key_path!r}, value: {data!r}"
        )
    return new_matches


def _evaluate_entry(
        target, path, comparison: function,
        has_value: bool, data
):
    if path == ROOT:
        return not has_value or comparison(
            data, target
        )
    return (
        comparison(data, target[path])
        if has_value else comparison(path, target)
    )
