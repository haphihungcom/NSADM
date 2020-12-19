import json

from nsadm import loader_api


@loader_api.cred_loader
def get_creds(config):
    with open(config['json_credloader']['cred_path']) as f:
        return json.load(f)


@loader_api.cred_loader
def add_cred(config, name, x_autologin):
    cred_path = config['json_credloader']['cred_path']
    new_creds = {name: x_autologin}

    try:
        with open(cred_path, 'r+') as f:
            creds = json.load(f)
            new_creds.update(creds)
            f.seek(0)
            json.dump(new_creds, f)
    except FileNotFoundError:
        with open(cred_path, 'w') as f:
            json.dump(new_creds, f)


@loader_api.cred_loader
def remove_cred(config, name):
    with open(config['json_credloader']['cred_path'], 'r+') as f:
        creds = json.load(f)
        f.seek(0)
        del creds[name]
        json.dump(creds, f)
        f.truncate()