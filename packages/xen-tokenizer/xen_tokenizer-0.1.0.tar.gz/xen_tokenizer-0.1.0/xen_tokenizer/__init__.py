"""
XenTokeniser - XenArcAI's High-Performance Tokenization Library

A fast, efficient, and feature-rich tokenizer optimized for XenArcAI's NLP pipelines.
Built on top of Hugging Face's Transformers with additional optimizations and features.
"""

# Core components
from .tokenizer import XenTokenizerFast
from .processor import AzureParquetProcessor
from .config import TokenizerConfig

# Version information
from .version import __version__, __version_info__

# Public API
__all__ = [
    # Main classes
    "XenTokenizerFast",
    "AzureParquetProcessor",
    "TokenizerConfig",
    
    # Version info
    "__version__",
    "__version_info__",
]

# Set default logging
import logging
from typing import Optional

# Configure package-level logger
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

def enable_logging(level: int = logging.INFO) -> None:
    """Enable logging for the XenTokeniser package.
    
    Args:
        level: Logging level (default: logging.INFO)
    """
    logger = logging.getLogger(__name__)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(level)

# Set up package resources
try:
    # Import package resources if needed
    import pkg_resources
    __resource_path__ = pkg_resources.resource_filename(__name__, "")
except ImportError:
    __resource_path__ = None

# Initialize package
__initialized__ = False

def _initialize() -> None:
    """Initialize package resources and configurations."""
    global __initialized__
    if not __initialized__:
        # Add any package initialization code here
        __initialized__ = True

# Initialize the package when imported
_initialize()