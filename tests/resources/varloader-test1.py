"""A simple variable loader for testing.
"""


from nsadm import loader_api


@loader_api.var_loader
def get_all_vars(config):
    return {'key1': config['varloader-test1']}
