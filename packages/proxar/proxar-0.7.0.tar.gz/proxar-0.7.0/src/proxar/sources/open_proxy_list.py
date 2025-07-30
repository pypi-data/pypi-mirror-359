import asyncio
import logging
from pathlib import Path

import aiohttp

from ..errors import ProxarFetchError
from ..handlers.storage import StorageHandler

logger = logging.getLogger(__name__)
method_name = Path(__file__).stem


async def get_proxies(
    session: aiohttp.ClientSession,
    storage_handler: StorageHandler,
    url: str,
    proxy_type: str,
) -> None:
    """Fetch proxies from a URL and store them.

    Args:
        session: The client session used for making requests.
        storage_handler: The handler used for storing the fetched proxies.
        url: The URL to fetch proxies from.
        proxy_type: The type of proxies that will be fetched.

    Raises:
        ProxarFetchError: If the URL returns a bad response, a timeout
            occurs, aiohttp runs into an issue or a general error occurs.
    """
    logger.debug("Attempting to fetch proxies from %s in %s.", url, method_name)

    try:
        # Send HTTP request for proxies
        async with session.get(url) as response:
            text_data = await response.text()

        if text_data:
            # Parse proxies
            proxies = set()

            for proxy_ip_port in text_data.splitlines():
                if proxy_ip_port:
                    proxies.add((proxy_type, proxy_ip_port))

            # Store proxies
            for proxy in proxies:
                await storage_handler.store_proxy(proxy[0], proxy[1])

            logger.debug(
                "%s proxies from %s in %s have been fetched.",
                len(proxies),
                url,
                method_name,
            )
        else:
            raise ProxarFetchError(
                f"Unable to get response from {url} in {method_name}."
            )

    except asyncio.TimeoutError as e:
        raise ProxarFetchError(
            f"Timed out while fetching proxies from {url} in {method_name}."
        ) from e

    except aiohttp.ClientError as e:
        raise ProxarFetchError(
            f"Aiohttp error while fetching proxies from {url} in {method_name}."
        ) from e

    except Exception as e:
        raise ProxarFetchError(
            f"Error while fetching proxies from {url} in {method_name}."
        ) from e


async def get(session: aiohttp.ClientSession, storage_handler: StorageHandler) -> None:
    """Handle the operations of fetching and storing of proxies.

    Args:
        session: The client session used for making requests.
        storage_handler: The handler used for storing the fetched proxies.
    """
    logger.debug("Attempting to fetch proxies from %s.", method_name)

    # Get all the sub-URLs containing proxies
    urls = {
        proxy_type: (
            "https://raw.githubusercontent.com/roosterkid/openproxylist/refs/heads"
            f"/main/{proxy_type.upper()}_RAW.txt"
        )
        for proxy_type in ("https", "socks4", "socks5")
    }

    # Create and start tasks for each URL
    tasks = [
        get_proxies(session, storage_handler, urls[proxy_type], proxy_type)
        for proxy_type in urls
    ]
    await asyncio.gather(*tasks)

    logger.debug("Proxies from %s have been fetched.", method_name)
