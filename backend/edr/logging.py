"""
EDR System Logging Configuration
=================================

Provides centralized logging configuration for all EDR components
with support for file, console, and structured logging.
"""

from __future__ import annotations

import logging
import logging.handlers
from pathlib import Path
from typing import Optional

from backend.edr.config.settings import LOG_DIR, ensure_directories


class EDRLogger:
    """Centralized logging configuration for EDR system."""

    _loggers: dict[str, logging.Logger] = {}

    @classmethod
    def configure(
        cls,
        name: str,
        level: int = logging.INFO,
        log_file: Optional[str] = None,
        console: bool = True,
    ) -> logging.Logger:
        """
        Configure and return a logger for the specified component.

        Args:
            name: Logger name (typically module name)
            level: Logging level (default: INFO)
            log_file: Optional log file name (will be in LOG_DIR)
            console: Whether to output to console (default: True)

        Returns:
            Configured logger instance
        """
        if name in cls._loggers:
            return cls._loggers[name]

        # Create logger
        logger = logging.getLogger(name)
        logger.setLevel(level)

        # Prevent duplicate handlers
        logger.handlers.clear()

        # Format
        formatter = logging.Formatter(
            "%(asctime)s | %(name)s | %(levelname)-8s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Console handler
        if console:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        # File handler
        if log_file:
            ensure_directories()
            log_path = LOG_DIR / log_file
            file_handler = logging.handlers.RotatingFileHandler(
                log_path,
                maxBytes=10 * 1024 * 1024,  # 10 MB
                backupCount=5,
            )
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        cls._loggers[name] = logger
        return logger

    @classmethod
    def get(cls, name: str) -> logging.Logger:
        """Get existing logger or create default one."""
        if name not in cls._loggers:
            return cls.configure(name)
        return cls._loggers[name]

    @classmethod
    def configure_all(cls) -> None:
        """Configure all component loggers."""
        ensure_directories()

        # Core components
        cls.configure("edr.agent", logging.INFO, "agent.log")
        cls.configure("edr.detection", logging.INFO, "detection.log")
        cls.configure("edr.response", logging.INFO, "response.log")
        cls.configure("edr.pipeline", logging.INFO, "pipeline.log")
        cls.configure("edr.storage", logging.INFO, "storage.log")
        cls.configure("edr.service", logging.INFO, "service.log")
        cls.configure("edr.api", logging.INFO, "api.log")

        # Root EDR logger
        cls.configure("edr", logging.INFO, "edr.log")


# Convenience functions
def get_logger(name: str) -> logging.Logger:
    """Get or create a logger."""
    return EDRLogger.get(name)


def configure_logging() -> None:
    """Configure all EDR logging."""
    EDRLogger.configure_all()
