"""
nanobot - A lightweight AI agent framework
"""

__version__ = "0.1.4.post6"
__logo__ = "🐈"
# Initialize loguru logger
from nanobot.utils.logger import logger, setup_logger

# Auto-setup logger on import (can be overridden by calling setup_logger())
setup_logger()

__all__ = ['__version__', '__logo__', 'logger', 'setup_logger']