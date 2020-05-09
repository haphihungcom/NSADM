import nationstates

from nsadm import exceptions


class DispatchAPI():
    """NationSates API adapter. All results returned as set.

    Args:
        ns_api (nationstates.Nationstates): NationStates API object
        descriptive_category (bool): Use descriptive category and subcategory name
    """

    def __init__(self, ns_api, descriptive_category=True):
        self.api = ns_api
        self.owner_nation = None
        self.descriptive_category = descriptive_category

    def login(self, owner_nation, password):
        """Send ping to the nation and return X-Pin.

        Args:
            owner_nation (str): Owner nation's name
            password (str): Owner nation's password
        """

        self.owner_nation = self.api.nation(owner_nation, password)

        try:
            resp = self.owner_nation.get_shards('ping', full_response=True)
        except nationstates.exceptions.Forbidden:
            raise exceptions.DispatchAPIError('Could not log into your nation!')

    def send_command(self, action, mode, **kwargs):
        """Send dispatch command.

        Args:
            action (str): Action to perform on dispatch
            mode (str): Command mode

        Returns:
            dict: Respond content
        """

        resp = self.owner_nation.command('dispatch',
                                         dispatch=action, mode=mode,
                                         dispatchid=kwargs.get('dispatch_id', None),
                                         title=kwargs.get('title', None),
                                         text=kwargs.get('text', None),
                                         category=kwargs.get('category', None),
                                         subcategory=kwargs.get('subcategory', None))
        return resp

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
        """

        token = self.prepare_command(action, **kwargs)
        kwargs['token'] = token
        self.send_command(action, mode='execute', **kwargs)

    def create_dispatch(self, title, text, category, subcategory):
        """Create a dispatch.

        Args:
            title (str): Dispatch title
            text (str): Dispatch text
            category (str): Dispatch category (accept descriptive text or number)
            subcategory (str): DIspatch subcategory (accept descriptive text or number)
        """

        self.execute_command('create', title=title,
                             text=text,
                             category=category,
                             subcategory=subcategory)

    def edit_dispatch(self, dispatch_id, title, text, category, subcategory):
        """Edit a dispatch.

        Args:
            dispatch_id (str): Dispatch ID
            title (str): Dispatch title
            text (str): Dispatch text
            category (str): Dispatch category number
            subcategory (str): DIspatch subcategory number
        """

        self.execute_command('edit', dispatch_id=dispatch_id,
                             title=title,
                             text=text,
                             category=category,
                             subcategory=subcategory)

    def delete_dispatch(self, dispatch_id):
        """Delete a dispatch.

        Args:
            dispatch_id ([type]): [description]
        """

        self.execute_command('remove', dispatchid=dispatch_id)
