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


class DispatchUploader():
    """Dispatch Uploader"""

    def __init__(self, renderer, ns_site, id_store, dispatch_config):
        self.ns_site = ns_site
        self.renderer = renderer
        self.dispatch_config = dispatch_config
        self.id_store = id_store

    def create_dispatch(self, name):
        """Create a new dispatch.

        Args:
            name (str): Dispatch file name.

        Returns:
            str: HTML response.
        """

        html = self.post_dispatch(self.dispatch_config[name], RESERVED_PLACEHOLDER)
        logger.info('Created new dispatch "%s"', name)

        return html

    def update_dispatch(self, name):
        """Update dispatch.

        Args:
            name (str): Dispatch file name.
            config (dict): Dispatch configuration.
        """

        text = self.renderer.render(name)
        dispatch_id = self.id_store[name]
        dispatch_config = self.dispatch_config[name]

        self.post_dispatch(dispatch_config, text, dispatch_id)
        logger.info('Updated dispatch "%s"', name)

    def post_dispatch(self, config, text, edit_id=None):
        """Post dispatch.

        Args:
            config (dict): Dispatch configuration.
            text (str): Text to post.
            edit_id (int|None): Dispatch ID. Defaults to None.
        """

        subcategory_name = "subcategory-{}".format(config['category'])
        params = {'category': str(config['category']),
                  subcategory_name: str(config['sub_category']),
                  'dname': config['title'],
                  'message': text.encode('windows-1252'),
                  'submitbutton': '1'}

        if edit_id:
            params['edit'] = str(edit_id)

        #time.sleep(6)
        return self.ns_site.execute('lodge_dispatch', params)
