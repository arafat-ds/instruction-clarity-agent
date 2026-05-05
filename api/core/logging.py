"""
core/logging.py — Structured logging configuration.
"""

import logging
import sys


def setup_logging(debug: bool = False) -> None:
    """
    Configure root logger with structured format.
    Outputs to stdout — suitable for container environments.
    """
    level = logging.DEBUG if debug else logging.INFO

    fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    datefmt = "%Y-%m-%dT%H:%M:%S"

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(fmt=fmt, datefmt=datefmt))

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers = [handler]

    # Suppress noisy third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
