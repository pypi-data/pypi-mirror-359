"""utils functions for peekpy"""

import inspect
import os


def get_full_name(func):
    """Get the full name of a function, including its module and qualified name."""
    module = func.__module__
    qualname = func.__qualname__

    return f"{module}.{qualname}" if module else qualname


def get_path_file_location(func):
    """Get the file path and line number where the function is defined.
    Returns a string in the format 'file_path:line_number'.
    """
    try:
        file_path = os.path.abspath(inspect.getfile(func))
        line_number = inspect.getsourcelines(func)[1]

        project_root = os.getcwd()
        relative_path = os.path.relpath(file_path, project_root)

        return f"{relative_path}:{line_number}"
    except (TypeError, OSError):
        return "Unknown location"
