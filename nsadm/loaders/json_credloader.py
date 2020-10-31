import json

from nsadm import loader_api


@loader_api.cred_loader
def get_creds(config):
    with open(config['json_credloader']['cred_path']) as f:
        return json.load(f)


@loader_api.cred_loader
def add_cred(config, name, autologin):
    with open(config['json_credloader']['cred_path'], 'r+') as f:
        creds = json.load(f)
        f.seek(0)
        creds[name] = autologin
        json.dump(creds, f)


@loader_api.cred_loader
def delete_cred(config, name):
    with open(config['json_credloader']['cred_path'], 'r+') as f:
        creds = json.load(f)
        f.seek(0)
        del creds[name]
        json.dump(creds, f)