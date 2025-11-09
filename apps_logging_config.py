
import logging
import logging.config
from typing import Dict

DEFAULT_LOG_LEVEL = "INFO"

LOGGING_CONFIG: Dict = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s %(levelname)s [%(name)s] %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "detailed": {
            "format": "%(asctime)s %(levelname)s [%(name)s] %(message)s (%(filename)s:%(lineno)d)",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": DEFAULT_LOG_LEVEL,
            "stream": "ext://sys.stdout",
        },
        "debug_file": {
            "class": "logging.FileHandler",
            "formatter": "detailed",
            "level": "DEBUG",
            "filename": "logs/debug.log",
            "mode": "a",
            "encoding": "utf-8",
        },
    },
    "loggers": {
        # Application namespaces
        "": {"handlers": ["console"], "level": DEFAULT_LOG_LEVEL, "propagate": False},
        "apps": {"handlers": ["console"], "level": DEFAULT_LOG_LEVEL, "propagate": False},
        # Third party libs you may want quieter output from
        "uvicorn": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "sqlalchemy": {"handlers": ["console"], "level": "WARN", "propagate": False},
        "openai": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "twilio": {"handlers": ["console"], "level": "INFO", "propagate": False},
    },
    "root": {"handlers": ["console"], "level": DEFAULT_LOG_LEVEL},
}

def configure_logging(debug: bool = False, enable_file: bool = False) -> None:
    """
    Apply logging configuration for the app.

    - debug: if True, set verbose DEBUG levels for key modules.
    - enable_file: if True, add file handler (logs/debug.log). Ensure logs/ exists or create it.
    """
    cfg = LOGGING_CONFIG.copy()

    if enable_file:
        # ensure the file handler is enabled
        if "debug_file" not in cfg["handlers"]:
            pass
        # attach the file handler to root and 'apps'
        cfg["handlers"] = dict(cfg["handlers"])
        cfg["handlers"]["debug_file"] = LOGGING_CONFIG["handlers"]["debug_file"]
        cfg["loggers"][""] = dict(cfg["loggers"][""])
        cfg["loggers"][""]["handlers"] = ["console", "debug_file"]
        cfg["loggers"]["apps"]["handlers"] = ["console", "debug_file"]

    logging.config.dictConfig(cfg)

    if debug:
        # More verbose for development
        logging.getLogger("apps").setLevel(logging.DEBUG)
        logging.getLogger("apps.conversation.gpt_dialogue_manager").setLevel(logging.DEBUG)
        logging.getLogger("apps.telephony.webhooks").setLevel(logging.DEBUG)
        logging.getLogger("openai").setLevel(logging.DEBUG)
