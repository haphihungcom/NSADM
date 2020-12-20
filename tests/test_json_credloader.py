import os
import json

import pytest
import toml

from nsadm.loaders import json_credloader


@pytest.fixture
def mock_creds_setup():
    creds = {'nation1': 'hunterprime1', 'nation2': 'hunterprime2'}
    with open('test.json', 'w') as f:
        json.dump(creds, f)

    yield

    os.remove('test.json')


@pytest.fixture
def only_clean_creds():
    yield

    os.remove('test.json')


class TestJSONLoader():
    def test_get_creds(self, mock_creds_setup):
        config = {'json_credloader': {'cred_path': 'test.json'}}
        r = json_credloader.get_creds(config)

        assert r['nation2'] == 'hunterprime2'

    def test_add_cred_with_existing_file(self, mock_creds_setup):
        config = {'json_credloader': {'cred_path': 'test.json'}}
        json_credloader.add_cred(config, 'nation3', 'hunterprime3')

        with open('test.json') as f:
            r = json.load(f)

        assert r['nation3'] == 'hunterprime3'

    def test_add_cred_with_non_existing_file(self, only_clean_creds):
        config = {'json_credloader': {'cred_path': 'test.json'}}
        json_credloader.add_cred(config, 'nation1', 'hunterprime1')

        with open('test.json') as f:
            r = json.load(f)

        assert r['nation1'] == 'hunterprime1'

    def test_remove_cred(self, mock_creds_setup):
        config = {'json_credloader': {'cred_path': 'test.json'}}
        json_credloader.remove_cred(config, 'nation2')

        with open('test.json') as f:
            r = json.load(f)

        assert 'nation2' not in r