import sys
import structlog

import linkpulse.logging
logger = structlog.get_logger()

def main(*args):
    if args[0] == "serve":
        import asyncio
        from linkpulse.app import app
        from uvicorn import run


        logger.debug('Invoking uvicorn.run')
        run('linkpulse.app:app', reload=True, host='0.0.0.0', access_log=True)

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
        from bpython import embed
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
