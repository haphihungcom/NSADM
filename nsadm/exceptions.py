"""Exceptions for NSADM-specific errors.
"""

class NSADMError(Exception):
    """NSADM general error.
    """


class ConfigError(NSADMError):
    """NSADM general config error.
    """


class LoaderError(NSADMError):
    """Loader plugin error.
    """

    def __init__(self, suppress_nsadm_error=True):
        self.suppress_nsadm_error = suppress_nsadm_error
        super().__init__()


class DispatchTextNotFound(LoaderError):
    """Dispatch text not found error.
    """


class DispatchAPIError(NSADMError):
    """Dispatch API error.
    """


class UnknownDispatchError(DispatchAPIError):
    """This dispatch does not exist.
    """


class NotOwnerDispatchError(DispatchAPIError):
    """You do not own this dispatch.
    """


class NationLoginError(DispatchAPIError):
    """Failed to log in to nation.
    """


class DispatchUpdatingError(NSADMError):
    """Dispatch update error.
    """


class NonexistentCategoryError(DispatchUpdatingError):
    """Category or subcategory doesn't exist.
    """

    def __init__(self, category_type, category_value):
        self.category_type = category_type
        self.category_value = category_value
        super().__init__()


class DispatchRenderingError(NSADMError):
    """Dispatch rendering error.
    """


class BBParsingError(DispatchRenderingError):
    """BBCode parsing errors.
    """


class TemplateRendererError(DispatchRenderingError):
    """Jinja template rendering errors.
    """
