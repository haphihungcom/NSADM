import logging

import toml

from nsadm import loader_api


logger = logging.getLogger(__name__)


def load_vars_from_file(path):
    try:
        vars = toml.load(path)
        logger.debug('Loaded vars file "%s"', path)
        return vars
    except FileNotFoundError:
        raise FileNotFoundError('Vars file {} not found'.format(path))


def get_all_vars(paths):
    vars = {}

    if isinstance(paths, list):
        if not paths:
            logger.debug('No vars file found')
        else:
            for path in paths:
                vars.update(load_vars_from_file(path))
    elif paths == '':
        logger.debug('No vars file found')
    else:
        vars = load_vars_from_file(paths)

    return vars


@loader_api.var_loader
def get_vars(config):
    var_paths = config['file_varloader']['var_paths']
    return get_all_vars(var_paths)