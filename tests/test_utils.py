import os
import shutil
import json
import toml
import logging
from unittest import mock

import pytest

from nsadm import info
from nsadm import exceptions
from nsadm import utils


class TestCredManager():
    def test_load_creds(self):
        mock_creds = {'nation1': '123456', 'nation2': '567890'}
        mock_cred_loader = mock.Mock(get_creds=mock.Mock(return_value=mock_creds))
        creds = utils.CredManager(mock_cred_loader, mock.Mock())

        creds.load_creds()

        assert creds['nation1'] == '123456'

    def test_add_cred(self):
        mock_cred_loader = mock.Mock(add_cred=mock.Mock())
        mock_dispatch_api = mock.Mock(login=mock.Mock(return_value='123456'))
        creds = utils.CredManager(mock_cred_loader, mock_dispatch_api)

        creds['nation1'] = 'hunterprime'

        mock_cred_loader.add_cred.assert_called_with('nation1', '123456')
        mock_dispatch_api.login('nation1', password='123456')

    def test_remove_cred(self):
        mock_cred_loader = mock.Mock(remove_cred=mock.Mock())
        creds = utils.CredManager(mock_cred_loader, mock.Mock())

        del creds['nation1']

        mock_cred_loader.remove_cred.assert_called_with('nation1')


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
                           'nation2': {'dispatch3': {'title': 'Test Title 1',
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
                    'dispatch3': {'title': 'Test Title 1',
                                   'ns_id': '1234567',
                                   'category': '1',
                                   'subcategory': '100',
                                   'owner_nation': 'nation2'}}


class TestGetConfig():
    @mock.patch('os.getenv')
    def test_config_with_env(self, mock_getenv, toml_files):
        toml_files({'test_config.toml': {'testkey': 'testval'}})
        mock_getenv.return_value = 'test_config.toml'

        r = utils.get_config()

        assert r == {'testkey': 'testval'}

    @mock.patch('os.getenv')
    def test_config_with_env_and_non_existing_config_file(self, mock_getenv):
        mock_getenv.return_value = 'test_config.toml'

        with pytest.raises(exceptions.ConfigError):
            utils.get_config()

    @mock.patch('appdirs.user_config_dir')
    def test_config_with_no_env_and_existing_config_file(self, mock_appdir, toml_files):
        toml_files({info.CONFIG_NAME: {'testkey': 'testval'}})
        mock_appdir.return_value = ''

        r = utils.get_config()

        assert r == {'testkey': 'testval'}

    @mock.patch('appdirs.user_config_dir')
    def test_config_with_no_env_and_non_existing_config_file(self, mock_appdir):
        mock_appdir.return_value = 'test_folder'

        with pytest.raises(exceptions.ConfigError):
            utils.get_config()

        config_path = os.path.join('test_folder', info.CONFIG_NAME)
        assert os.path.isfile(config_path)

        shutil.rmtree('test_folder')
