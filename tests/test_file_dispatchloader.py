import os
import json
import toml
import logging
from unittest import mock

import pytest

from nsadm.loaders import file_dispatchloader


# TODO: Refactor
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

    def test_load_id_store_from_dispatch_config_with_no_remove_action_and_no_override(self):
        ins = file_dispatchloader.IDStore('test.json')
        ins['test1'] = '1234567'

        dispatch_config = {'nation1': {'test1': {'title': 'test_title',
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

    def test_load_id_store_from_dispatch_config_with_no_remove_action_and_with_override(self):
        """Previously loaded id must be overridden with
        the dispatch config version when this method is called.
        """

        ins = file_dispatchloader.IDStore('test.json')
        ins['test1'] = '1234567'

        dispatch_config = {'nation1': {'test1': {'title': 'test_title',
                                                 'ns_id': '456789',
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

        assert ins == {'test1': '456789', 'test3': '9876543'}

    def test_load_id_store_from_dispatch_config_with_remove_action(self):
        """Id of dispatches with remove action should not be loaded.
        """

        ins = file_dispatchloader.IDStore('test.json')
        ins['test1'] = '1234567'

        dispatch_config = {'nation1': {'test1': {'title': 'test_title',
                                                 'category': '1',
                                                 'subcategory': '100'},
                                       'test2': {'title': 'test_title',
                                                 'category': '1',
                                                 'subcategory': '100'}},
                           'nation2': {'test3': {'action': 'remove',
                                                 'ns_id': '9876543',
                                                 'title': 'test_title',
                                                 'category': '1',
                                                 'subcategory': '100'}}}

        ins.load_from_dispatch_config(dispatch_config)

        assert ins == {'test1': '1234567'}

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
    def test_with_create_edit_actions(self):
        dispatch_config = {'nation1': {'test1': {'title': 'test_title',
                                                 'category': '1',
                                                 'subcategory': '100'},
                                       'test2': {'ns_id': '543210',
                                                 'title': 'test_title',
                                                 'category': '1',
                                                 'subcategory': '100'}},
                           'nation2': {'test3': {'ns_id': '667889',
                                                 'title': 'test_title',
                                                 'category': '1',
                                                 'subcategory': '100'},
                                       'test4': {'title': 'test_title',
                                                 'category': '1',
                                                 'subcategory': '100'}}}
        id_store = {'test1': '123456', 'test3': '988766'}

        r = file_dispatchloader.merge_with_id_store(dispatch_config, id_store)

        r1 = r['nation1']
        r2 = r['nation2']
        assert r1['test1']['ns_id'] == '123456' and r1['test1']['action'] == 'edit'
        assert r1['test2']['ns_id'] == '543210' and r1['test2']['action'] == 'edit'
        # User-configured id takes precedent over the version in id store
        assert r2['test3']['ns_id'] == '667889'
        assert r2['test4']['action'] == 'create'

    def test_with_one_remove_action_and_id_in_store(self):
        dispatch_config = {'nation1': {'test1': {'action': 'remove',
                                                 'title': 'test_title',
                                                 'category': '1',
                                                 'subcategory': '100'},
                                       'test2': {'ns_id': '543210',
                                                 'title': 'test_title',
                                                 'category': '1',
                                                 'subcategory': '100'}},
                           'nation2': {'test3': {'title': 'test_title',
                                                 'category': '1',
                                                 'subcategory': '100'}}}
        id_store = {'test1': '123456', 'test3': '988766'}

        file_dispatchloader.merge_with_id_store(dispatch_config, id_store)

        assert 'test1' not in id_store

    def test_with_one_remove_action_and_user_defined_id(self):
        dispatch_config = {'nation1': {'test1': {'action': 'remove',
                                                 'ns_id': '123456',
                                                 'title': 'test_title',
                                                 'category': '1',
                                                 'subcategory': '100'},
                                       'test2': {'ns_id': '543210',
                                                 'title': 'test_title',
                                                 'category': '1',
                                                 'subcategory': '100'}},
                           'nation2': {'test3': {'title': 'test_title',
                                                 'category': '1',
                                                 'subcategory': '100'}}}
        id_store = {'test3': '988766'}

        r = file_dispatchloader.merge_with_id_store(dispatch_config, id_store)

        assert r['nation1']['test1']['ns_id'] == '123456'

    def test_with_one_remove_action_and_non_existing_id(self):
        dispatch_config = {'nation1': {'test1': {'action': 'remove',
                                                 'title': 'test_title',
                                                 'category': '1',
                                                 'subcategory': '100'},
                                       'test2': {'ns_id': '543210',
                                                 'title': 'test_title',
                                                 'category': '1',
                                                 'subcategory': '100'}},
                           'nation2': {'test3': {'title': 'test_title',
                                                 'category': '1',
                                                 'subcategory': '100'}}}
        id_store = {'test3': '123456'}

        r = file_dispatchloader.merge_with_id_store(dispatch_config, id_store)

        assert 'test1' not in r

    def test_with_all_remove_action_and_non_existing_id_in_one_nation(self):
        dispatch_config = {'nation1': {'test1': {'action': 'remove',
                                                 'title': 'test_title',
                                                 'category': '1',
                                                 'subcategory': '100'},
                                       'test2': {'action': 'remove',
                                                 'title': 'test_title',
                                                 'category': '1',
                                                 'subcategory': '100'}},
                           'nation2': {'test3': {'title': 'test_title',
                                                 'category': '1',
                                                 'subcategory': '100'}}}
        id_store = {'test3': '123456'}

        r = file_dispatchloader.merge_with_id_store(dispatch_config, id_store)

        assert 'nation1' not in r


class TestFileDispatchLoader():
    @pytest.fixture
    def setup_text_files(self, text_files):
        text_files({'test1.txt': 'Test text 1', 'test2.txt': 'Test text 2',
                    'text3.txt': 'Test text 3'})

    def test_integration_with_non_existing_id_store_with_save_config_defined_id_true(self,
                                                                                     toml_files,
                                                                                     setup_text_files):
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
        toml_files({'test_config.toml': dispatch_config})
        config = {'file_dispatchloader': {'id_store_path': 'id_store_test.json',
                                          'dispatch_config_paths': 'test_config.toml',
                                          'file_ext': 'txt',
                                          'save_config_defined_id': True}}
        loader = file_dispatchloader.init_loader(config)

        r_config = file_dispatchloader.get_dispatch_config(loader)
        r_text = file_dispatchloader.get_dispatch_text(loader, 'test1')
        file_dispatchloader.add_dispatch_id(loader, 'test1', '1234567')

        file_dispatchloader.cleanup_loader(loader)

        with open('id_store_test.json') as f:
            r_id_store = json.load(f)

        os.remove('id_store_test.json')

        assert r_config['nation1']['test2']['ns_id'] == '7654321'
        assert r_config['nation1']['test1']['action'] == 'create'
        assert r_text == 'Test text 1'
        assert r_id_store['test1'] == '1234567'
        assert r_id_store['test2'] == '7654321'
        assert 'test3' not in r_id_store

    def test_integration_with_existing_id_store_with_save_config_defined_id_true(self,
                                                                                 toml_files,
                                                                                 json_files,
                                                                                 setup_text_files):
        dispatch_config = {'nation1': {'test1': {'title': 'test_title',
                                                 'category': '1',
                                                 'subcategory': '100'},
                                       'test2': {'ns_id': '7654321',
                                                 'title': 'test_title',
                                                 'category': '1',
                                                 'subcategory': '100'},
                                       'test3': {'title': 'test_title',
                                                 'category': '1',
                                                 'subcategory': '100'}},
                           'nation2': {'test4': {'action': 'remove',
                                                 'title': 'test_title',
                                                 'category': '1',
                                                 'subcategory': '100'}}}
        toml_files({'test_config.toml': dispatch_config})
        json_files({'id_store_test.json' :{'test1': '1234567', 'test4': '456789'}})
        config = {'file_dispatchloader': {'id_store_path': 'id_store_test.json',
                                          'dispatch_config_paths': 'test_config.toml',
                                          'file_ext': 'txt',
                                          'save_config_defined_id': True}}
        loader = file_dispatchloader.init_loader(config)

        r_config = file_dispatchloader.get_dispatch_config(loader)
        r_text = file_dispatchloader.get_dispatch_text(loader, 'test2')
        file_dispatchloader.add_dispatch_id(loader, 'test3', '3456789')

        file_dispatchloader.cleanup_loader(loader)

        with open('id_store_test.json') as f:
            r_id_store = json.load(f)

        r_config_1 = r_config['nation1']
        assert r_config_1['test1']['ns_id'] == '1234567' and r_config_1['test1']['action'] == 'edit'
        assert r_config_1['test3']['action'] == 'create'
        assert r_text == 'Test text 2'
        assert r_id_store['test2'] == '7654321'
        assert r_id_store['test3'] == '3456789'
        assert 'test4' not in r_id_store

    def test_integration_with_existing_id_store_with_save_config_defined_id_false(self,
                                                                                  toml_files,
                                                                                  json_files,
                                                                                  setup_text_files):
        dispatch_config = {'nation1': {'test1': {'title': 'test_title',
                                                 'category': '1',
                                                 'subcategory': '100'},
                                       'test2': {'ns_id': '7654321',
                                                 'title': 'test_title',
                                                 'category': '1',
                                                 'subcategory': '100'},
                                       'test3': {'title': 'test_title',
                                                 'category': '1',
                                                 'subcategory': '100'}},
                           'nation2': {'test4': {'action': 'remove',
                                                 'title': 'test_title',
                                                 'category': '1',
                                                 'subcategory': '100'}}}
        toml_files({'test_config.toml': dispatch_config})
        json_files({'id_store_test.json': {'test1': '1234567', 'test4': '456789'}})
        config = {'file_dispatchloader': {'id_store_path': 'id_store_test.json',
                                          'dispatch_config_paths': 'test_config.toml',
                                          'file_ext': 'txt',
                                          'save_config_defined_id': False}}
        loader = file_dispatchloader.init_loader(config)

        r_config = file_dispatchloader.get_dispatch_config(loader)
        r_text = file_dispatchloader.get_dispatch_text(loader, 'test2')
        file_dispatchloader.add_dispatch_id(loader, 'test3', '3456789')

        file_dispatchloader.cleanup_loader(loader)

        with open('id_store_test.json') as f:
            r_id_store = json.load(f)

        r_config = r_config['nation1']
        assert r_config['test1']['ns_id'] == '1234567' and r_config['test1']['action'] == 'edit'
        assert r_config['test2']['ns_id'] == '7654321'
        assert r_config['test3']['action'] == 'create'
        assert r_text == 'Test text 2'
        assert r_id_store['test3'] == '3456789'
        assert 'test4' not in r_id_store
        assert 'test2' not in r_id_store