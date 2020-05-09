import os
import configparser
from unittest import mock

import toml
import pytest


@pytest.fixture
def toml_files():
    """Generate TOML config files for testing."""

    existing_files = []

    def gen_toml_files(files={}):
        for name, config in files.items():
            with open(name, 'w') as f:
                toml.dump(config, f)
                existing_files.append(name)

    yield gen_toml_files

    for name in existing_files:
        os.remove(name)


@pytest.fixture
def text_files():
    """Create text files for testing.
    """

    existing_files = []

    def gen_mock_files(files={'test.txt': ''}):
        for name, text in files.items():
            with open(name, 'w') as f:
                f.write(text)
                existing_files.append(name)

    yield gen_mock_files

    for name in existing_files:
        os.remove(name)
