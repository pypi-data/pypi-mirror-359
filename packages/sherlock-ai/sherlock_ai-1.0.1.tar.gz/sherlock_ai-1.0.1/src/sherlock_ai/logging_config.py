# app > core > logging_config.py
import logging
import logging.handlers
from pathlib import Path
from sherlock_ai.utils.helper import request_id_var

class RequestIdFormatter(logging.Formatter):
    """Custom formatter that includes request ID in log messages"""

    def format(self, record):
        """Add request ID to log message"""
        # get current request ID from context
        record.request_id = request_id_var.get("") or "-"
        return super().format(record)


def setup_logging():
    """Set up logging configuration for the application with request ID support"""

    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Configure logging format
    log_format = "%(asctime)s - %(request_id)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # Create custom formatter with request ID support
    formatter = RequestIdFormatter(log_format, datefmt=date_format)

    # Clear existing handlers to avoid duplicates
    logging.root.handlers.clear()

    # 1. Console Handler - prints to terminal
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # 2. Main App Log - all logs INFO and above
    app_handler = logging.handlers.RotatingFileHandler(
        "logs/app.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    app_handler.setLevel(logging.INFO)
    app_handler.setFormatter(formatter)

    # 3. Error Log - only ERROR and CRITICAL logs
    error_handler = logging.handlers.RotatingFileHandler(
        "logs/errors.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    # 4. API Log - specifically for API-related logs
    api_handler = logging.handlers.RotatingFileHandler(
        "logs/api.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    api_handler.setLevel(logging.INFO)
    api_handler.setFormatter(formatter)

    # 5. Database Log - specifically for database operations
    db_handler = logging.handlers.RotatingFileHandler(
        "logs/database.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    db_handler.setLevel(logging.INFO)
    db_handler.setFormatter(formatter)

    # 6. Services Log - for all service-related operations
    services_handler = logging.handlers.RotatingFileHandler(
        "logs/services.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    services_handler.setLevel(logging.INFO)
    services_handler.setFormatter(formatter)

    # 7. Performance Log - specifically for performance metrics
    performance_handler = logging.handlers.RotatingFileHandler(
        "logs/performance.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    performance_handler.setLevel(logging.INFO)
    performance_handler.setFormatter(formatter)

    # Configure root logger with console, main app, and error handlers
    logging.root.setLevel(logging.INFO)
    logging.root.addHandler(console_handler)
    logging.root.addHandler(app_handler)
    logging.root.addHandler(error_handler)

    # Configure specific loggers for different components
    # API loggers - all API modules will log to api.log
    api_logger = logging.getLogger("app.api")
    api_logger.setLevel(logging.INFO)
    api_logger.addHandler(api_handler)

    # Database loggers - all database operations will log to database.log
    db_logger = logging.getLogger("app.core.dbConnection")
    db_logger.setLevel(logging.INFO)
    db_logger.addHandler(db_handler)

    # Services loggers - all services will log to services.log
    services_logger = logging.getLogger("app.services")
    services_logger.setLevel(logging.INFO)
    services_logger.addHandler(services_handler)

    # Performance loggers - all performance metrics will log to performance.log
    performance_logger = logging.getLogger("PerformanceLogger")
    performance_logger.setLevel(logging.INFO)
    performance_logger.addHandler(performance_handler)

    # Set specific log levels for external libraries
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)

    # Prevent duplicate logs (don't propagate to parent if already handled)
    api_logger.propagate = True  # Still propagate to get in main app.log
    db_logger.propagate = True
    services_logger.propagate = True
    performance_logger.propagate = False

# Helper function to get logger (optional, but clean)
def get_logger(name: str = None):
    """Get a logger. If no name provided, uses the caller's __name__."""
    return logging.getLogger(name) if name else logging.getLogger(__name__)


# setup_logging()
