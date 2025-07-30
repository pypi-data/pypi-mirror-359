# Proxar

Proxar is a Python client for fetching public proxies from various online sources.

It uses an asynchronous architecture to retrieve fresh proxies from multiple providers, providing a stream of proxies for use in web scraping, data analysis, and other network-intensive tasks.

---

## Features

- **Multi-Source Aggregation:** Fetches and aggregates proxies from a diverse set of public sources, including web pages and APIs.
- **Asynchronous Architecture:** Built on `asyncio` and `aiohttp` for high-performance, non-blocking network operations.
- **Flexible Usage:** Choose to have proxies saved directly to a file or returned as a Python dictionary for immediate use.
- **Atomic JSON Storage:** Safely saves proxies to a single `proxies.json` file, preventing data corruption with atomic write operations.
- **Platform-Aware Storage:** Uses `platformdirs` to store proxies in the appropriate user-specific data directory, but allows overriding with a custom path.
- **Persistent Session:** Loads previously fetched proxies at startup to maintain a persistently unique and growing list across sessions.

---

## Installation

### From PyPI (Recommended)

```bash
pip install proxar
```

### From Source

You can set up Proxar by cloning the repository directly.

1.  Clone the repository:
    ```bash
    git clone https://github.com/filming/proxar.git
    cd proxar
    ```
2.  Install the project and its dependencies:
    ```bash
    pip install -e .
    ```
    - To install development dependencies like `mypy` and `ruff`, use:
    ```bash
    pip install -e .[dev]
    ```

---

## Usage

Here’s how to use Proxar to fetch proxies. You can either save them to a file or work with them directly.

```python
import asyncio
from proxar import Proxar

async def main():
    # Initialize Proxar.
    # By default, it uses a platform-specific data directory.
    # You can provide a custom path, e.g., Proxar(storage_dir="path/to/proxies")
    proxar = Proxar()

    try:
        # --- Example 1: Save proxies to a file (default behavior) ---
        print("Fetching proxies and saving to file...")
        await proxar.get_proxies(save_to_file=True)
        print("Proxy fetching and saving complete.")
        # Proxies are saved in proxies.json inside the storage directory.

        # --- Example 2: Get proxies as a dictionary ---
        print("\nFetching proxies and returning them directly...")
        proxies = await proxar.get_proxies(save_to_file=False)
        if proxies:
            http_proxies = proxies.get("http", [])
            print(f"Fetched {len(http_proxies)} HTTP proxies.")
            # print("First 5 HTTP proxies:", http_proxies[:5])

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Configuration

Proxar is designed to work out-of-the-box with minimal configuration.

-   **Storage:** By default, Proxar stores fetched proxies in a `proxar` directory inside your user data folder. You can override this by passing a `storage_dir` argument during initialization.
-   **Logging:** The library uses the standard `logging` module. You can configure the root logger in your application to control the log level and output format.

---

## Dependencies

All project dependencies are managed via [`pyproject.toml`](pyproject.toml).

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Contributing

Contributions, bug reports, and feature requests are welcome!
Please open an issue or submit a pull request on [GitHub](https://github.com/filming/proxar).
