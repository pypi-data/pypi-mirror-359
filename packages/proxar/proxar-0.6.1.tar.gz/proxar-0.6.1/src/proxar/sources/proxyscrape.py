import asyncio
import logging
from math import ceil
from pathlib import Path
from urllib.parse import urlencode

import aiohttp

from ..errors import ProxarFetchError
from ..handlers.storage import StorageHandler

logger = logging.getLogger(__name__)
method_name = Path(__file__).stem


async def get_proxies(
    session: aiohttp.ClientSession, storage_handler: StorageHandler, url: str
) -> None:
    """Fetch proxies from a URL and store them.

    Args:
        session: The client session used for making requests.
        storage_handler: The handler used for storing the fetched proxies.
        url: The URL to fetch proxies from.

    Raises:
        ProxarFetchError: If the URL returns a bad response, a timeout
            occurs, aiohttp runs into an issue or a general error occurs.
    """
    logger.debug("Attempting to fetch proxies from %s in %s.", url, method_name)

    try:
        # Send HTTP request for proxies
        async with session.get(url) as response:
            json_data = await response.json()

        if json_data:
            # Parse proxies
            proxies = set()

            for proxy_data in json_data["proxies"]:
                proxy_type = proxy_data["protocol"]
                proxy_ip_port = f"{proxy_data['ip']}:{proxy_data['port']}"
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


async def get_urls(
    session: aiohttp.ClientSession, url: str, params: dict[str, str]
) -> list[str]:
    """Get a list of sub-URLs required to fetch all proxies.

    Args:
        session: The client session used for making requests.
        url: The URL to fetch sub-URLs from.
        params: The query parameters for the URL.

    Raises:
        ProxarFetchError: If the URL returns a bad response, a timeout
            occurs, aiohttp runs into an issue or a general error occurs.

    Returns:
        A list containing strings.
    """
    logger.debug(
        "Attempting to find all sub-URLs for %s (%s) in %s.", url, params, method_name
    )

    try:
        # Send HTTP request for URLs
        async with session.get(url, params=params) as response:
            json_data = await response.json()

        if json_data:
            # Parse URLs
            url_count = ceil(json_data["total_records"] / 500)
            urls = []

            for _ in range(url_count):
                urls.append(f"{url}?{urlencode(params)}")
                params["skip"] = str(int(params["skip"]) + 500)

            return urls

        else:
            raise ProxarFetchError(
                f"Unable to get response from {url} ({params}) in {method_name}."
            )

    except asyncio.TimeoutError as e:
        raise ProxarFetchError(
            f"Timed out while getting URLs from {url} ({params}) in {method_name}."
        ) from e

    except aiohttp.ClientError as e:
        raise ProxarFetchError(
            f"Aiohttp error while getting URLs from {url} ({params}) in {method_name}."
        ) from e

    except Exception as e:
        raise ProxarFetchError(
            f"Error while getting URLs from {url} ({params}) in {method_name}."
        ) from e


async def get(session: aiohttp.ClientSession, storage_handler: StorageHandler) -> None:
    """Handle the operations of fetching and storing of proxies.

    Args:
        session: The client session used for making requests.
        storage_handler: The handler used for storing the fetched proxies.
    """
    logger.debug("Attempting to fetch proxies from %s.", method_name)

    # Get all the sub-URLs containing proxies
    base_url = "https://api.proxyscrape.com/v4/free-proxy-list/get"
    params = {
        "request": "get_proxies",
        "protocol": "http,socks4,socks5",
        "proxy_format": "protocolipport",
        "format": "json",
        "timeout": "20",
        "limit": "500",
        "skip": "0",
    }

    urls = await get_urls(session, base_url, params)

    if urls:
        # Create and start tasks for each URL
        tasks = [get_proxies(session, storage_handler, url) for url in urls]
        await asyncio.gather(*tasks)

        logger.debug("Proxies from %s have been fetched.", method_name)
    else:
        raise ProxarFetchError(
            f"Unable to find URLs to fetch proxies from in {method_name}."
        )
