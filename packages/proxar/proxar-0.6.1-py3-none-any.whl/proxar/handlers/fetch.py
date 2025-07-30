import asyncio
import logging
from collections.abc import Awaitable

import aiohttp

from ..config import HEADERS
from ..sources import geonode, proxyscrape
from .storage import StorageHandler

logger = logging.getLogger(__name__)


class FetchHandler:
    """Manages the operations of fetching proxies from various sources."""

    def __init__(self, storage_handler: StorageHandler) -> None:
        """Initialize the FetchHandler instance.

        Args:
            storage_handler: A handler for storage operations.
        """
        self.storage_handler = storage_handler

        logger.debug("FetchHandler has been initialized.")

    async def get_proxies(self) -> None:
        """Fetch and store proxies from various sources."""
        logger.debug("Attempting to fetch proxies from various sources.")

        async with aiohttp.ClientSession(headers=HEADERS) as session:
            tasks: dict[str, Awaitable[None]] = {
                "proxyscrape": proxyscrape.get(session, self.storage_handler),
                "geonode": geonode.get(session, self.storage_handler),
            }

            results = await asyncio.gather(*tasks.values(), return_exceptions=True)
            task_names = list(tasks.keys())

            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(
                        "Task '%s' raised an exception: %s",
                        task_names[i],
                        result,
                        exc_info=result,
                    )

        logger.debug("Fetching proxy process completed.")

        logger.debug("Attempting to store proxies.")
        await self.storage_handler._save()
        logger.debug("Proxy storing process has been completed.")
