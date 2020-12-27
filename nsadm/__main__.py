import argparse
import sys
import logging

import toml
import nationstates

from nsadm import info
from nsadm import exceptions
from nsadm import api_adapter
from nsadm import loader
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
                                                  template_config)

        self.cred_loader = loader.CredLoader(plugin_options['cred_loader'], loader_config)
        self.creds = utils.CredManager(self.cred_loader, dispatch_api)

        self.updater = updater.DispatchUpdater(dispatch_api, self.creds, self.renderer, self.dispatch_loader)

    def load(self):
        self.dispatch_loader.load_loader()
        self.dispatch_config = self.dispatch_loader.get_dispatch_config()

        self.creds.load_creds()

        self.var_loader.load_loader()
        self.renderer.load(self.dispatch_config)

    def soft_load(self):
        self.cred_loader.load_loader()

    def update_dispatches_all_nations(self, dispatches=None):
        for owner_nation, dispatch_config in self.dispatch_config.items():
            try:
                self.updater.login_owner_nation(owner_nation, dispatch_config)
                logger.info('Logged in nation "%s".', owner_nation)
            except exceptions.NationLoginError:
                logger.error('Could not log into nation "%s".', owner_nation)
                continue

            for name in dispatch_config.keys():
                if dispatches is None or name in dispatches:
                    self.updater.update_dispatch(name)

    def add_nation_cred(self, nation_name, password):
        self.creds[nation_name] = password

    def remove_nation_cred(self, nation_name):
        del self.creds[nation_name]

    def close(self):
        self.dispatch_loader.cleanup_loader()


def cli():
    parser = argparse.ArgumentParser(description=info.DESCRIPTION)
    subparsers = parser.add_subparsers(help='Sub-command help')

    cred_command = subparsers.add_parser('cred', help='Nation login credential management')
    cred_command.add_argument('--add', nargs=2, metavar=('NAME', 'PASSWORD'),
                              help='Add new login credential')
    cred_command.add_argument('--remove', nargs=1, metavar='NAME',
                              help='Remove login credential')

    parser.add_argument('dispatches', nargs='*', default=None, metavar='N',
                        help='Names of dispatches to update (Leave blank means all)')

    return parser.parse_args()


def run(app, inputs):
    if hasattr(inputs, 'add'):
        app.add_nation_cred(inputs.add[0], inputs.add[1])
    elif hasattr(inputs, 'remove'):
        app.remove_nation_cred(inputs.remove[0])
    else:
        app.load()
        app.update_dispatches(inputs.dispatches)


def main():
    inputs = cli()

    try:
        config = utils.get_config()
        logger.info('Loaded general config.')
    except exceptions.ConfigError as err:
        print(err)
        return

    try:
        app = NSADM(config)
        app.soft_load()
        run(app, inputs)
        app.close()
    except Exception as err:
        logger.critical(err, exc_info=True)


if __name__ == "__main__":
    main()


