"""
This module serves as the entry point for the LinkPulse application. It provides
command-line interface (CLI) commands to serve the application, run migrations,
or start a REPL (Read-Eval-Print Loop) session.

Commands:
- serve: Starts the application server using Uvicorn.
- migrate: Runs database migrations.
- repl: Starts an interactive Python shell with pre-imported objects and models.
"""

from linkpulse.logging import setup_logging

# We want to setup logging as early as possible.
setup_logging()

import os
import sys
import structlog


logger = structlog.get_logger()


def main(*args):
    """
    Primary entrypoint for the LinkPulse application
    - Don't import any modules globally unless you're certain it's necessary. Imports should be tightly controlled.
    """
    if args[0] == "serve":
        from linkpulse.utilities import is_development
        from uvicorn import run

        logger.debug("Invoking uvicorn.run")

        run(
            "linkpulse.app:app",
            reload=is_development,
            host="0.0.0.0",
            port=int(os.getenv("PORT", "8000")),
            log_config={
                "version": 1,
                "disable_existing_loggers": False,
                "loggers": {
                    "uvicorn": {"propagate": True},
                    "uvicorn.access": {"propagate": True},
                },
            },
        )

    elif args[0] == "migrate":
        from linkpulse.migrate import main

        main(*args)
    elif args[0] == "repl":
        import linkpulse

        # import most useful objects, models, and functions
        lp = linkpulse  # alias
        from linkpulse.utilities import get_db
        from linkpulse.app import app
        from linkpulse.models import BaseModel, IPAddress

        db = get_db()

        # start REPL
        from bpython import embed  # type: ignore

        embed(locals())
    else:
        raise ValueError("Unexpected command: {}".format(" ".join(args)))


if __name__ == "__main__":
    logger.debug("Entrypoint", argv=sys.argv)
    args = sys.argv[1:]

    if len(args) == 0:
        logger.debug("No arguments provided, defaulting to 'serve'")
        main("serve")
    else:
        # Check that args after aren't all whitespace
        normalized_args = " ".join(args).strip()
        if len(normalized_args) == 0:
            logger.warning("Whitespace arguments provided, defaulting to 'serve'")

        logger.debug("Invoking main with arguments", args=args)
        main(*args)
