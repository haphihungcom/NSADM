import os
import json
import toml
import logging
from unittest import mock

import pytest

from nsadm import utils


class TestGetDispatchInfo():
    def test_get_dispatch_info(self):
        dispatch_config = {'nation1': {'dispatch1': {'title': 'Test Title 1',
                                                     'ns_id': '1234567',
                                                     'category': '1',
                                                     'subcategory': '100'},
                                      'dispatch2': {'title': 'Test Title 2',
                                                     'ns_id': '7654321',
                                                     'category': '2',
                                                     'subcategory': '120'}},
                           'nation2': {'dispatch1': {'title': 'Test Title 1',
                                                    'ns_id': '1234567',
                                                    'category': '1',
                                                    'subcategory': '100'}}}

        r = utils.get_dispatch_info(dispatch_config)
        assert r == {'dispatch1': {'title': 'Test Title 1',
                                   'ns_id': '1234567',
                                   'category': '1',
                                   'subcategory': '100',
                                   'owner_nation': 'nation1'},
                    'dispatch2': {'title': 'Test Title 2',
                                   'ns_id': '7654321',
                                   'category': '2',
                                   'subcategory': '120',
                                   'owner_nation': 'nation1'},
                    'dispatch1': {'title': 'Test Title 1',
                                   'ns_id': '1234567',
                                   'category': '1',
                                   'subcategory': '100',
                                   'owner_nation': 'nation2'}}