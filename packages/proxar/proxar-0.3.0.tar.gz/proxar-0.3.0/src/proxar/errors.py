class ProxarError(BaseException):
    """Base exception class for all Proxar related errors."""

    pass


class ProxarStorageError(ProxarError):
    """Raise for storage related errors."""

    pass
