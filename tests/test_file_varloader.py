import os

import pytest
import toml

from nsadm.loaders import file_varloader


class TestCustomVars():
    @pytest.fixture(scope='class')
    def setup_custom_vars_files(self):
        custom_vars_1 = {'foo1': {'bar1': 'john1'}}
        with open('test1.toml', 'w') as f:
            toml.dump(custom_vars_1, f)

        custom_vars_2 = {'foo2': {'bar2': 'john2'}}
        with open('test2.toml', 'w') as f:
            toml.dump(custom_vars_2, f)

        yield 0

        os.remove('test1.toml')
        os.remove('test2.toml')

    def test_load_custom_vars_with_one_file(self, setup_custom_vars_files):
        ins = file_varloader.CustomVars('test1.toml')

        assert ins._custom_vars == {'foo1': {'bar1': 'john1'}}

    def test_load_custom_vars_with_many_files(self, setup_custom_vars_files):
        ins = file_varloader.CustomVars(['test1.toml', 'test2.toml'])

        assert ins._custom_vars == {'foo1': {'bar1': 'john1'},
                                    'foo2': {'bar2': 'john2'}}

    def test_load_custom_vars_with_non_existent_file(self):
        with pytest.raises(FileNotFoundError):
            file_varloader.CustomVars(['asas.toml', 'asss.toml'])

    def test_load_custom_vars_with_no_file(self):
        """Load custom vars if no file is provided.
        Nothing should happen.
        """

        file_varloader.CustomVars([])

    def test_get_custom_vars(self):
        ins = file_varloader.CustomVars('')
        ins._custom_vars = {'foo': {'bar': 'john'}}

        assert ins.custom_vars == {'foo': {'bar': 'john'}}
