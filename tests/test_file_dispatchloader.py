import os
import json
import toml
import shutil
from unittest import mock

import pytest

from nsadm import exceptions
from nsadm.loaders import file_dispatchloader


class TestIDStore():
    @pytest.fixture
    def id_file(self, json_files):
        return json_files({'test.json': {'Test': '12345'}})

    def test_init_load_id_store_from_json_when_file_not_exist_with_id_store_path(self):
        ins = file_dispatchloader.IDStore('test.json')

        ins.load_from_json()

        assert os.path.isfile('test.json')
        assert ins == {}

        os.remove('test.json')

    def test_init_load_id_store_from_json_when_file_not_exist_with_no_id_store_path(self, tmp_path):
        with mock.patch('nsadm.info.DATA_DIR', tmp_path):
            ins = file_dispatchloader.IDStore(None)

            ins.load_from_json()

        assert ins == {}

    def test_init_load_id_store_when_file_already_exists(self, id_file):
        ins = file_dispatchloader.IDStore(id_file)

        ins.load_from_json()

        assert ins['Test'] == '12345'

    def test_load_id_store_from_dispatch_config_with_no_remove_action_and_no_override(self, tmp_path):
        id_file_path = tmp_path / 'id_store.json'
        ins = file_dispatchloader.IDStore(id_file_path)
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

    def test_load_id_store_from_dispatch_config_with_no_remove_action_and_with_override(self, tmp_path):
        """Previously loaded id must be overridden with
        the dispatch config version when this method is called.
        """

        id_file_path = tmp_path / 'id_store.json'
        ins = file_dispatchloader.IDStore(id_file_path)
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

    def test_load_id_store_from_dispatch_config_with_remove_action(self, tmp_path):
        """Id of dispatches with remove action should not be loaded.
        """

        id_file_path = tmp_path / 'id_store.json'
        ins = file_dispatchloader.IDStore(id_file_path)
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
    def test_save_when_saved_is_true(self, json_dump, id_file):
        ins = file_dispatchloader.IDStore(id_file)
        ins.saved = True

        ins.save()

        json_dump.assert_not_called()

    @mock.patch('json.dump')
    def test_save_when_saved_is_false(self, json_dump, id_file):
        ins = file_dispatchloader.IDStore(id_file)
        ins.saved = False

        ins.save()

        json_dump.assert_called_once()


class TestLoadDispatchConfig():
    @pytest.fixture
    def dispatch_config_files(self, toml_files):
        return toml_files({'test1.toml': {'Test1': 'TestVal1'},
                           'test2.toml': {'Test2': 'TestVal2'}})

    def test_when_dispatch_config_path_is_one(self, dispatch_config_files):
        r = file_dispatchloader.load_dispatch_config(dispatch_config_files / 'test1.toml')

        assert r == {'Test1': 'TestVal1'}

    def test_when_dispatch_config_path_is_list(self, dispatch_config_files):
        r = file_dispatchloader.load_dispatch_config([dispatch_config_files / 'test1.toml',
                                                      dispatch_config_files / 'test2.toml'])

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


class TestFileDispatchLoaderObj():

    def test_get_dispatch_text(self, text_files):
        template_path = text_files({'test1.txt': 'Test text 1', 'test2.txt': 'Test text 2'})

        obj = file_dispatchloader.FileDispatchLoader({}, {}, template_path, '.txt')

        assert obj.get_dispatch_text('test1') == 'Test text 1'

    def test_get_dispatch_text_with_non_existing_file(self, tmp_path):
        obj = file_dispatchloader.FileDispatchLoader({}, {}, tmp_path, '.txt')

        with pytest.raises(exceptions.LoaderError):
            obj.get_dispatch_text('test2')


class TestFileDispatchLoader():
    @pytest.fixture
    def dispatch_files(self, text_files):
        return text_files({'test1.txt': 'Test text 1', 'test2.txt': 'Test text 2',
                           'text3.txt': 'Test text 3'})

    def test_edit_dispatch_with_existing_id_store(self, toml_files, json_files, dispatch_files):
        dispatch_config = {'nation1': {'test1': {'title': 'test_title',
                                                 'category': '1',
                                                 'subcategory': '100'},
                                       'test2': {'title': 'test_title',
                                                 'category': '1',
                                                 'subcategory': '100'},
                                       'test3': {'title': 'test_title',
                                                 'category': '1',
                                                 'subcategory': '100'}},
                           'nation2': {'test4': {'title': 'test_title',
                                                 'category': '1',
                                                 'subcategory': '100'}}}
        dispatch_config_path = toml_files({'dispatch_config.toml': dispatch_config})
        id_file_path = json_files({'id_store_test.json': {'test1': '1234567', 'test2': '456789',
                                                          'test3': '9876545', 'test4': '454545'}})
        config = {'file_dispatchloader': {'id_store_path': id_file_path,
                                          'dispatch_config_paths': dispatch_config_path,
                                          'template_path': dispatch_files,
                                          'file_ext': '.txt',
                                          'save_config_defined_id': False}}
        loader = file_dispatchloader.init_dispatch_loader(config)

        r_config = file_dispatchloader.get_dispatch_config(loader)
        r_text = file_dispatchloader.get_dispatch_text(loader, 'test2')

        file_dispatchloader.cleanup_dispatch_loader(loader)

        r_config_1 = r_config['nation1']
        r_config_2 = r_config['nation2']
        assert r_config_1['test1']['ns_id'] == '1234567' and r_config_1['test1']['action'] == 'edit'
        assert r_config_2['test4']['ns_id'] == '454545' and r_config_2['test4']['action'] == 'edit'
        assert r_text == 'Test text 2'

    def test_add_new_dispatch_with_non_existing_id_store_with_save_config_defined_id_true(self,
                                                                                          toml_files,
                                                                                          dispatch_files,
                                                                                          tmp_path):
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
        dispatch_config_path = toml_files({'dispatch_config.toml': dispatch_config})
        id_file_path = tmp_path / 'id_store.json'
        config = {'file_dispatchloader': {'id_store_path': id_file_path,
                                          'dispatch_config_paths': dispatch_config_path,
                                          'template_path': dispatch_files,
                                          'file_ext': '.txt',
                                          'save_config_defined_id': True}}
        loader = file_dispatchloader.init_dispatch_loader(config)

        r_config = file_dispatchloader.get_dispatch_config(loader)
        file_dispatchloader.add_dispatch_id(loader, 'test1', '1234567')

        file_dispatchloader.cleanup_dispatch_loader(loader)

        with open(id_file_path) as f:
            r_id_store = json.load(f)

        assert r_config['nation1']['test1']['action'] == 'create'
        assert r_config['nation1']['test2']['action'] == 'edit'
        assert r_id_store['test1'] == '1234567'
        assert r_id_store['test2'] == '7654321'
        assert 'test3' not in r_id_store

    def test_new_dispatch_with_existing_id_store_with_save_config_defined_id_true(self,
                                                                                  toml_files,
                                                                                  json_files,
                                                                                  dispatch_files):
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
        dispatch_config_path = toml_files({'dispatch_config.toml': dispatch_config})
        id_file_path = json_files({'id_store.json' :{'test1': '1234567', 'test4': '456789'}})
        config = {'file_dispatchloader': {'id_store_path': id_file_path,
                                          'dispatch_config_paths': dispatch_config_path,
                                          'template_path': dispatch_files,
                                          'file_ext': '.txt',
                                          'save_config_defined_id': True}}
        loader = file_dispatchloader.init_dispatch_loader(config)

        r_config = file_dispatchloader.get_dispatch_config(loader)
        file_dispatchloader.add_dispatch_id(loader, 'test3', '3456789')

        file_dispatchloader.cleanup_dispatch_loader(loader)

        with open(id_file_path) as f:
            r_id_store = json.load(f)

        r_config_1 = r_config['nation1']
        assert r_config_1['test1']['ns_id'] == '1234567' and r_config_1['test1']['action'] == 'edit'
        assert r_config_1['test3']['action'] == 'create'
        assert r_id_store['test2'] == '7654321'
        assert r_id_store['test3'] == '3456789'
        assert 'test4' not in r_id_store

    def test_new_dispatch_with_existing_id_store_with_save_config_defined_id_false(self,
                                                                                   toml_files,
                                                                                   json_files,
                                                                                   dispatch_files):
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
        dispatch_config_path = toml_files({'dispatch_config.toml': dispatch_config})
        id_file_path = json_files({'id_store_test.json': {'test1': '1234567', 'test4': '456789'}})
        config = {'file_dispatchloader': {'id_store_path': id_file_path,
                                          'dispatch_config_paths': dispatch_config_path,
                                          'template_path': dispatch_files,
                                          'file_ext': '.txt',
                                          'save_config_defined_id': False}}
        loader = file_dispatchloader.init_dispatch_loader(config)

        r_config = file_dispatchloader.get_dispatch_config(loader)
        r_text = file_dispatchloader.get_dispatch_text(loader, 'test2')
        file_dispatchloader.add_dispatch_id(loader, 'test3', '3456789')

        file_dispatchloader.cleanup_dispatch_loader(loader)

        with open(id_file_path) as f:
            r_id_store = json.load(f)

        r_config = r_config['nation1']
        assert r_config['test1']['ns_id'] == '1234567' and r_config['test1']['action'] == 'edit'
        assert r_config['test2']['ns_id'] == '7654321'
        assert r_config['test3']['action'] == 'create'
        assert r_text == 'Test text 2'
        assert r_id_store['test3'] == '3456789'
        assert 'test4' not in r_id_store
        assert 'test2' not in r_id_store
