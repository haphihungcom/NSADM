"""Loads and runs plugins
"""

import collections
import os

import pluggy

from nsadm import info
from nsadm import loader_api
from nsadm import utils


class Loader():
    """Handling loader plugins.

    Args:
        proj_name (str): Pluggy project name for this plugin type
        name (str|list): Name(s) of loader file(s)
        loader_config (dict): Loaders' configuration
    """

    def __init__(self, proj_name, name, loader_config):
        self.manager = pluggy.PluginManager(proj_name)
        self.manager.add_hookspecs(loader_api)
        self.loader_config = loader_config
        self.name = name

    def load_a_loader(self, name):
        """Load a loader's module and register it.

        Args:
            name (str): Name of loader file
        """

        path = os.path.join(info.LOADER_DIR_PATH, utils.add_extension(name))
        module = utils.load_module(path, name)
        self.manager.register(module)

    def load_loader(self):
        """Load loader(s).
        """

        if isinstance(self.name, list):
            for name in self.name:
                self.load_a_loader(name)
        else:
            self.load_a_loader(self.name)


# pylint: disable=maybe-no-member
class DispatchLoader(Loader):
    """Load dispatch information and content.

    Args:
        name (str): Name of loader file
    """

    def __init__(self, name, loader_config):
        super(DispatchLoader, self).__init__(info.DISPATCH_LOADER_PROJ,
                                             name, loader_config)
        # Loader instance to reuse the same database connection
        # across hook calls.
        self._loader = None

    def load_loader(self):
        """Load a loader and return its instance for
        reusing file handlers/database connections.
        """

        super(DispatchLoader, self).load_loader()
        self._loader = self.manager.hook.init_loader(config=self.loader_config)

    def get_dispatch_config(self):
        return self.manager.hook.get_dispatch_config(loader=self._loader)

    def get_dispatch_text(self, name):
        return self.manager.hook.get_dispatch_text(loader=self._loader, name=name)

    def add_dispatch_id(self, name, id):
        return self.manager.hook.add_dispatch_id(loader=self._loader, name=name, dispatch_id=id)

    def cleanup_loader(self):
        self.manager.hook.cleanup_loader(loader=self._loader)


class VarLoader(Loader):
    """Load variables from multiple loaders.

    Args:
        names (list): Names of loader files
    """

    def __init__(self, names, loader_config):
        super(VarLoader, self).__init__(info.VAR_LOADER_PROJ,
                                        names, loader_config)

    def get_all_vars(self):
        vars_list = self.manager.hook.get_vars(config=self.loader_config)
        merged_vars_dict = dict(collections.ChainMap(*vars_list))
        return merged_vars_dict


class CredLoader(Loader):
    """Load nation login credentials.

    Args:
        name (str): Name of loader file
    """

    def __init__(self, name, loader_config):
        super(CredLoader, self).__init__(info.CRED_LOADER_PROJ,
                                         name, loader_config)

    def get_creds(self):
        return self.manager.hook.get_creds(config=self.loader_config)

    def add_cred(self, name, x_autologin):
        return self.manager.hook.add_cred(config=self.loader_config,
                                             name=name, x_autologin=x_autologin)

    def remove_cred(self, name):
        return self.manager.hook.remove_cred(config=self.loader_config, name=name)
