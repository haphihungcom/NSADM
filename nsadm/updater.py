"""Create dispatches based on templates and upload them.
"""


import logging
import time
import codecs

import toml

from nsadm import info
from nsadm import exceptions
from nsadm import renderer
from nsadm import utils


logger = logging.getLogger(__name__)

RESERVED_PLACEHOLDER = "[reserved]"


def get_category_number(category, subcategory):
    """Get category and subcategory number if they are descriptive name.

    Args:
        category (str): Category
        subcategory (str): Subcategory

    Raises:
        exceptions.DispatchUpdatingError: Raises if cannot find (sub)category number from name

    Returns:
        str, str: Category and subcategory number
    """

    if category.isalpha() and subcategory.isalpha():
        try:
            category_info = info.CATEGORIES[category]
            category_num = category_info['num']
            subcategory_num = category_info['subcategories'][subcategory]
        except KeyError:
            raise exceptions.DispatchUpdatingError('Non-existent category or subcategory name')
    else:
        category_num = category
        subcategory_num = subcategory

    return category_num, subcategory_num


class DispatchUpdater():
    """Update a dispatch.

    Args:
        dispatch_api (nsadm.api_adapter.DispatchAPI): Dispatch API adapter
        creds (dict): Nation login credentials
        renderer (nsadm.renderer.Renderer): Renderer
        dispatch_loader (nsadm.loader.DispatchLoader): Dispatch loader
    """

    def __init__(self, dispatch_api, creds, renderer, dispatch_loader):
        self.dispatch_api = dispatch_api
        self.renderer = renderer
        self.dispatch_loader = dispatch_loader
        self.dispatch_config = None
        self.creds = creds

    def login_owner_nation(self, owner_nation, dispatch_config):
        """Log into dispatch owner nation and set its dispatches' info.

        Args:
            owner_nation (str): Nation name
            dispatch_config (dict): Nation's dispatches' info
        """

        self.dispatch_api.login(owner_nation, self.creds[owner_nation])
        self.dispatch_config = dispatch_config

    def update_dispatch(self, name):
        """Update a dispatch.

        Args:
            name (str): Dispatch name
        """

        this_dispatch_config = self.dispatch_config[name]
        action = this_dispatch_config.pop('action')

        if action == 'remove':
            dispatch_id = this_dispatch_config['ns_id']
            self.delete_dispatch(dispatch_id)
        else:
            self.create_or_edit_dispatch(name, action, this_dispatch_config)

    def get_dispatch_text(self, name):
        """Get rendered text for a dispatch.

        Args:
            name (str): Dispatch name

        Returns:
            str: Rendered text
        """

        return self.renderer.render(name)

    def create_or_edit_dispatch(self, name, action, this_dispatch_config):
        """Create or edit a dispatch based on action.

        Args:
            name (str): Dispatch name
            action (str): Action to perform
            this_dispatch_config (dict): This dispatch's info

        Raises:
            exceptions.DispatchUpdatingError: Raises when action is invalid
        """

        category = this_dispatch_config['category']
        subcategory = this_dispatch_config['subcategory']
        category_num, subcategory_num = get_category_number(category, subcategory)
        title = this_dispatch_config['title']
        text = self.get_dispatch_text(name)

        params = {'title': title,
                  'text': text,
                  'category': category_num,
                  'subcategory': subcategory_num}

        if action == 'create':
            self.create_dispatch(name, params)
        elif action == 'edit':
            dispatch_id = this_dispatch_config['ns_id']
            self.edit_dispatch(dispatch_id, params)
        else:
            raise exceptions.DispatchUpdatingError

    def create_dispatch(self, name, params):
        """Create a dispatch.

        Args:
            name (str): Dispatch name
            params (dict): Dispatch parameters
        """

        new_dispatch_id = self.dispatch_api.create_dispatch(title=params['title'],
                                                            text=params['text'],
                                                            category=params['category'],
                                                            subcategory=params['subcategory'])
        self.dispatch_loader.add_dispatch_id(name, new_dispatch_id)

    def edit_dispatch(self, dispatch_id, params):
        """Edit a dispatch.

        Args:
            dispatch_id (str): Dispatch ID
            params (dict): Dispatch parameters
        """

        self.dispatch_api.edit_dispatch(dispatch_id=dispatch_id,
                                        title=params['title'],
                                        text=params['text'],
                                        category=params['category'],
                                        subcategory=params['subcategory'])

    def delete_dispatch(self, dispatch_id):
        """Delete a dispatch.

        Args:
            dispatch_id (str): Dispatch ID
        """
        self.dispatch_api.delete_dispatch(dispatch_id)

