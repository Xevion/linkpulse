import sys
import structlog


logger = structlog.get_logger()


def main(*args):
    if args[0] == "serve":
        from linkpulse.logging import setup_logging
        from uvicorn import run

        setup_logging()

        logger.debug("Invoking uvicorn.run")
        run(
            "linkpulse.app:app",
            reload=True,
            host="0.0.0.0",
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

        main(*args[1:])
    elif args[0] == "repl":
        import linkpulse

        # import most useful objects, models, and functions
        lp = linkpulse  # alias
        from linkpulse.app import app, db
        from linkpulse.models import BaseModel, IPAddress

        # start REPL
        from bpython import embed  # type: ignore

        embed(locals())
    else:
        print("Invalid command: {}".format(args[0]))


if __name__ == "__main__":
    if len(sys.argv) == 1:
        main("serve")
    else:
        # Check that args after aren't all whitespace
        remaining_args = " ".join(sys.argv[1:]).strip()
        if len(remaining_args) > 0:
            main(*sys.argv[1:])
