import logging
import sys
from typing import List

import structlog
from structlog.stdlib import ProcessorFormatter
from structlog.types import Processor

shared_processors: List[Processor] = [
    structlog.stdlib.add_log_level,
    structlog.processors.CallsiteParameterAdder(
        {
            structlog.processors.CallsiteParameter.MODULE,
            structlog.processors.CallsiteParameter.FILENAME,
            structlog.processors.CallsiteParameter.LINENO,
        }
    ),
    structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S.%f"),
]

structlog_processors = shared_processors + []
# Remove _record & _from_structlog.
logging_processors: List[Processor] = [ProcessorFormatter.remove_processors_meta]

if sys.stderr.isatty():
    console_renderer = structlog.dev.ConsoleRenderer()
    logging_processors.append(console_renderer)
    structlog_processors.append(console_renderer)
else:
    json_renderer = structlog.processors.JSONRenderer(indent=1, sort_keys=True)
    structlog_processors.append(json_renderer)
    logging_processors.append(json_renderer)

structlog.configure(
    processors=structlog_processors,
    wrapper_class=structlog.stdlib.BoundLogger,
    # logger_factory=structlog.stdlib.LoggerFactory(),
    logger_factory=structlog.PrintLoggerFactory(sys.stderr),
    context_class=dict,
    cache_logger_on_first_use=True,
)


formatter = ProcessorFormatter(
    # These run ONLY on `logging` entries that do NOT originate within
    # structlog.
    foreign_pre_chain=shared_processors,
    # These run on ALL entries after the pre_chain is done.
    processors=logging_processors,
)

handler = logging.StreamHandler(sys.stderr)
# Use OUR `ProcessorFormatter` to format all `logging` entries.
handler.setFormatter(formatter)
logging.basicConfig(handlers=[handler], level=logging.INFO)

external_loggers = ["uvicorn.error", "uvicorn.access"]
for logger_name in external_loggers:
    logger = logging.getLogger(logger_name)
    logger.handlers = [handler]
    logger.propagate = False
