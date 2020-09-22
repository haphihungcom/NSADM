import pluggy

from nsadm import info


dispatch_loader_specs = pluggy.HookspecMarker(info.DISPATCH_LOADER_PROJ)
dispatch_loader = pluggy.HookimplMarker(info.DISPATCH_LOADER_PROJ)

var_loader_specs = pluggy.HookspecMarker(info.VAR_LOADER_PROJ)
var_loader = pluggy.HookimplMarker(info.VAR_LOADER_PROJ)

cred_loader_specs = pluggy.HookspecMarker(info.CRED_LOADER_PROJ)
cred_loader = pluggy.HookimplMarker(info.CRED_LOADER_PROJ)


@dispatch_loader_specs(firstresult=True)
def init_loader(config):
    """Initiate a loader.

    Args:
        config (dict): Loaders' configuration

    Return:
        Loader object
    """

    pass


@dispatch_loader_specs(firstresult=True)
def get_dispatch_info(loader):
    """Get a dict of dispatch parameters.

    Args:
        loader: Loader

    Return:
        dict: Dispatch info
    """
    pass


@dispatch_loader_specs(firstresult=True)
def get_dispatch_text(loader, name):
    """Get content text of a dispatch.

    Args:
        loader: Loader

    Return:
        str: Dispatch content text
    """

    pass


@dispatch_loader_specs(firstresult=True)
def add_dispatch_id(loader, name, id):
    """Add or update dispatch ID when a new dispatch is made.

    Args:
        loader: Loader
        name (str): Dispatch name
        id (str): Dispatch ID
    """

    pass


@var_loader_specs
def get_all_vars(config):
    """Get all variables as a dict.

    Args:
        config (dict): Loaders' configuration

    Return:
        dict: Variables
    """

    pass


@cred_loader_specs(firstresult=True)
def get_all_creds(config):
    """Get all nations' credential.

    Args:
        config (dict): Loaders' configuration

    Return:
        dict: Nations' credential
    """

    pass


@cred_loader_specs(firstresult=True)
def add_cred(config, name, autologin):
    """Add a nation's credential.

    Args:
        config (dict): Loaders' configuration
        name (str): Nation name
        autologin (str): Nation's X-Autologin.
    """

    pass


@cred_loader_specs(firstresult=True)
def delete_cred(config, name):
    """Delete a nation's credential.

    Args:
        config (dict): Loaders' configuration
        name (str): Nation name
    """

    pass
