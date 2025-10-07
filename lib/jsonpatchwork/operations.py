"""
JSONPatchwork operation functions
"""
# Standard libraries
from copy import deepcopy
from functools import partial as partial_function

# 3th party libraries
from .comparisons import get_comparison
from .constants import INFINITY, ROOT, JSONPatchError, JSONPatchWarning
from .helpers import get_function_name, get_required_field
from .process_path import process_path


def get_operation(obj: dict):
    """
    Get operation function from dict
    """
    operation = get_required_field(obj, "op")
    if operation not in ops:
        raise JSONPatchWarning(
            f"Unknown operation: {operation!r}"
        )
    return ops[operation]


def set_value(original, patch: dict, _: str = ""):
    """
    Set the target to the value
    """
    path = get_required_field(patch, 'path')
    value = get_required_field(patch, 'value')
    for target, key in process_path(original, path):
        original = _set_value(
            original, target, key, value
        )
    return original


def _set_value(original, target, key, value):
    if key == ROOT:
        return value
    if isinstance(target, dict):
        target[key] = value
        return original
    # Allow appending to a list
    if key == INFINITY:
        target.append(value)
        return original
    target.insert(key, value)
    return original


def add_value(original, patch: dict, _: str = ""):
    """
    Add to the target
    """
    path = get_required_field(patch, 'path')
    value = get_required_field(patch, 'value')
    for target, key in process_path(original, path):
        original = _add_value(
            original, target, key, value
        )
    return original


def _add_value(original, target, key, value):
    if key == ROOT:
        if isinstance(original, dict):
            original.update(value)
            return original
        return original + value
    if isinstance(target[key], dict):
        target[key].update(value)
        return original
    target[key] += value
    return original


def replace_value(original, patch: dict, _: str = ""):
    """
    Replace the target with the value
    """
    path = get_required_field(patch, 'path')
    value = get_required_field(patch, 'value')
    for target, key in process_path(original, path):
        original = _replace_value(
            original, target, key, value
        )
    return original


def _replace_value(original, target, key, value):
    if key == ROOT:
        return value
    # Verify occurence in dict
    if isinstance(target, dict) and key not in target:
        raise KeyError(key)
    target[key] = value
    return original


def remove_value(original, patch: dict, _: str = ""):
    """
    Remove the target
    """
    path = get_required_field(patch, 'path')
    # Reverse order for correct removal
    for target, key in reversed(
            process_path(original, path)
    ):
        if key == ROOT:
            raise JSONPatchError(
                "can't remove root, " +
                "use replace with null instead"
            )
        del target[key]
    return original


def sort_value(original, patch: dict, _: str = ""):
    """
    Sort the target
    """
    path = get_required_field(patch, 'path')
    has_key = patch.get("has_key", "key" in patch)
    key_path = patch.get("key", ROOT)
    reverse = patch.get("reverse", False)
    for target, key in process_path(original, path):
        original = _sort_value(
            original, target, key, has_key, key_path,
            reverse
        )
    return original


def _sort_value(
        original, target, key, has_key: bool, key_path,
        reverse: bool
):
    if key == ROOT:
        return _sort_obj(
            original, has_key, key_path, reverse
        )
    target[key] = _sort_obj(
        target[key], has_key, key_path, reverse
    )
    return original


def _sort_obj(
        obj: dict, has_key: bool, key_path, reverse: bool
):
    if isinstance(obj, dict):
        return dict(sorted(
            obj.items(), key=partial_function(
                    _get_dict_keys, path=key_path
                    ) if has_key else None, reverse=reverse
        ))
    return sorted(obj, key=partial_function(
        _get_list_keys, path=key_path
    ), reverse=reverse)


def _get_dict_keys(item, path):
    _, obj = item
    return [
        obj[path] if path != ROOT else obj
        for obj, path in process_path(obj, path)
    ]


def _get_list_keys(obj, path):
    return [
        obj[path] if path != ROOT else obj
        for obj, path in process_path(obj, path)
    ]


def move_value(original, patch: dict, _: str = ""):
    """
    Move the target to the destination
    """
    path = get_required_field(patch, 'path')
    move_to = get_required_field(patch, 'to')
    matches = process_path(original, path)
    if (original, ROOT) in matches:
        raise JSONPatchError(
            "can't move root, use copy instead"
        )
    # Reversing, & a list comprehension for
    # correct moving
    for value in reversed([
            target.pop(key)
            for target, key in reversed(matches)
    ]):
        try:
            matches_to = process_path(
                original, move_to
            )
        except JSONPatchWarning as error:
            raise JSONPatchError(
                "a fatal error occured while moving, " +
                "use copy instead"
            ) from error
        except (KeyError, IndexError) as error:
            raise JSONPatchError(
                "can't move to child or non-existent " +
                "object, use copy instead"
            ) from error
        if not matches_to:
            raise JSONPatchError(
                "can't move to child or nothing, " +
                "use copy instead"
            )
        for destination, destination_key in (
                matches_to
        ):
            original = _set_value(
                original, destination, destination_key,
                value
            )
    return original


def copy_value(original, patch: dict, _: str = ""):
    """
    Copy the target to the destination
    """
    path = get_required_field(patch, 'path')
    copy_to = get_required_field(patch, 'to')
    # Deepcopy to prevent circular & normal
    # references
    for value in [
            deepcopy(
                target if key == ROOT else target[key]
            ) for target, key in process_path(
                original, path
            )]:
        for destination, destination_key in (
                process_path(original, copy_to)
        ):
            original = _set_value(
                original, destination, destination_key,
                value
            )
    return original


def merge_value(original, patch: dict, _: str = ""):
    """
    Merge the target with the destination
    """
    path = get_required_field(patch, 'path')
    merge_with = get_required_field(patch, 'with')
    matches = process_path(original, path)
    if (original, ROOT) in matches:
        raise JSONPatchError(
            "can't merge root, use combine instead"
        )
    # Reversing, & a list comprehension for
    # correct merging
    for value in reversed([
            target.pop(key)
            for target, key in reversed(matches)]
    ):
        try:
            matches_to = process_path(
                original, merge_with
            )
        except JSONPatchWarning as error:
            raise JSONPatchError(
                "a fatal error occured while merging, " +
                "use combine instead"
            ) from error
        except (KeyError, IndexError) as error:
            raise JSONPatchError(
                "can't merge with child or non-existent " +
                "object, use combine instead"
            ) from error
        if not matches_to:
            raise JSONPatchError(
                "can't merge with child or nothing, " +
                "use combine instead"
            )
        for destination, destination_key in (
                matches_to
        ):
            original = _add_value(
                original, destination, destination_key,
                value
            )
    return original


def combine_value(original, patch: dict, _: str = ""):
    """
    Combine the target with the destination
    """
    path = get_required_field(patch, 'path')
    combine_with = get_required_field(patch, 'with')
    # Deepcopy to prevent circular & normal
    # references
    for value in [
            deepcopy(
                target if key == ROOT else target[key]
            ) for target, key in process_path(
                original, path
            )]:
        for destination, destination_key in (
                process_path(original, combine_with)
        ):
            original = _add_value(
                original, destination, destination_key,
                value
            )
    return original


def check_value(original, patch: dict, _: str = ""):
    """
    Compare the target with the value
    """
    path = get_required_field(patch, 'path')
    value = get_required_field(patch, 'value')
    comparison = get_comparison(patch, "eq")
    for target, key in process_path(original, path):
        if key == ROOT:
            if not comparison(value, target):
                raise JSONPatchError(
                    f"check failed, {value!r} " +
                    f"{get_function_name(comparison)} " +
                    f"{target!r}"
                )
        elif not comparison(value, target[key]):
            raise JSONPatchError(
                f"check failed, {value!r} " +
                f"{get_function_name(comparison)} " +
                f"{target[key]!r}"
            )
    return original


def compare_value(original, patch: dict, _: str = ""):
    """
    Compare the target with the destination
    """
    path = get_required_field(patch, 'path')
    compare_with = get_required_field(patch, 'with')
    comparison = get_comparison(patch, "eq")
    for target, key in process_path(original, path):
        if key == ROOT:
            raise JSONPatchError(
                "can't compare root"
            )
        value = target[key]
        for destination, destination_key in (
                process_path(original, compare_with)
        ):
            if destination_key == ROOT:
                raise JSONPatchError(
                    "can't compare root"
                )
            if not comparison(
                    value, destination[destination_key]
            ):
                raise JSONPatchError(
                    f"comparison failed, {value!r} " +
                    f"{get_function_name(comparison)} " +
                    f"{destination[destination_key]!r}"
                )
    return original


def hash_value(
        original, patch: dict, patch_id: str = ""
):
    """
    Set the patch id at the target location,
    abort if the patch if has already been set
    """
    path = get_required_field(patch, 'path')
    for target, key in process_path(original, path):
        original = _hash_value(
            original, target, key, patch_id
        )
    return original


def _hash_value(original, target, key, patch_id):
    if key == ROOT:
        if original == patch_id:
            raise JSONPatchError(
                "can't apply a patch with hash check " +
                "twice"
            )
        return patch_id
    if isinstance(target, dict):
        if key in target and target[key] == patch_id:
            raise JSONPatchError(
                "can't apply a patch with hash check " +
                "twice"
            )
        target[key] = patch_id
        return original
    # Allow appending to a list
    if key == INFINITY:
        target.append(patch_id)
        return original
    if (
            -len(target) <= key < len(target) and
            target[key] == patch_id
    ):
        raise JSONPatchError(
            "can't apply a patch with hash check " +
            "twice"
        )
    target.insert(key, patch_id)
    return original


ops = {
    # Modify operations
    "set": set_value,
    "add": add_value,
    "replace": replace_value,
    "remove": remove_value,
    # Rearrange operations
    "sort": sort_value,
    "move": move_value,
    "copy": copy_value,
    "merge": merge_value,
    "combine": combine_value,
    # Check operations
    "check": check_value,
    "compare": compare_value,
    "hash": hash_value
}
