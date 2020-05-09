import logging

import toml

from nsadm import exceptions
from nsadm import renderer
from nsadm import uploader
from nsadm import utils


logger = logging.getLogger(__name__)


class NSADM():
    def __init__(self, ns_site, config, data):
        self.config = config
        general_conf = config.get('general', {})
        self.ns_site = ns_site

        self.dispatch_config = utils.load_dispatch_config(general_conf.get('dispatch_config_path', None))
        if not self.dispatch_config:
            raise exceptions.NSADMError('No dispatch was configured')
        self.blacklist = general_conf.get('blacklist', [])

        dry_run_conf = config.get('dry_run', {})
        self.dry_run_dispatches = dry_run_conf.get('dispatches', None)

        self.id_store = utils.IDStore(general_conf.get('id_store_path', None))

        renderer_conf = config.get('renderer', {})
        self.renderer = renderer.Renderer(renderer_conf)

        self.uploader = uploader.DispatchUploader(self.renderer, ns_site,
                                                  self.id_store, self.dispatch_config)

        self.create_all_dispatches()
        self.id_store.save()

        self.config = config
        self.data = data

    def update_ctx(self):
        dispatch_info = utils.get_dispatch_info(self.dispatch_config,
                                                self.id_store)
        self.renderer.update_ctx(self.data, self.config,
                                 self.config, dispatch_info)

    def run(self):
        self.update_ctx()
        self.update_all_dispatches()

    def prepare(self):
        self.id_store.load_from_json()
        self.id_store.load_from_dispatch_config(self.dispatch_config)

    def dry_run(self):
        self.update_ctx()

        if not self.dry_run_dispatches:
            self.update_all_dispatches()
        else:
            self.update_dispatches(self.dry_run_dispatches)

    def get_allowed_dispatches(self):
        """Get non-blacklisted dispatches.

        Returns:
            list: Dispatch file names.
        """

        return [dispatch for dispatch in self.dispatch_config.keys()
                if dispatch not in self.blacklist]

    def update_all_dispatches(self):
        """Update all dispatches except blacklisted ones.
        """

        dispatches = self.get_allowed_dispatches()
        self.update_dispatches(dispatches)

    def update_dispatches(self, dispatches):
        """Update dispatches

        Args:
            dispatches (list): Dispatch file names.
        """

        for name in dispatches:
            self.uploader.update_dispatch(name)

    def create_all_dispatches(self):
        """Create all dispatches except blacklisted ones.
        """

        dispatches = self.get_allowed_dispatches()
        self.create_dispatches(dispatches)

    def create_dispatches(self, dispatches):
        """Create dispatches and add their ID.

        Args:
            dispatches (list): Dispatch file names.
        """

        for name in dispatches:
            if name not in self.id_store:
                html = self.uploader.create_dispatch(name)
                self.id_store.add_id_from_html(name, html)
