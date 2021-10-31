import logging
import logging.config
import structlog
from typing import Any, MutableMapping, Tuple
from starlette_context import context


shared_processors: Tuple[structlog.types.Processor, ...] = (
    structlog.stdlib.add_logger_name,
    structlog.stdlib.add_log_level,
    structlog.processors.TimeStamper(fmt="iso"),
)

logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.processors.JSONRenderer(),
            "foreign_pre_chain": shared_processors,
        }
    },
    "handlers": {
        "default": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "json",
        }
    },
    "loggers": {
        "": {
            "handlers": ["default"], 
            "level": "INFO"
        },
        "uvicorn.error": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": ["default"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}

def setup_logging(log_level: str) -> None:
    def add_app_context(logger: logging.Logger, method_name: str, event_dict: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        if context.exists():
            event_dict.update(context.data)

        return event_dict

    structlog.configure(
        processors=[
            add_app_context,
            structlog.stdlib.filter_by_level,
            *shared_processors,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.UnicodeDecoder(),
            structlog.processors.format_exc_info,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    logging_config["loggers"][""]["level"] = log_level
    logging.config.dictConfig(logging_config)


def get_logger(mod_name: str) -> structlog.stdlib.BoundLogger:
    """To use this, do logger = get_logger(__name__)

    Parameters
    ----------
    mod_name : str
        Module name

    Returns
    -------
    Logger:
        Logger instance
    """
    logger: structlog.stdlib.BoundLogger = structlog.getLogger(mod_name)
    return logger