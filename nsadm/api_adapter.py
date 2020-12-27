"""Adapter for the pynationstates NS API wrapper
"""

import re
import logging

import nationstates

from nsadm import exceptions


class DispatchAPI():
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
        except nationstates.exceptions.Forbidden as err:
            raise exceptions.NationLoginError from err

        if password is not None:
            if 'X-Autologin' in resp_headers:
                return resp_headers['X-Autologin']
            else:
                raise exceptions.NationLoginError

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

        r = self.owner_nation.create_dispatch(title=title,
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

        try:
            self.owner_nation.edit_dispatch(dispatch_id=dispatch_id,
                                            title=title,
                                            text=text,
                                            category=category,
                                            subcategory=subcategory)
        except nationstates.exceptions.APIUsageError as err:
            if 'Unknown dispatch' in str(err):
                raise exceptions.UnknownDispatchError from err
            elif 'not the author of this dispatch' in str(err):
                raise exceptions.NotOwnerDispatchError from err

    def remove_dispatch(self, dispatch_id):
        """Delete a dispatch.

        Args:
            dispatch_id (str): Dispatch ID
        """

        r = self.owner_nation.remove_dispatch(dispatchid=dispatch_id)
        if not r:
            raise exceptions.DispatchAPIError