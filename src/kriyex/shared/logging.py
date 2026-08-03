"""
Central logging configuration for KRIYEX.
"""

from __future__ import annotations

import logging
from pathlib import Path


LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"


def configure_logging() -> None:
    """
    Configure application logging.

    Creates:
    - Console logger
    - File logger
    """

    log_directory = Path.home() / ".kriyex" / "logs"
    log_directory.mkdir(parents=True, exist_ok=True)

    log_file = log_directory / "kriyex.log"

    logging.basicConfig(
        level=logging.INFO,
        format=LOG_FORMAT,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file, encoding="utf-8"),
        ],
        force=True,
    )

    logger = logging.getLogger("kriyex")
    logger.info("=" * 60)
    logger.info("KRIYEX logging initialized.")
    logger.info("=" * 60)