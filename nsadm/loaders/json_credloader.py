"""Load nation login credentials from JSON file.
"""

import collections
import json
import logging

import appdirs

from nsadm import info
from nsadm import loader_api


logger = logging.getLogger(__name__)


class JSONCredLoader(collections.UserDict):
    """JSON Credential Loader.

    Args:
        config (dict): Configuration
    """

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.json_path = None
        self.saved = True

    def set_path(self):
        """Set JSON file path. Use system default
        if none is provided in config.
        """

        if not 'cred_path' in self.config:
            self.json_path = appdirs.user_data_dir(info.APP_NAME, info.AUTHOR)
        else:
            self.json_path = self.config['cred_path']

    def load_creds(self):
        """Get all login credentials

        Returns:
            dict: Nation name and autologin code
        """

        try:
            with open(self.json_path) as f:
                self.data = json.load(f)
        except FileNotFoundError:
            pass

    def __setitem__(self, name, x_autologin):
        """Add a new credential into file.

        Args:
            name (str): Nation name
            x_autologin (str): X-Autologin code
        """

        self.data[name] = x_autologin
        self.saved = False

    def __delitem__(self, name):
        """Remove a credential from file.

        Args:
            name (str): Nation name
        """

        del self.data[name]
        self.saved = False

    def save(self):
        """Save creds to JSON file.
        """

        if not self.saved:
            with open(self.json_path, 'w') as f:
                json.dump(self.data, f)


@loader_api.cred_loader
def init_cred_loader(config):
    config = config['json_credloader']
    loader = JSONCredLoader(config)
    loader.set_path()
    loader.load_creds()

    return loader


@loader_api.cred_loader
def get_creds(loader):
    return loader.data


@loader_api.cred_loader
def add_cred(loader, name, x_autologin):
    loader[name] = x_autologin


@loader_api.cred_loader
def remove_cred(loader, name):
    del loader[name]


@loader_api.cred_loader
def cleanup_cred_loader(loader):
    loader.save()
