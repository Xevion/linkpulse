import sys

def main(*args):
    if args[0] == "serve":
        import asyncio
        from hypercorn import Config
        from hypercorn.asyncio import serve
        from linkpulse.app import app

        config = Config()

        asyncio.run(serve(app, config))
    elif args[0] == "migrate":
        from linkpulse.migrate import main
        main(*args[1:])
    else:
        print("Invalid command: {}".format(args[0]))

if __name__ == "__main__":
    if len(sys.argv) == 1:
        main("serve")
    else:
        # Check that args after aren't all whitespace
        remaining_args = ' '.join(sys.argv[1:]).strip()
        if len(remaining_args) > 0:
            main(*sys.argv[1:])