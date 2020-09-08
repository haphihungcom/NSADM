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


class DispatchUploadingError(NSADMError):
    """Dispatch upload error.
    """

    pass


class DispatchRenderingError(NSADMError):
    """Dispatch rendering error.
    """

    pass


class BBParsingError(DispatchRenderingError):
    """BBCode parsing errors.
    """

    pass


class TemplateRendererError(DispatchRenderingError):
    """Jinja template rendering errors.
    """

    pass
