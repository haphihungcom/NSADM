from unittest import mock

import nationstates
import pytest

from nsadm import api_adapter
from nsadm import exceptions


def mock_ns_response(*args, **kwargs):
    if kwargs['mode'] == 'prepare':
        return {'success': '1234abcd'}
    elif kwargs['mode'] == 'execute' and kwargs['token'] == '1234abcd':
        return {'success': 'Done'}


class TestDispatchAPI():
    def test_login_with_password_and_get_autologin(self):
        response = {'headers': {'X-Autologin': '123456'}}
        mock_nation =  mock.Mock(get_shards=mock.Mock(return_value=response))
        mock_nsapi = mock.Mock(nation=mock.Mock(return_value=mock_nation))
        dispatch_api = api_adapter.DispatchAPI(mock_nsapi)

        autologin = dispatch_api.login('my_nation', password='hunterprime123')

        assert autologin == '123456'

    def test_login_with_autologin(self):
        response = {'headers': {'XYZ': '123'}}
        mock_nation =  mock.Mock(get_shards=mock.Mock(return_value=response))
        mock_nsapi = mock.Mock(nation=mock.Mock(return_value=mock_nation))
        dispatch_api = api_adapter.DispatchAPI(mock_nsapi)

        dispatch_api.login('my_nation', autologin='123456')

        mock_nsapi.nation.assert_called_with('my_nation', autologin='123456')

    def test_login_forbidden_exception(self):
        mock_nation =  mock.Mock(get_shards=mock.Mock(side_effect=nationstates.exceptions.Forbidden))
        mock_nsapi = mock.Mock(nation=mock.Mock(return_value=mock_nation))
        dispatch_api = api_adapter.DispatchAPI(mock_nsapi)

        with pytest.raises(exceptions.DispatchAPIError):
            dispatch_api.login('my_nation', 'hunterprime123')

    def test_prepare_command_success(self):
        mock_nation = mock.Mock(command=mock.Mock(return_value={'success': '1234abcd'}))
        dispatch_api = api_adapter.DispatchAPI(mock.Mock())
        dispatch_api.owner_nation = mock_nation

        token = dispatch_api.prepare_command('remove', dispatch_id='12345')

        assert token == '1234abcd'

    def test_prepare_command_error(self):
        mock_nation = mock.Mock(command=mock.Mock(return_value={'error': 'error message'}))
        dispatch_api = api_adapter.DispatchAPI(mock.Mock())
        dispatch_api.owner_nation = mock_nation

        with pytest.raises(exceptions.DispatchAPIError):
            dispatch_api.prepare_command('remove', dispatch_id='12345')

    def test_execute_command(self):
        mock_nation = mock.Mock(command=mock.Mock(side_effect=mock_ns_response))
        dispatch_api = api_adapter.DispatchAPI(mock.Mock())
        dispatch_api.owner_nation = mock_nation

        dispatch_api.execute_command('create', title='test', text='hello world',
                                     category='1', subcategory='100')

        mock_nation.command.assert_called_with('dispatch', dispatch='create', mode='execute', dispatchid=None,
                                               title='test', text='hello world', category='1', subcategory='100',
                                               token='1234abcd')
