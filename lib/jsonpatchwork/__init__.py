"""
JSONPatchwork module for patching json data.

Python 3.8- is not supported & won't receive bug fixes.
"""
# 3th party libraries
from .constants import JSONPatchWarning, NoProgressBar
from .helpers import get_patch_hash
from .operations import get_operation


def patch_json(original, patches: list, progress_bar: object = NoProgressBar):
    """Apply jsonpatchwork patch."""
    patch_id = get_patch_hash(patches)
    for patch in patches:
        try:
            operation = get_operation(patch)
            original = operation(
                original, patch, patch_id
            )
        except (
                JSONPatchWarning, IndexError, KeyError
        ) as warning:
            progress_bar.silent_warning(warning)
            progress_bar.skip_sub_task()
        else:
            progress_bar.finish_sub_task()

    return original
