"""Load dispatches from plain text files with TOML dispatch configuration.
"""

import pathlib
import collections
import json
import logging
import toml

from nsadm import info
from nsadm import exceptions
from nsadm import loader_api

DEFAULT_ID_STORE_FILENAME = 'dispatch_id.json'
DEFAULT_EXT = '.txt'

logger = logging.getLogger(__name__)


class IDStore(collections.UserDict):
    """Store dispatch IDs on disk.

    Args:
        id_store_path (str): Path to store file.
    """

    def __init__(self, id_store_path):
        if id_store_path is None:
            self.id_store_path = pathlib.Path(info.DATA_DIR, DEFAULT_ID_STORE_FILENAME)
        else:
            self.id_store_path = pathlib.Path(id_store_path)
        self.saved = False
        super().__init__()

    def load_from_json(self):
        """Load dispatch IDs from configured JSON file.
        """

        if self.id_store_path is None:
            return

        try:
            with open(self.id_store_path) as f:
                self.data = json.load(f)
                logger.debug('Loaded id store: %r', self.data)
        except FileNotFoundError:
            self.save()
            logger.debug('Created id store at "%s"', self.id_store_path)

    def load_from_dispatch_config(self, dispatch_config):
        """Load dispatch IDs from dispatch configurations.

        Args:
            dispatch_config (dict): Dispatch configuration.
        """

        for nation in dispatch_config.keys():
            for name, config in dispatch_config[nation].items():
                if 'action' in config and config['action'] == 'remove':
                    continue

                if 'ns_id' not in config:
                    continue

                self.data[name] = config['ns_id']

        self.saved = False

    def __setitem__(self, name, dispatch_id):
        """Add new dispatch ID.

        Args:
            name (str): Dispatch file name.
            dispatch_id (int): Dispatch ID.
        """

        self.data[name] = dispatch_id
        self.saved = False

    def save(self):
        """Save ID store into file.
        """

        if self.saved:
            return

        with open(self.id_store_path, 'w') as f:
            json.dump(self.data, f)
            self.saved = True
            logger.debug('Saved id store: %r', self.data)


def define_action(name, config, id_dont_exist):
    """Determine action to do on dispatch.

    Args:
        name (str): Dispatch name
        config (dict): Dispatch config
        id_dont_exist (bool): Dispatch doesn't have id

    Returns:
        str: Action
    """

    # Use user-configured action if exists
    if 'action' in config:
        if config['action'] == 'remove' and id_dont_exist:
            logger.error('No dispatch id found for dispatch "%s". Will not remove it.', name)
            return 'skip'

        if config['action'] == 'edit' and id_dont_exist:
            logger.error('No dispatch id found for dispatch "%s". Will not edit it.', name)
            return 'skip'

        return config['action']

    if id_dont_exist:
        logger.debug(('No dispatch id found for dispatch "%s".'
                      'Will attempt to create the dispatch.'), name)
        return 'create'

    return 'edit'


def merge_with_id_store(dispatch_config, id_store):
    """Add id and action into dispatch config.

    Args:
        dispatch_config (dict): Dispatch config
        id_store: Dispatch id store

    Returns:
        dict: New dispatch config
    """

    new_dispatch_config = {}
    for nation in dispatch_config.keys():
        new_dispatch_config[nation] = {}
        for name in dispatch_config[nation].keys():
            config = dispatch_config[nation][name]
            id_dont_exist = False
            id_user_defined = True
            # Use user-configured dispatch id if exists
            if 'ns_id' not in config:
                id_user_defined = False
                if name in id_store:
                    config['ns_id'] = id_store[name]
                else:
                    id_dont_exist = True

            action = define_action(name, config, id_dont_exist)
            if action == 'skip':
                continue

            config['action'] = action
            new_dispatch_config[nation][name] = config

            # Only delete id in store if the id of dispatch to remove
            # is not user-configured
            if action == 'remove' and not id_user_defined:
                del id_store[name]

        # Delete this nation to avoid useless login
        if not new_dispatch_config[nation]:
            del new_dispatch_config[nation]

    return new_dispatch_config


def load_dispatch_config(dispatch_config_path):
    """Load dispatch configuration files.

    Args:
        dispatch_config_path (str|list): Dispatch configuration path(s)

    Returns:
        dict: Dispatch configuration
    """

    dispatches = {}
    if isinstance(dispatch_config_path, list):
        for dispatch_config in dispatch_config_path:
            dispatches.update(toml.load(dispatch_config))
            logger.debug('Loaded dispatch config: "%r"', dispatches)
        logger.info('Loaded all dispatch config files')
    else:
        dispatches = toml.load(dispatch_config_path)
        logger.debug('Loaded dispatch config: "%r"', dispatches)

    return dispatches


class FileDispatchLoader():
    """Load dispatches from plain text files.

    Args:
        id_store: Dispatch id store
        dispatch_config (dict): Dispatch config
        file_ext (str): Dispatch file extension
    """

    def __init__(self, id_store, dispatch_config, template_path, file_ext):
        self.id_store = id_store
        self.dispatch_config = dispatch_config
        self.template_path = template_path
        self.file_ext = file_ext

    def get_dispatch_text(self, name):
        """Get a dispatch's text content.

        Args:
            name (str): Dispatch name

        Raises:
            exceptions.LoaderError: Could not find dispatch file

        Returns:
            str: Text
        """

        file_path = pathlib.Path(self.template_path, name).with_suffix(self.file_ext)
        try:
            return file_path.read_text()
        except FileNotFoundError as err:
            logger.error('Could not find dispatch template file "%s".', file_path)
            raise exceptions.DispatchTextNotFound from err

    def add_new_dispatch_id(self, name, dispatch_id):
        """Add id of new dispatch into id store.

        Args:
            name (str): Dispatch name
            dispatch_id (str): Dispatch id
        """

        self.id_store[name] = dispatch_id

    def save_id_store(self):
        """Save all changes to id store.
        """

        self.id_store.save()


@loader_api.dispatch_loader
def init_dispatch_loader(config):
    this_config = config.get('file_dispatchloader')
    if this_config is None:
        raise exceptions.LoaderError('File dispatch loader does not have config.')

    dispatch_config_paths = this_config.get('dispatch_config_paths')
    if dispatch_config_paths is None:
        raise exceptions.LoaderError('There is no dispatch config!')
    dispatch_config = load_dispatch_config(dispatch_config_paths)
    if not dispatch_config:
        logger.error('Dispatch config is empty!')

    id_store = IDStore(this_config.get('id_store_path'))
    id_store.load_from_json()

    dispatch_config = merge_with_id_store(dispatch_config, id_store)

    if this_config.get('save_config_defined_id', False):
        id_store.load_from_dispatch_config(dispatch_config)

    loader = FileDispatchLoader(id_store, dispatch_config,
                                this_config['template_path'],
                                this_config.get('file_ext', DEFAULT_EXT))

    return loader


@loader_api.dispatch_loader
def get_dispatch_config(loader):
    return loader.dispatch_config


@loader_api.dispatch_loader
def get_dispatch_text(loader, name):
    return loader.get_dispatch_text(name)


@loader_api.dispatch_loader
def add_dispatch_id(loader, name, dispatch_id):
    return loader.add_new_dispatch_id(name, dispatch_id)


@loader_api.dispatch_loader
def cleanup_dispatch_loader(loader):
    loader.save_id_store()
