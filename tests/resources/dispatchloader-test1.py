"""A simple dispatch loader for testing.
"""


from nsadm import loader_api


class DispatchLoaderTest1():
    def __init__(self, config):
        self.config = config

    def get_dispatch_config(self):
        return {'foo1': 'bar1', 'foo2': 'bar2'}

    def get_dispatch_text(self, name):
        return 'Dispatch content of {}'.format(name)

    def add_dispatch_id(self, name, id):
        return

    def cleanup_loader(self):
        return


@loader_api.dispatch_loader
def init_loader(config):
    return DispatchLoaderTest1(config['dispatchloader-test1'])


@loader_api.dispatch_loader
def get_dispatch_config(loader):
    return loader.get_dispatch_config()


@loader_api.dispatch_loader
def get_dispatch_text(loader, name):
    return loader.get_dispatch_text(name)


@loader_api.dispatch_loader
def add_dispatch_id(loader, name, id):
    loader.add_dispatch_id(name, id)
    return True


@loader_api.dispatch_loader
def cleanup_loader(loader):
    return loader.cleanup_loader()