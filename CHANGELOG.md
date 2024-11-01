# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Improved documentation in multiple areas
  - `__main__.py`
  - `logging.py`

### Fixed

- Raised level for `apscheduler.scheduler` logger to `WARNING` to prevent excessive logging
- IPv4 interface bind in production, preventing Railway's Private Networking from functioning
- Reloader mode enabled in production

## [0.2.1] - 2024-11-01

### Changed

- Mildly reformatted `README.md`
- A development mode check for the `app.state.ip_pool`'s initialization (caused application failure in production only)

### Fixed

- Improper formatting of blockquote Alerts in `README.md`

## [0.2.0] - 2024-11-01

### Added

- This `CHANGELOG.md` file
- Structured logging with `structlog`
  - Readable `ConsoleRenderer` for local development
  - `JSONRenderer` for production logging
- Request-Id Middleware with `asgi-correlation-id`
- Expanded README.md with more comprehensive instructions for installation & usage
  - Repository-wide improved documentation details, comments
- CodeSpell exceptions in VSCode workspace settings

### Changed

- Switched from `hypercorn` to `uvicorn` for ASGI runtime
- Switched to direct module 'serve' command in `backend/run.sh` & `backend/railway.json`
- Relocated `.tool-versions` to project root
- Massively overhauled run.sh scripts, mostly for backend service
- Improved environment variable access in logging setup
- Root logger now adheres to the same format as the rest of the application
- Hide IP list when error occurs on client
- `run.sh` passes through all arguments, e.g. bpython REPL via `./run.sh repl`
- Use UTC timezone for timestamps, localize human readable strings, fixing 4 hour offset issue
- `is_development` available globally from `utilities` module

### Removed

- Deprecated `startup` and `shutdown` events
- Development-only randomized IP address pool for testing
