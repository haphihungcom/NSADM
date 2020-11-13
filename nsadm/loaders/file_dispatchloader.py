import collections
import json
import logging
import toml


from nsadm import loader_api


logger = logging.getLogger(__name__)


class IDStore(collections.UserDict):
    """Store dispatch IDs on disk.

    Args:
        id_store_path (str): Path to store file.
    """

    def __init__(self, id_store_path):
        if id_store_path is None:
            pass
        self.id_store_path = id_store_path
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

        for name, info in dispatch_config.items():
            try:
                self.data[name] = info['id']
            except KeyError:
                pass

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

        return dispatches


class FileDispatchLoader():
    def __init__(self, id_store, dispatch_config, file_ext):
        self.id_store = id_store
        self.dispatch_config = dispatch_config
        self.file_ext = file_ext

    def get_dispatch_text(self, name):
        filename = '{}.{}'.format(name, self.file_ext)
        with open(filename) as f:
            text = f.read()

        return text

    def add_new_dispatch_id(self, name, dispatch_id):
        self.id_store[name] = dispatch_id


@loader_api.dispatch_loader
def init_loader(config):
    this_config = config['file_dispatchloader']

    id_store = IDStore(this_config['id_store_path'])
    dispatch_config = load_dispatch_config(this_config['dispatch_config_paths'])
    loader = FileDispatchLoader(id_store, dispatch_config, this_config['file_ext'])

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