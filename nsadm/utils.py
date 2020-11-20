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


def get_dispatch_info(dispatch_config, id_store):
    """Compose and return dispatch information
    for use as context in the template renderer.

    Args:
        dispatch_config (dict): Dispatch configuration.
        id_store (IDStore): Dispatch ID store.

    Returns:
        dict: Dispatch information.
    """

    dispatches = dispatch_config
    for name in id_store.keys():
        if name in dispatches:
            dispatches[name]['id'] = id_store[name]
        else:
            dispatches[name] = {'id': id_store[name]}

    return dispatches


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


def load_dispatch_config(dispatch_config_path):
        """Load dispatch configuration files.

        Args:
            dispatch_config_path (str|list): Dispatch configuration path(s).

        Returns:
            dict: Dispatch configuration.
        """

        if isinstance(dispatch_config_path, str):
            dispatches = toml.load(dispatch_config_path)
            logger.info('Loaded dispatch config: "%r"', dispatches)
        elif isinstance(dispatch_config_path, list):
            dispatches = {}
            for dispatch_config in dispatch_config_path:
                dispatches.update(toml.load(dispatch_config))
                logger.debug('Loaded dispatch config: "%r"', dispatches)
                logger.info('Loaded all dispatch config files')
        else:
            dispatches = None

        return dispatches


def get_id_from_html(html_text):
    """Get new dispatch ID from respond's HTML.

    Args:
        html_text (str): HTML text of respond.

    Returns:
        int: Dispatch ID.
    """

    soup = bs4.BeautifulSoup(html_text, 'html.parser')

    new_dispatch_url = soup.find(name='p', attrs={'class': 'info'}).a['href']

    dispatch_id = new_dispatch_url.split('id=')[1]

    return int(dispatch_id)


def add_extension(name):
    """Get file name with .py extension.

    Args:
        name (str): Name

    Returns:
        str
    """

    return '{}.py'.format(name)
