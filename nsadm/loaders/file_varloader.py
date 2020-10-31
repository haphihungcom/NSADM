import logging

import toml

from nsadm import loader_api


logger = logging.getLogger(__name__)


def load_vars_from_file(path):
    try:
        vars = toml.load(path)
        logger.debug('Loaded custom vars file "%s"', path)
        return vars
    except FileNotFoundError:
        raise FileNotFoundError('Custom vars file {} not found'.format(path))


@loader_api.var_loader
def get_vars(config):
    var_paths = config['file_varloader']['var_paths']
    vars = {}

    if isinstance(var_paths, list):
        for path in var_paths:
            load_vars_from_file(path)
    elif var_paths == '':
        logger.debug('No custom vars file found')
    else:
        load_vars_from_file(var_paths)

    return vars