"""
Sherlock AI - Your AI assistant package
"""

__version__ = "1.1.4"
# __author__ = "Pranaw Mishra"
# __email__ = "pranawmishra73@gmail.com"

# Import main components for easy access
from .performance import log_performance, PerformanceTimer
from .logging_setup import setup_logging, get_logger
from .config import LoggingConfig, LoggingPresets, LogFileConfig, LoggerConfig
from .utils import set_request_id, get_request_id, clear_request_id

# ✅ Logger name constants 
class LoggerNames:
    """Available logger names for use with get_logger()"""
    API = "ApiLogger"
    DATABASE = "DatabaseLogger"
    SERVICES = "ServiceLogger"
    PERFORMANCE = "PerformanceLogger"

# ✅ Convenience function
def list_available_loggers():
    """Get list of all available logger names"""
    return [
        LoggerNames.API,
        LoggerNames.DATABASE,
        LoggerNames.SERVICES,
        LoggerNames.PERFORMANCE
    ]

__all__ = [
    "log_performance", 
    "PerformanceTimer",
    "setup_logging",
    "get_logger",
    "LoggingConfig",
    "LoggingPresets",
    "LogFileConfig",
    "LoggerConfig",
    "set_request_id",
    "get_request_id",
    "clear_request_id",
    "LoggerNames",
    "list_available_loggers",
    "__version__",
]