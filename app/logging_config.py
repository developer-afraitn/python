# app/logging_config.py
import logging
import sys
import json
import structlog
import os
from collections import OrderedDict


def setup_logging() -> None:
    level = os.getenv("LOG_LEVEL", "INFO").upper()

    logging.basicConfig(
        level=getattr(logging, level, logging.INFO),
        format="%(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    def reorder_event_first(_, __, event_dict):
        """
        Ensure 'event' key is the first key in JSON output
        """
        if "event" in event_dict:
            return OrderedDict(
                [("event", event_dict.pop("event"))] + list(event_dict.items())
            )
        return event_dict

    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso", key="timestamp"),
            structlog.processors.add_log_level,
            reorder_event_first,  # ⭐ این مهمه
            structlog.processors.JSONRenderer(
                serializer=lambda obj, **kw: json.dumps(
                    obj,
                    ensure_ascii=False,
                    **kw,
                )
            ),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = "app"):
    return structlog.get_logger(name)
