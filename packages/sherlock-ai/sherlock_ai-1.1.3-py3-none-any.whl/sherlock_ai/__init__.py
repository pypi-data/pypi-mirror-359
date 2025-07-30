"""
Sherlock AI - Your AI assistant package
"""

__version__ = "1.1.3"
# __author__ = "Pranaw Mishra"
# __email__ = "pranawmishra73@gmail.com"

# Import main components for easy access
from .performance import log_performance, PerformanceTimer
from .logging_config import setup_logging, get_logger
from .config import LoggingConfig, LoggingPresets, LogFileConfig, LoggerConfig

__all__ = [
    "log_performance", 
    "PerformanceTimer",
    "setup_logging",
    "get_logger",
    "LoggingConfig",
    "LoggingPresets",
    "LogFileConfig",
    "LoggerConfig",
    "__version__"
]