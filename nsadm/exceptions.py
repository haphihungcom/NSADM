class NSADMError(Exception):
    """NSADM general error.
    """

    pass


class LoaderError(NSADMError):
    """Loader plugin error.
    """

    pass


class DispatchAPIError(NSADMError):
    """Dispatch API error.
    """

    pass


class DispatchUpload(NSADMError):
    """Dispatch upload error.
    """

    pass


class DispatchRenderError(NSADMError):
    """Dispatch rendering error.
    """

    pass


class BBParsingError(DispatchRendererError):
    """BBCode parsing errors.
    """

    pass


class TemplateRendererError(DispatchRendererError):
    """Jinja template rendering errors.
    """

    pass