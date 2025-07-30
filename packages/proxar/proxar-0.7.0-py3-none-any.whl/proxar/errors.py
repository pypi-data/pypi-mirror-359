class ProxarError(Exception):
    """Base exception class for all Proxar related errors."""

    pass


class ProxarStorageError(ProxarError):
    """Raise for storage related errors."""

    pass


class ProxarFetchError(ProxarError):
    """Raise for fetching related errors."""

    pass
