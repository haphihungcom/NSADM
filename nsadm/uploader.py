"""Create dispatches based on templates and upload them.
"""


import logging
import time
import codecs

import toml

from nsadm import exceptions
from nsadm import renderer
from nsadm import utils


logger = logging.getLogger(__name__)

RESERVED_PLACEHOLDER = "[reserved]"


"""if 'category' in kwargs and 'subcategory' in kwargs:
            try:
                category = CATEGORIES[kwargs['category']]
                kwargs['category'] = category['num']
                kwargs['subcategory'] = category['subcategories'][kwargs['subcategory']]
            except KeyError:
                if self.descriptive_category:
                    raise exceptions.DispatchAPIError('Non-existent category or subcategory name')"""


class DispatchUpdater():
    def __init__(self, api, loader):
        self.api = api
        self.loader = loader
        self.dispatch_params = self.loader.get_dispatch_params()

    def add_dispatch_id(self, resp):
        self.api.create_dispatch()
        self.loader.add_dispatch_id()

    def execute_dispatches(self, dispatches):
        for dispatch in dispatches:
            action = dispatch['action']
            if action == 'create':
                resp = self.api.create_dispatch()
                self.add_dispatch_id(resp)
            elif action == 'delete':
                self.api.edit_dispatch()
            elif action == 'update':
                self.api.delete_dispatch()

    def update_dispatches_by_nation(self, names=None):
        for nation in self.dispatch_info.keys():
            self.api.login()
            dispatches = self.dispatch_info[nation]
            self.update_dispatches(dispatches)

    def update_dispatches(self):
        pass
