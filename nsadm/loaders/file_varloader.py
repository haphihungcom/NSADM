import logging

import toml

from nsadm import loader_api


logger = logging.getLogger(__name__)


def load_vars_from_file(path):
    """Load variables from a TOML file.

    Args:
        path (str): File path

    Raises:
        FileNotFoundError: [description]

    Returns:
        [type]: [description]
    """
    try:
        vars = toml.load(path)
        logger.debug('Loaded vars file "%s"', path)
        return vars
    except FileNotFoundError:
        logger.error('Could not find var file "{}"'.format(path))
        return None


def get_all_vars(paths):
    """Get variables from file(s).

    Args:
        paths (str|list): File path(s)

    Returns:
        dict: Variables
    """

    loaded_vars = {}

    if isinstance(paths, list):
        if not paths:
            logger.debug('No var file found')
        else:
            for path in paths:
                file_vars = load_vars_from_file(path)
                if file_vars:
                    loaded_vars.update(file_vars)
    elif paths == '':
        logger.debug('No var file found')
    else:
        loaded_vars = load_vars_from_file(paths)

    return loaded_vars


@loader_api.var_loader
def get_vars(config):
    var_paths = config['file_varloader']['var_paths']
    return get_all_vars(var_paths)