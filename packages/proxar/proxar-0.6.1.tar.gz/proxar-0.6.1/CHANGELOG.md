# Changelog

All notable changes to Xify will be documented in this file.

## v0.6.1 (2025-07-02)

### Bug Fixes

- **source**: improve proxyscrape fetching process

## v0.6.0 (2025-07-01)

### Bug Fixes

- **fetch**: correct logging form
- **errors**: custom errors use exception class

### Features

- **source**: add geonode

## v0.5.0 (2025-07-01)

### Code Refactoring

- **config**: remove unneeded header fields
- **storage**: signal save method to be used internally

### Features

- **source**: add proxyscrape as a source

## v0.4.0 (2025-06-30)

### Features

- **fetch**: add proxy fetching functionality
- **config**: add project config python file
- **errors**: add fetch related custom errors
- **fetch**: introduce fetch handler into project

## v0.3.0 (2025-06-30)

### Code Refactoring

- improve structure of main class init

### Features

- **storage**: synchronously save proxies locally
- **storage**: asynchronously save proxies locally
- **storage**: add fetched proxy into memory
- **storage**: load local proxies for uniqueness
- **storage**: add a structure to hold proxies in memory
- **errors**: add custom project level errors

## v0.2.0 (2025-06-29)

### Features

- add storage handler with platformdirs integration

## v0.1.2 (2025-06-29)

### Bug Fixes

- change gitignore order

## v0.1.1 (2025-06-29)

### Bug Fixes

- issue publishing package to pypi

## v0.1.0 (2025-06-29)

### Features

- add main class
