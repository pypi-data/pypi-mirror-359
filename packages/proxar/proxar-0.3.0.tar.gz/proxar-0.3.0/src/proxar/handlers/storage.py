import asyncio
import atexit
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path

import aiofiles
import platformdirs

from ..errors import ProxarStorageError

logger = logging.getLogger(__name__)


@dataclass
class ProxyResources:
    """Represents the resources for a single proxy type.

    This includes a thread-safe lock for concurrent operations and a set of
    proxy strings to ensure uniqueness.
    """

    lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    proxies: set[str] = field(default_factory=set)


class StorageHandler:
    """Handle persistent, asynchronous storage of proxies in a JSON file."""

    def __init__(self, storage_dir: str | Path | None) -> None:
        """Initializes the StorageHandler instance.

        Args:
            storage_dir: The directory path to store the proxies.json file. If None,
                an OS-specific user data directory is used.
        """
        # Set a flag to track unsaved proxies.
        self._dirty: bool = False

        # Set storage dir path and ensure its existence
        if storage_dir is None:
            self.storage_dir_path = Path(platformdirs.user_data_dir("proxar"))
            logger.debug(
                "No storage directory provided. Using default path: %s",
                self.storage_dir_path,
            )
        else:
            self.storage_dir_path = Path(storage_dir)
            logger.debug("Using provided storage directory: %s", self.storage_dir_path)

        self.storage_dir_path.mkdir(parents=True, exist_ok=True)
        self.json_file_path = self.storage_dir_path / "proxies.json"

        # Proxy types mapped to their associated resource instances.
        self.proxy_resources: dict[str, ProxyResources] = {
            "http": ProxyResources(),
            "https": ProxyResources(),
            "socks4": ProxyResources(),
            "socks5": ProxyResources(),
        }

        self._load_proxies_from_disk()

        # Register the synchronous save as a fallback on graceful exit.
        atexit.register(self._save_proxies_to_disk_sync)

        logger.debug("StorageHandler has been initialized.")

    def _load_proxies_from_disk(self) -> None:
        """Loads proxies from the JSON file into their in-memory sets.

        Raises:
            ProxarStorageError: If there's an issue loading proxies from the disk
                file, such as a JSON decoding or I/O errors.
        """
        if not self.json_file_path.exists():
            logger.debug(
                "Storage file not found at %s, starting fresh.", self.json_file_path
            )
            return

        try:
            with open(self.json_file_path, encoding="utf-8") as f:
                data = json.load(f)

            total_proxies_loaded = 0
            for proxy_type, proxies in data.items():
                if proxy_type in self.proxy_resources and isinstance(proxies, list):
                    unique_proxies = set(proxies)
                    self.proxy_resources[proxy_type].proxies.update(unique_proxies)
                    total_proxies_loaded += len(unique_proxies)

            if total_proxies_loaded > 0:
                count_summary = ", ".join(
                    f"{len(proxies)} {proxy_type.upper()}"
                    for proxy_type, proxies in data.items()
                    if proxies
                )
                logger.info(
                    "Loaded %d proxies (%s) from %s",
                    total_proxies_loaded,
                    count_summary,
                    self.json_file_path,
                )
            else:
                logger.debug("Storage file at %s was empty.", self.json_file_path)

        except (OSError, json.JSONDecodeError) as e:
            raise ProxarStorageError(f"Failed to load proxies from disk: {e}") from e

    async def store_proxy(self, proxy_type: str, proxy: str) -> None:
        """Add a proxy to the appropriate in-memory set if it is unique.

        Args:
            proxy_type: The type of proxy to store.
            proxy: The proxy string to store.

        Raises:
            ProxarStorageError: If the provided proxy_type is not supported.
        """
        proxy_type = proxy_type.lower()
        resources = self.proxy_resources.get(proxy_type)

        if not resources:
            raise ProxarStorageError(f"Unknown proxy type '{proxy_type}'.")

        async with resources.lock:
            if proxy not in resources.proxies:
                resources.proxies.add(proxy)
                self._dirty = True

    def _get_all_proxies_as_dict(self) -> dict[str, list[str]]:
        """Gathers all proxies from memory into one dictionary.

        Returns:
            Dictionary mapping proxy types to lists of proxy strings.
        """
        return {
            proxy_type: list(res.proxies)
            for proxy_type, res in self.proxy_resources.items()
        }

    async def save(self) -> None:
        """Asynchronously and atomically saves all proxies to the JSON file.

        Raises:
            ProxarStorageError: If the file cannot be written to disk due to I/O or
                permission errors.
        """
        if not self._dirty:
            logger.debug("No new proxies to save, skipping write to disk.")
            return

        all_proxies_data = self._get_all_proxies_as_dict()
        temp_file_path = self.json_file_path.with_suffix(".json.tmp")

        try:
            async with aiofiles.open(temp_file_path, "w", encoding="utf-8") as f:
                await f.write(json.dumps(all_proxies_data, indent=2))

            temp_file_path.rename(self.json_file_path)
            self._dirty = False  # Reset dirty flag after successful save.

            count_summary = ", ".join(
                f"{len(proxies)} {proxy_type.upper()}"
                for proxy_type, proxies in all_proxies_data.items()
                if proxies
            )
            total_proxies = sum(len(p) for p in all_proxies_data.values())

            logger.info(
                "Successfully saved %d proxies (%s) to %s",
                total_proxies,
                count_summary,
                self.json_file_path,
            )

        except OSError as e:
            raise ProxarStorageError(f"Failed to save proxies to disk: {e}") from e

        finally:
            # Ensure the temporary file is cleaned up, even if an error occurs.
            if temp_file_path.exists():
                temp_file_path.unlink()

    def _save_proxies_to_disk_sync(self) -> None:
        """Synchronously saves all proxies to disk as a fallback.

        Raises:
            ProxarStorageError: If the file cannot be written to disk due to I/O or
                permission errors.
        """
        if not self._dirty:
            return

        all_proxies_data = self._get_all_proxies_as_dict()
        temp_file_path = self.json_file_path.with_suffix(".json.tmp")

        try:
            with open(temp_file_path, "w", encoding="utf-8") as f:
                json.dump(all_proxies_data, f, indent=2)

            temp_file_path.rename(self.json_file_path)
            self._dirty = False

            count_summary = ", ".join(
                f"{len(proxies)} {proxy_type.upper()}"
                for proxy_type, proxies in all_proxies_data.items()
                if proxies
            )
            total_proxies = sum(len(p) for p in all_proxies_data.values())

            logger.info(
                "Shutdown hook: Saved %d proxies (%s) to %s",
                total_proxies,
                count_summary,
                self.json_file_path,
            )

        except OSError as e:
            raise ProxarStorageError(
                f"Shutdown hook: Failed to save proxies to disk: {e}"
            ) from e

        finally:
            # Ensure the temporary file is cleaned up, even if an error occurs.
            if temp_file_path.exists():
                temp_file_path.unlink()
