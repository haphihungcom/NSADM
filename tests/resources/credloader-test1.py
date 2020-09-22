"""A simple credential loader for testing.
"""


from nsadm import loader_api


@loader_api.cred_loader
def get_all_creds(config):
    return {'nation1': '123456'}


@loader_api.cred_loader
def add_cred(config, name, autologin):
    return True

@loader_api.cred_loader
def delete_cred(config, name):
    return True