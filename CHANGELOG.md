# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## Added

- A release checklist to the `CHANGELOG.md` file, as a reminder for procedure.
- backend: `pwdlib[argon2]` for password hashing
- backend: provided `LOG_JSON_FORMAT` and `LOG_LEVEL` environment variable defaults in `run.sh` development script
- backend: `User` model, `Session` model with migration script
- backend: `utc_now` helper function
- frontend: Added `clsx` package

## Changed

- frontend: Updated `eslint` to `9.x.x`, `@types/node` to `22.9.x`

## Removed

- frontend: Removed `@nkzw/eslint-config` package
- backend: `IPAddress` Model (definition + DB state via migration) & all related code

## [0.2.2] - 2024-11-01

### Added

- Added the `orjson` serializer for faster JSON serialization
  - Used in `structlog`'s `JSONRenderer` for production logging
  - Used in `fastapi`'s `Response` for faster response serialization
- Improved documentation in multiple files
  - `__main__.py`
  - `logging.py`
  - `models.py`
  - `utilities.py`
  - `migrate.py`
  - `responses.py`
- A `get_db` utility function to retrieve a reference to the database (with type hinting)
- Minor `DATABASE_URL` check in `models.py` to prevent cryptic connection issues

## Changed

- Migration script now uses `structlog` instead of `print`
  - Migration script output is tuned to structlog as well.
- Migration names must be at least 9 characters long
- Unspecified IPv6 addresses are returned without hiding in `utilities.hide_ip`
- Applied `get_db` utility function in all applicable areas.

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
