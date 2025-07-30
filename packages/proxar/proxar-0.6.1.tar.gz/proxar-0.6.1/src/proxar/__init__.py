import logging
from pathlib import Path

from .handlers.fetch import FetchHandler
from .handlers.storage import StorageHandler

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class Proxar:
    """A Python client for fetching public proxies.

    This library provides an asynchronous, easy-to-use interface to
    retrieve fresh proxies, handling the complexities of web scraping
    and source aggregation.
    """

    def __init__(self, storage_dir: str | Path | None = None) -> None:
        """Initialize the Proxar instance.

        Args:
            storage_dir: The path to store proxy files. Defaults to None.
        """
        self.storage_handler = StorageHandler(storage_dir)
        self.fetch_handler = FetchHandler(self.storage_handler)

        logger.info("Proxar has been initialized.")

    async def get_proxies(self) -> None:
        """Fetch proxies from various sources and save them."""
        logger.info("Starting proxy fetching process.")
        await self.fetch_handler.get_proxies()
        logger.info("Proxy fetching process has finished.")
