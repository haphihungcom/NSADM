class NSADMError(Exception):
    pass


class DispatchAPIError(NSADMError):
    pass


class DispatchUploader(NSADMError):
    pass


class DispatchRendererError(NSADMError):
    pass


class BBParserError(DispatchRendererError):
    pass


class TemplateRendererError(DispatchRendererError):
    pass