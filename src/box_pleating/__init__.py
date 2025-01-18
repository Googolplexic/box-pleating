"""
Box Pleating Pattern Module

This module provides tools for creating and validating box-pleating origami patterns.
Box pleating is a tessellation technique where all creases are at 45° or 90° angles
to each other, forming a grid-like pattern.
"""

import logging
from typing import Optional

# Configure package-level logger
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())  # Default null handler


def configure_logger(level: Optional[int] = None) -> None:
    """
    Configure the box pleating package logger.

    Args:
        level: Optional logging level to set (e.g., logging.DEBUG)
              If not provided, defaults to logging.INFO
    """
    if level is None:
        level = logging.INFO

    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)

    logger = logging.getLogger(__name__)
    logger.addHandler(handler)
    logger.setLevel(level)


from .models import Point, Crease, CreaseType
from .pattern import BoxPleatingPattern

__all__ = ["Point", "Crease", "CreaseType", "BoxPleatingPattern", "configure_logger"]

__version__ = "1.0.1"
