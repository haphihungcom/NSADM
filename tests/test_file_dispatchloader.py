import os
import json
import toml
import logging
from unittest import mock

import pytest

from nsadm.loaders import file_dispatchloader


class TestIDStore():
    @pytest.fixture
    def setup_test_file(self):
        with open('test.json', 'w') as f:
            json.dump({'Test': 1}, f)

        yield

        os.remove('test.json')

    def test_init_load_id_store_from_json_when_file_not_exist(self, setup_test_file):
        os.remove('test.json')
        ins = file_dispatchloader.IDStore('test.json')

        ins.load_from_json()

        assert os.path.isfile('test.json')
        assert ins == {}

    def test_init_load_id_store_when_file_already_exists(self, setup_test_file):
        ins = file_dispatchloader.IDStore('test.json')

        ins.load_from_json()

        assert ins == {'Test': 1}

    def test_load_id_store_from_dispatch_config(self):
        ins = file_dispatchloader.IDStore('test.json')
        ins['test1'] = 1234567

        dispatch_config = {'nation1': {'test1': {'title': 'test_title',
                                                 'ns_id': '1234567',
                                                 'category': '1',
                                                 'subcategory': '100'},
                                       'test2': {'title': 'test_title',
                                                 'category': '1',
                                                 'subcategory': '100'}},
                           'nation2': {'test3': {'ns_id': '9876543',
                                                 'title': 'test_title',
                                                 'category': '1',
                                                 'subcategory': '100'}}}

        ins.load_from_dispatch_config(dispatch_config)

        assert ins == {'test1': '1234567', 'test3': '9876543'}

    @mock.patch('json.dump')
    def test_save_when_saved_is_true(self, mock_json_dump, setup_test_file):
        ins = file_dispatchloader.IDStore('test.json')
        ins.saved = True

        ins.save()

        mock_json_dump.assert_not_called()

    @mock.patch('json.dump')
    def test_save_when_saved_is_false(self, mock_json_dump, setup_test_file):
        ins = file_dispatchloader.IDStore('test.json')
        ins.saved = False

        ins.save()

        mock_json_dump.assert_called_once()


class TestLoadDispatchConfig():
    @pytest.fixture
    def setup_test_file(self, scope='class'):
        with open('test1.toml', 'w') as f:
            toml.dump({'Test1': 'TestVal1'}, f)

        with open('test2.toml', 'w') as f:
            toml.dump({'Test2': 'TestVal2'}, f)

        yield

        os.remove('test1.toml')
        os.remove('test2.toml')

    def test_when_dispatch_config_path_is_str(self, setup_test_file):
        r = file_dispatchloader.load_dispatch_config('test1.toml')

        assert r == {'Test1': 'TestVal1'}

    def test_when_dispatch_config_path_is_list(self, setup_test_file):
        r = file_dispatchloader.load_dispatch_config(['test1.toml', 'test2.toml'])

        assert r == {'Test1': 'TestVal1', 'Test2': 'TestVal2'}


class TestDefineAction():
    def test_with_configured_action_and_id_exist(self):
        config = {'action': 'create', 'title': 'test title',
                  'category': '1', 'subcategory': '100'}

        r = file_dispatchloader.define_action('test1', config, id_dont_exist=False)

        assert r == 'create'

    def test_with_edit_action_and_id_dont_exist(self):
        config = {'action' : 'edit', 'title': 'test title',
                  'category': '1', 'subcategory': '100'}

        r = file_dispatchloader.define_action('test1', config, id_dont_exist=True)

        assert r == 'skip'

    def test_with_no_configured_action_and_id_dont_exist(self):
        config = {'title': 'test title', 'category': '1', 'subcategory': '100'}

        r = file_dispatchloader.define_action('test1', config, id_dont_exist=True)

        assert r == 'create'

    def test_with_no_configured_action_and_id_exist(self):
        config = {'title': 'test title', 'category': '1', 'subcategory': '100'}

        r = file_dispatchloader.define_action('test1', config, id_dont_exist=False)

        assert r == 'edit'

    def test_with_remove_action_and_id_exist(self):
        config = {'action': 'remove', 'title': 'test title',
                  'category': '1', 'subcategory': '100'}

        r = file_dispatchloader.define_action('test1', config, id_dont_exist=False)

        assert r == 'remove'

    def test_with_remove_action_and_id_dont_exist(self):
        config = {'action': 'remove', 'title': 'test title',
                  'category': '1', 'subcategory': '100'}

        r = file_dispatchloader.define_action('test1', config, id_dont_exist=True)

        assert r == 'skip'


class TestMergeIDStore():
    def test(self):
        dispatch_config = {'nation1': {'test1': {'title': 'test_title',
                                                 'category': '1',
                                                 'subcategory': '100'},
                                       'test2': {'action': 'remove',
                                                 'title': 'test_title',
                                                 'category': '1',
                                                 'subcategory': '100'},
                                       'test3': {'ns_id': '543210',
                                                 'title': 'test_title',
                                                 'category': '1',
                                                 'subcategory': '100'},
                                       'test4': {'title': 'test_title',
                                                 'category': '1',
                                                 'subcategory': '100'},
                                       'test5': {'action': 'remove',
                                                 'ns_id': '987654',
                                                 'title': 'test_title',
                                                 'category': '1',
                                                 'subcategory': '100'}}}
        id_store = {'test1': '123456', 'test2': '567890', 'test3': '988766'}

        r = file_dispatchloader.merge_with_id_store(dispatch_config, id_store)['nation1']

        assert r['test1']['ns_id'] == '123456' and r['test1']['action'] == 'edit'
        assert r['test2']['ns_id'] == '567890' and r['test2']['action'] == 'remove'
        assert 'test2' not in id_store
        # ID defined in config has priority over those in ID store.
        assert r['test3']['ns_id'] == '543210'
        assert r['test4']['action'] == 'create'
        assert r['test5']['ns_id'] == '987654' and r['test5']['action'] == 'remove'

    def test_with_remove_action_and_non_existing_id(self):
        dispatch_config = {'nation1': {'test1': {'title': 'test_title',
                                                 'category': '1',
                                                 'subcategory': '100'},
                                       'test2': {'action': 'remove',
                                                 'title': 'test_title',
                                                 'category': '1',
                                                 'subcategory': '100'}}}
        id_store = {'test1': '123456'}

        r = file_dispatchloader.merge_with_id_store(dispatch_config, id_store)

        assert 'test2' not in r['nation1']


class TestFileDispatchLoader():
    @pytest.fixture(scope='class')
    def setup(self):
        dispatch_config = {'nation1': {'test1': {'title': 'test_title',
                                                 'category': '1',
                                                 'subcategory': '100'},
                                       'test2': {'ns_id': '7654321',
                                                 'title': 'test_title',
                                                 'category': '1',
                                                 'subcategory': '100'}},
                           'nation2': {'test3': {'action': 'remove',
                                                 'ns_id': '5656565',
                                                 'title': 'test_title',
                                                 'category': '1',
                                                 'subcategory': '100'}}}

        with open('test.toml', 'w') as f:
            toml.dump(dispatch_config, f)

        with open('test1.txt', 'w') as f:
            f.write('Test text 1')

        with open('test2.txt', 'w') as f:
            f.write('Test text 2')

        yield

        os.remove('test.toml')
        os.remove('test1.txt')
        os.remove('test2.txt')
        os.remove('test.json')

    def test_integration_no_id_store(self, setup):
        config = {'file_dispatchloader': {'id_store_path': 'test.json',
                                          'dispatch_config_paths': 'test.toml',
                                          'file_ext': 'txt',
                                          'save_config_defined_id': True}}
        loader = file_dispatchloader.init_loader(config)

        r1 = file_dispatchloader.get_dispatch_config(loader)
        r2 = file_dispatchloader.get_dispatch_text(loader, 'test1')
        file_dispatchloader.add_dispatch_id(loader, 'test1', '1234567')

        file_dispatchloader.cleanup_loader(loader)

        assert r1['nation1']['test2']['ns_id'] == '7654321'
        assert r1['nation1']['test1']['action'] == 'create'
        assert r2 == 'Test text 1'

    def test_integration_with_existing_id_store(self, setup):
        config = {'file_dispatchloader': {'id_store_path': 'test.json',
                                          'dispatch_config_paths': 'test.toml',
                                          'file_ext': 'txt',
                                          'save_config_defined_id': True}}
        loader = file_dispatchloader.init_loader(config)

        r1 = file_dispatchloader.get_dispatch_config(loader)
        r2 = file_dispatchloader.get_dispatch_text(loader, 'test2')

        file_dispatchloader.cleanup_loader(loader)

        assert r1['nation2']['test3']['ns_id'] == '5656565' and r1['nation2']['test3']['action'] == 'remove'
        assert r1['nation1']['test1']['ns_id'] == '1234567' and r1['nation1']['test1']['action'] == 'edit'
        assert r2 == 'Test text 2'
