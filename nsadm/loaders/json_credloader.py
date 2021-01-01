"""Load nation login credentials from JSON file.
"""

import json
import logging

import appdirs

from nsadm import info
from nsadm import loader_api


logger = logging.getLogger(__name__)


class JSONCredLoader():
    """JSON Credential Loader.

    Args:
        config (dict): Configuration
    """

    def __init__(self, config):
        self.config = config
        self.json_path = None

    def set_path(self):
        """Set JSON file path. Use system default
        if none is provided in config.
        """

        if not 'cred_path' in self.config:
            self.json_path = appdirs.user_data_dir(info.APP_NAME, info.AUTHOR)
        else:
            self.json_path = self.config['cred_path']

    def get_creds(self):
        """Get all login credentials

        Returns:
            dict: Nation name and autologin code
        """

        try:
            with open(self.json_path) as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error('Could not find any login credential, Please add one!')

    def add_cred(self, name, x_autologin):
        """Add a new credential into file.

        Args:
            name (str): Nation name
            x_autologin (str): X-Autologin code
        """

        new_creds = {name: x_autologin}

        try:
            with open(self.json_path, 'r+') as f:
                creds = json.load(f)
                new_creds.update(creds)
                f.seek(0)
                json.dump(new_creds, f)
        except FileNotFoundError:
            with open(self.json_path, 'w') as f:
                json.dump(new_creds, f)

    def remove_cred(self, name):
        """Remove a credential from file.

        Args:
            name (str): Nation name
        """

        with open(self.json_path, 'r+') as f:
            creds = json.load(f)
            f.seek(0)
            del creds[name]
            json.dump(creds, f)
            f.truncate()


@loader_api.cred_loader
def init_cred_loader(config):
    config = config['json_credloader']
    loader = JSONCredLoader(config)
    loader.set_path()
    return loader


@loader_api.cred_loader
def get_creds(loader):
    return loader.get_creds()


@loader_api.cred_loader
def add_cred(loader, name, x_autologin):
    loader.add_cred(name, x_autologin)


@loader_api.cred_loader
def remove_cred(loader, name):
    loader.remove_cred(name)
