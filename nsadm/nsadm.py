import argparse
import logging

import toml
import nationstates

from nsadm import api_adapter
from nsadm import exceptions
from nsadm import loader
from nsadm import info
from nsadm import renderer
from nsadm import updater
from nsadm import utils


logger = logging.getLogger(__name__)


class NSADM():
    def __init__(self, config):
        ns_api = nationstates.Nationstates(user_agent=config['general']['user_agent'])
        dispatch_api = api_adapter.DispatchAPI(ns_api)

        plugin_options = config['plugins']
        loader_config = config['loader_config']

        self.dispatch_loader = loader.DispatchLoader(plugin_options['dispatch_loader'], loader_config)
        self.var_loader = loader.VarLoader(plugin_options['var_loader'], loader_config)

        self.dispatch_config = None

        bb_config = config['bbcode']
        template_config= config['template_renderer']
        self.renderer = renderer.DispatchRenderer(self.dispatch_loader, self.var_loader, bb_config,
                                                  template_config, self.dispatch_config)

        self.cred_loader = loader.CredLoader(plugin_options['cred_loader'], loader_config)
        self.creds = utils.CredManager(self.cred_loader, dispatch_api)

        self.updater = updater.DispatchUpdater(dispatch_api, self.creds, self.renderer, self.dispatch_loader)

    def load(self):
        self.dispatch_loader.load_loader()
        self.dispatch_config = self.dispatch_loader.get_dispatch_config()

        self.cred_loader.load_loader()
        self.creds.load_creds()

        self.var_loader.load_loader()
        self.renderer.load()

    def update_dispatches(self, dispatches=None):
        pass

    def add_nation_cred(self, nation_name, password):
        self.creds[nation_name] = password

    def remove_nation_cred(self, nation_name):
        del self.creds[nation_name]


def main():
    parser = argparse.ArgumentParser(description=info.DESCRIPTION)
    parser.add_argument('dispatches', metavar='N', nargs='+', default=None,
                        help='Update specified dispaches (All if none is specified)')
    parser.add_argument('--add-nation', help="Add a nation's login credential")
    parser.add_argument('--remove-nation', help="Remove a nation's login credential")

