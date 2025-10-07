"""
JSONPatchwork constants
"""


class JSONPatchError(Exception):
    """
    Exception raised when an error occurs while
    applying a JSON patch.
    """


class JSONPatchWarning(JSONPatchError):
    """
    Exception raised when a non-fatal error occurs
    while applying a JSON patch.
    """


class NoProgressBar:
    """
    Class for no progress bar
    """
    @classmethod
    def silent_warning(cls, warning):
        """
        Raise error when a warning occurs
        """
        raise JSONPatchError(
            "a warning occured while patching, " +
            "use a logger instead"
        ) from warning

    @classmethod
    def finish_sub_task(cls):
        """
        No finish sub task
        """
        return

    @classmethod
    def skip_sub_task(cls):
        """
        No skip sub task
        """
        return


ROOT = []
INFINITY = float("Infinity")
