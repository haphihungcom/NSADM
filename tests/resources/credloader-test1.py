"""A simple credential loader for testing.
"""


from nsadm import loader_api


@loader_api.cred_loader
def get_all_creds(config):
    return {'nation1': 'password1'}


@loader_api.cred_loader
def update_cred(config, name, autologin):
    return
