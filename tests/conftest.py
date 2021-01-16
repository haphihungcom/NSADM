import os
import json
from unittest import mock

import toml
import pytest


@pytest.fixture
def toml_files(tmp_path):
    """Generate TOML config files for testing."""

    def gen_toml_files(files={'test.toml': {'sec': {'key': 'val'}}}):
        paths = {}
        for name, config in files.items():
            f_path = tmp_path / name
            with open(f_path, 'w') as f:
                toml.dump(config, f)
            paths[name] = f_path

        if len(paths) == 1:
            return paths.popitem()[1]
        return paths

    return gen_toml_files


@pytest.fixture
def text_files(tmp_path):
    """Create text files for testing.
    """

    def gen_text_files(files={'test.txt': 'Foo Bar'}):
        paths = {}
        for name, text in files.items():
            f_path = tmp_path / name
            f_path.write_text(text)
            paths[name] = f_path

        if len(paths) == 1:
            return paths.popitem()[1]
        return paths

    return gen_text_files


@pytest.fixture
def json_files(tmp_path):
    """Create JSON files for testing.
    """

    def gen_json_files(files={'test.json': {'key': 'value'}}):
        paths = {}
        for name, content in files.items():
            f_path = tmp_path / name
            with open(f_path, 'w') as f:
                json.dump(content, f)
            paths[name] = f_path

        if len(paths) == 1:
            return paths.popitem()[1]
        return paths

    return gen_json_files
