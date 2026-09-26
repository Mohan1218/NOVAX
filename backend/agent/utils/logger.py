"""
Structured logging helper for the agent.

Usage::

    from backend.agent.utils.logger import get_logger
    log = get_logger(__name__)
    log.info("Agent started", extra={"iteration": 1})
"""

from __future__ import annotations

import logging
import sys


def get_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Return a logger with a clean, human-readable console format.

    Parameters
    ----------
    name : str
        Logger name (typically ``__name__``).
    level : str
        Minimum severity (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        logger.addHandler(handler)

    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    return logger
