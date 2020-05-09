import os
import logging
import json
from unittest import mock

import pytest
import toml

from nsadm import uploader


class TestDispatchUploader():
    def test_post_dispatch_with_id(self):
        mock_renderer = mock.Mock()
        mock_ns_site = mock.Mock(execute=mock.Mock(return_value='test'))
        dispatch_config = {'title': 'Test', 'category': 123,
                           'sub_category': 456}
        ins = uploader.DispatchUploader(mock_renderer, mock_ns_site,
                                                {}, {})

        r = ins.post_dispatch(dispatch_config, 'abc', 1234567)

        mock_ns_site.execute.assert_called_with('lodge_dispatch',
                                               {'category': '123',
                                                'subcategory-123': '456',
                                                'dname': 'Test',
                                                'message': b'abc',
                                                'submitbutton': '1',
                                                'edit': '1234567',})
        assert r == 'test'

    def test_post_dispatch_with_no_id(self):
        mock_ns_site = mock.Mock(execute=mock.Mock(return_value='test'))
        dispatch_config = {'title': 'Test', 'category': 123,
                           'sub_category': 456}
        ins = uploader.DispatchUploader(mock.Mock(), mock_ns_site, {}, {})

        r = ins.post_dispatch(dispatch_config, 'abc')

        mock_ns_site.execute.assert_called_with('lodge_dispatch',
                                               {'category': '123',
                                                'subcategory-123': '456',
                                                'dname': 'Test',
                                                'message': b'abc',
                                                'submitbutton': '1'})
        assert r == 'test'

    def test_update_dispatch(self):
        mock_renderer = mock.Mock(render=mock.Mock(return_value='abcd'))
        id_store = {'test1': 1234567, 'test2': 8901234}
        dispatch_config = {'test1': {'title': 'Test', 'category': 123,
                                    'sub_category': 456},
                           'test2': {'title': 'Test', 'category': 123,
                                     'sub_category': 456}}
        ins = uploader.DispatchUploader(mock_renderer, mock.Mock(),
                                                id_store, dispatch_config)
        ins.post_dispatch = mock.Mock()

        ins.update_dispatch('test1')

        ins.post_dispatch.assert_called_with(dispatch_config['test1'],
                                             'abcd', 1234567)

    def test_create_dispatch(self):
        dispatch_config = {'test1': {'title': 'Test', 'category': 123,
                                    'sub_category': 456},
                           'test2': {'title': 'Test', 'category': 123,
                                     'sub_category': 456}}
        ins = uploader.DispatchUploader(mock.Mock(), mock.Mock(),
                                                {}, dispatch_config)
        ins.post_dispatch = mock.Mock()

        ins.create_dispatch('test1')

        ins.post_dispatch.assert_called_with(dispatch_config['test1'], '[reserved]')
