"""Adapter for the pynationstates NS API wrapper
"""

import re

import nationstates

from nsadm import exceptions


class GeneralAPIAdapter():
    """API adapter for pynationstates.

    Args:
        ns_api (nationstates.Nationstates): pynationstates API object
    """

    def __init__(self, ns_api):
        self.api = ns_api
        self.owner_nation = None

    def login(self, nation_name, password=None, autologin=None):
        """Get nation and test login.

        Args:
            nation_name (str): Nation name
            password (str): Nation password

        Returns:
            str: X-Autologin
        """

        if autologin is None:
            self.owner_nation = self.api.nation(nation_name, password=password)
        else:
            self.owner_nation = self.api.nation(nation_name, autologin=autologin)

        try:
            resp_headers = self.owner_nation.get_shards('ping', full_response=True)['headers']
        except nationstates.exceptions.Forbidden:
            raise exceptions.DispatchAPIError('Could not log into your nation!')

        if 'X-Autologin' in resp_headers:
            return resp_headers['X-Autologin']

    def send_command(self, action, mode, **kwargs):
        raise NotImplementedError

    def prepare_command(self, action, **kwargs):
        """Prepare dispatch command and get token for next step.

        Args:
            action (str): Action to perform on dispatch

        Raises:
            exceptions.DispatchAPIError: Raises if user error happens

        Returns:
            str: Token
        """

        resp = self.send_command(action, mode='prepare', **kwargs)

        if 'error' in resp:
            raise exceptions.DispatchAPIError(resp['error'])

        return resp['success']

    def execute_command(self, action, **kwargs):
        """Execute dispatch command.

        Args:
            action (str): Action to perform on dispatch

        Returns:
            dict: Respond's content
        """

        token = self.prepare_command(action, **kwargs)
        kwargs['token'] = token
        return self.send_command(action, mode='execute', **kwargs)


class DispatchAPI(GeneralAPIAdapter):
    def __init__(self, ns_api):
        super().__init__(ns_api)

    def send_command(self, action, mode, **kwargs):
        """Send dispatch command.

        Args:
            action (str): Action to perform on dispatch
            mode (str): Command mode

        Returns:
            dict: Respond's content
        """

        resp = self.owner_nation.command('dispatch',
                                         dispatch=action, mode=mode,
                                         dispatchid=kwargs.get('dispatchid', None),
                                         title=kwargs.get('title', None),
                                         text=kwargs.get('text', None),
                                         category=kwargs.get('category', None),
                                         subcategory=kwargs.get('subcategory', None),
                                         token=kwargs.get('token', None))
        return resp

    def create_dispatch(self, title, text, category, subcategory):
        """Create a dispatch.

        Args:
            title (str): Dispatch title
            text (str): Dispatch text
            category (str): Dispatch category number
            subcategory (str): Dispatch subcategory number
        Returns:
            str: New dispatch ID
        """

        r = self.execute_command('add', title=title,
                                 text=text,
                                 category=category,
                                 subcategory=subcategory)

        new_dispatch_id = re.search('id=(\\d+)', r['success']).group(1)
        return new_dispatch_id

    def edit_dispatch(self, dispatch_id, title, text, category, subcategory):
        """Edit a dispatch.

        Args:
            dispatch_id (str): Dispatch ID
            title (str): Dispatch title
            text (str): Dispatch text
            category (str): Dispatch category number
            subcategory (str): Dispatch subcategory number
        """

        self.execute_command('edit', dispatch_id=dispatch_id,
                             title=title,
                             text=text,
                             category=category,
                             subcategory=subcategory)

    def remove_dispatch(self, dispatch_id):
        """Delete a dispatch.

        Args:
            dispatch_id (str): Dispatch ID
        """

        self.execute_command('remove', dispatchid=dispatch_id)
