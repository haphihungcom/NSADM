""" Utilities for this plugin.
"""


import collections
import inspect
import logging
import json
import importlib

import toml
import bs4


logger = logging.getLogger(__name__)


def get_dispatch_info(dispatch_config):
    """Compose and return dispatch information
    for use as context in the template renderer.

    Args:
        dispatch_config (dict): Dispatch configuration.
        id_store (IDStore): Dispatch ID store.

    Returns:
        dict: Dispatch information.
    """

    dispatch_info = {}
    for nation, dispatches in dispatch_config.items():
        for name, info in dispatches.items():
            info['owner_nation'] = nation
            dispatch_info[name] = info

    return dispatch_info


def get_funcs(path):
    """Get functions from a module file (.py).

    Args:
        path (str): Path to module file (.py).
    """

    module = load_module(path)
    return inspect.getmembers(module, inspect.isfunction)


def load_module(path, name='module'):
    """Load module from an absolute path.

    Args:
        path (str): Path to module file (.py)
        name (str): Name of module for reference needs. Defaults to 'module'
    """

    spec = importlib.util.spec_from_file_location(name, path)
    if spec is not None:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module


def add_extension(name):
    """Get file name with .py extension.

    Args:
        name (str): Name

    Returns:
        str
    """

    return '{}.py'.format(name)
