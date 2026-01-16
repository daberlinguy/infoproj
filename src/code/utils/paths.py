import os
import sys


def _is_frozen():
    return hasattr(sys, "_MEIPASS")


def bundle_root():
    if _is_frozen():
        return sys._MEIPASS
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def project_root():
    if _is_frozen():
        return os.path.dirname(sys.executable)
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))


def resources_root():
    return os.path.join(bundle_root(), "resources")


def resources_path(*parts):
    """Get the full path to a resource file.

    Args:
        *parts: Path components relative to the resources folder.

    Returns:
        Absolute path to the resource file.

    Example::

        config_path = resources_path("textures.json")
        # Returns: /path/to/src/resources/textures.json
    """
    return os.path.join(resources_root(), *parts)


def assets_root():
    return os.path.join(resources_root(), "assets")


def assets_path(*parts):
    return os.path.join(assets_root(), *parts)


def data_root():
    return os.path.join(project_root(), "data")


def levels_root():
    return os.path.join(project_root(), "levels")


def bundled_data_root():
    return os.path.join(bundle_root(), "data")


def bundled_levels_root():
    return os.path.join(bundle_root(), "levels")
