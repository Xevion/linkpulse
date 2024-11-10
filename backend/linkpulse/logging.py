import logging
import os
import sys
from typing import Any, List, Optional

import structlog
from structlog.types import EventDict, Processor


def decode_bytes(_: Any, __: Any, bs: bytes) -> str:
    """
    orjson returns bytes; we need strings
    """
    return bs.decode()


def rename_event_key(_: Any, __: Any, event_dict: EventDict) -> EventDict:
    """
    Renames the `event` key to `msg`, as Railway expects it in that form.
    """
    event_dict["msg"] = event_dict.pop("event")
    return event_dict


def drop_color_message_key(_: Any, __: Any, event_dict: EventDict) -> EventDict:
    """
    Uvicorn logs the message a second time in the extra `color_message`, but we don't
    need it. This processor drops the key from the event dict if it exists.
    """
    event_dict.pop("color_message", None)
    return event_dict


def setup_logging(json_logs: Optional[bool] = None, log_level: Optional[str] = None) -> None:
    # Pull from environment variables, apply defaults if not set
    if json_logs is None:
        json_logs = os.getenv("LOG_JSON_FORMAT", "true").lower() == "true"
    if log_level is None:
        log_level = os.getenv("LOG_LEVEL", "INFO")

    def flatten(n):
        """
        Flattens a nested list into a single list of elements.
        """
        match n:
            case []:
                return []
            case [[*hd], *tl]:
                return [*flatten(hd), *flatten(tl)]
            case [hd, *tl]:
                return [hd, *flatten(tl)]

    # Shared structlog processors, both for the root logger and foreign loggers
    shared_processors: List[Processor] = flatten(
        [
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.stdlib.ExtraAdder(),
            drop_color_message_key,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            # Processors only used for the JSON renderer
            (
                [
                    rename_event_key,
                    # Format the exception only for JSON logs, as we want to pretty-print them when using the ConsoleRenderer
                    structlog.processors.format_exc_info,
                ]
                if json_logs
                else []
            ),
        ]
    )

    # Main structlog configuration
    structlog.configure(
        processors=[
            *shared_processors,
            # Prepare event dict for `ProcessorFormatter`.
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    log_renderer: structlog.types.Processor
    if json_logs:
        import orjson

        log_renderer = structlog.processors.JSONRenderer(serializer=orjson.dumps)
    else:
        log_renderer = structlog.dev.ConsoleRenderer()

    formatter = structlog.stdlib.ProcessorFormatter(
        # These run ONLY on `logging` entries that do NOT originate within structlog.
        foreign_pre_chain=shared_processors,
        # These run on ALL entries after the pre_chain is done.
        processors=[
            # Remove _record & _from_structlog.
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            log_renderer,
            # required with orjson
            *([decode_bytes] if json_logs else []),  # type: ignore
        ],
    )

    handler = logging.StreamHandler()
    # Use OUR `ProcessorFormatter` to format all `logging` entries.
    handler.setFormatter(formatter)
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level.upper())

    def configure_logger(
        name: str,
        level: Optional[str] = None,
        clear: Optional[bool] = None,
        propagate: Optional[bool] = None,
    ) -> None:
        """Helper function to configure a logger with the given parameters."""
        logger = logging.getLogger(name)

        if level is not None:
            logger.setLevel(level.upper())

        if clear is True:
            logger.handlers.clear()

        if propagate is not None:
            logger.propagate = propagate

    # Clear the log handlers for uvicorn loggers, and enable propagation
    # so the messages are caught by our root logger and formatted correctly
    # by structlog
    configure_logger("uvicorn", clear=True, propagate=True)
    configure_logger("uvicorn.error", clear=True, propagate=True)

    # Disable the apscheduler loggers, as they are too verbose
    # TODO: This should be configurable easily from a TOML or YAML file
    configure_logger("apscheduler.executors.default", level="WARNING")
    configure_logger("apscheduler.scheduler", level="WARNING")

    # Since we re-create the access logs ourselves, to add all information
    # in the structured log (see the `logging_middleware` in main.py), we clear
    # the handlers and prevent the logs to propagate to a logger higher up in the
    # hierarchy (effectively rendering them silent).
    configure_logger("uvicorn.access", clear=True, propagate=False)

    def handle_exception(exc_type, exc_value, exc_traceback):
        """
        Log any uncaught exception instead of letting it be printed by Python
        (but leave KeyboardInterrupt untouched to allow users to Ctrl+C to stop)
        See https://stackoverflow.com/a/16993115/3641865
        """
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        root_logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

    sys.excepthook = handle_exception
