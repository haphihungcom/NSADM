"""Adapter for the pynationstates NS API wrapper
"""

import nationstates

from nsadm import exceptions


class GeneralAPIAdapter():
    """API adapter for pynationstates. All results returned as set.

    Args:
        ns_api (nationstates.Nationstates): pynationstates API object
    """

    def __init__(self, ns_api):
        self.api = ns_api
        self.owner_nation = None

    def login(self, owner_nation, password):
        """Send ping to the nation and return X-Pin.

        Args:
            owner_nation (str): Owner nation's name
            password (str): Owner nation's password
        """

        self.owner_nation = self.api.nation(owner_nation, password)

        try:
            self.owner_nation.get_shards('ping')
        except nationstates.exceptions.Forbidden:
            raise exceptions.DispatchAPIError('Could not log into your nation!')

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
        super(DispatchAPI, self).__init__(ns_api)

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
                                         dispatchid=kwargs.get('dispatch_id', None),
                                         title=kwargs.get('title', None),
                                         text=kwargs.get('text', None),
                                         category=kwargs.get('category', None),
                                         subcategory=kwargs.get('subcategory', None))
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

        r = self.execute_command('create', title=title,
                                 text=text,
                                 category=category,
                                 subcategory=subcategory)

        return r['success']

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

    def delete_dispatch(self, dispatch_id):
        """Delete a dispatch.

        Args:
            dispatch_id (str): Dispatch ID
        """

        self.execute_command('remove', dispatchid=dispatch_id)
