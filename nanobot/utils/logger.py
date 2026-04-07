"""Unified loguru configuration for NanoBot.

This module provides centralized logging configuration using loguru.
All modules should import logger from this module instead of configuring their own.

Usage:
    from nanobot.utils.logger import logger
    
    logger.info("Hello, {}!", "world")
    logger.error("Error occurred: {}", error_msg)
"""
import os
import sys
from pathlib import Path
from loguru import logger as _logger


def get_log_dir() -> Path:
    """Get the log directory path."""
    # Check environment variable first
    log_dir = os.environ.get('NANOBOT_LOG_DIR')
    if log_dir:
        path = Path(log_dir)
    else:
        # Default to ~/.nanobot/logs
        home = Path.home()
        path = home / '.nanobot' / 'logs'
    
    path.mkdir(parents=True, exist_ok=True)
    return path


def setup_logger(
    level: str = "INFO",
    rotation: str = "10 MB",
    retention: str = "7 days",
    compression: str = "zip",
    format: str | None = None,
    colorize: bool = True,
    backtrace: bool = True,
    diagnose: bool = False,
    log_to_file: bool = True,
    log_to_console: bool = True,
) -> None:
    """Configure loguru logger with unified settings.
    
    Args:
        level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        rotation: When to rotate log files (e.g., "10 MB", "1 day", "00:00")
        retention: How long to keep old logs (e.g., "7 days", "1 month")
        compression: Compression format for old logs ("zip", "gz", or None)
        format: Custom log format (None for default format)
        colorize: Whether to colorize console output
        backtrace: Show full traceback on errors
        diagnose: Show local variables in tracebacks (security risk in production)
        log_to_file: Enable file logging
        log_to_console: Enable console logging
    """
    # Remove default handler
    _logger.remove()
    
    # Default format
    if format is None:
        format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )
    
    # Simplified format for console
    console_format = (
        "<green>{time:HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<level>{message}</level>"
    )
    
    # File format (no colors)
    file_format = (
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
        "{level: <8} | "
        "{name}:{function}:{line} | "
        "{message}"
    )
    
    # Add console handler
    if log_to_console:
        _logger.add(
            sys.stderr,
            format=console_format,
            level=level,
            colorize=colorize,
            backtrace=backtrace,
            diagnose=diagnose,
        )
    
    # Add file handler
    if log_to_file:
        log_dir = get_log_dir()
        log_path = log_dir / "nanobot_{time:YYYY-MM-DD}.log"
        
        _logger.add(
            log_path,
            format=file_format,
            level=level,
            rotation=rotation,
            retention=retention,
            compression=compression,
            backtrace=backtrace,
            diagnose=diagnose,
            encoding="utf-8",
        )
    
    # Catch unhandled exceptions
    _logger.add(
        sys.stderr,
        format=format,
        level="ERROR",
        backtrace=backtrace,
        diagnose=diagnose,
        filter=lambda record: record["level"].name == "CRITICAL"
    )


# Initialize logger with default settings
setup_logger()

# Export the configured logger instance
logger = _logger


def get_logger(name: str | None = None):
    """Get a logger instance with optional custom name.
    
    Args:
        name: Optional logger name (usually module name)
        
    Returns:
        Configured logger instance
        
    Example:
        logger = get_logger(__name__)
        logger.info("Message from module")
    """
    if name:
        return logger.bind(name=name)
    return logger


__all__ = ['logger', 'get_logger', 'setup_logger']
