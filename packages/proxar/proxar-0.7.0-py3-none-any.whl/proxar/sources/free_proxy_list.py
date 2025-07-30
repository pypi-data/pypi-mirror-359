import asyncio
import logging
from pathlib import Path

import aiohttp
from bs4 import BeautifulSoup

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
            text_data = await response.text()

        if text_data:
            # Parse proxies
            proxies = set()

            soup = BeautifulSoup(text_data, "lxml")
            table_rows = soup.select("section#list div.container tbody tr")

            for row in table_rows:
                cols = row.find_all("td")

                ip = cols[0].get_text()
                port = cols[1].get_text()
                protocol_text = cols[4].get_text()
                security_text = cols[6].get_text()

                proxy_type = "http"

                if protocol_text == "Socks4":
                    proxy_type = "socks4"
                elif protocol_text == "Socks5":
                    proxy_type = "socks5"
                elif security_text == "yes":
                    proxy_type = "https"

                proxy_address = f"{ip}:{port}"
                proxies.add((proxy_type, proxy_address))

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

    # Create and start tasks for each URL
    urls = [
        "https://www.socks-proxy.net/",
        "https://free-proxy-list.net/",
        "https://www.us-proxy.org/",
        "https://free-proxy-list.net/uk-proxy.html",
        "https://www.sslproxies.org/",
        "https://free-proxy-list.net/anonymous-proxy.html",
    ]

    tasks = [get_proxies(session, storage_handler, url) for url in urls]
    await asyncio.gather(*tasks)

    logger.debug("Proxies from %s have been fetched.", method_name)
