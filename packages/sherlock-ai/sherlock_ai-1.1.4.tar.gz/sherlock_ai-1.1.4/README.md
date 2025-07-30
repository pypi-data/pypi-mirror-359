# Sherlock AI

A Python package for performance monitoring and logging utilities that helps you track execution times and debug your applications with ease.

## Features

- 🎯 **Performance Decorators**: Easy-to-use decorators for tracking function execution times
- ⏱️ **Context Managers**: Monitor code block execution with simple context managers
- 🔧 **Advanced Configuration System**: Complete control over logging with dataclass-based configuration
- 🎛️ **Configuration Presets**: Pre-built setups for development, production, and testing environments
- 🔄 **Async/Sync Support**: Works seamlessly with both synchronous and asynchronous functions
- 📊 **Request Tracking**: Built-in request ID tracking for distributed systems
- 📁 **Flexible Log Management**: Enable/disable log files, custom directories, and rotation settings
- 🏷️ **Logger Name Constants**: Easy access to available logger names with autocomplete support
- 🔍 **Logger Discovery**: Programmatically discover available loggers in your application
- 🐛 **Development-Friendly**: Optimized for FastAPI auto-reload and development environments
- 🚀 **Zero Dependencies**: Lightweight with minimal external dependencies

## Installation

```bash
pip install sherlock-ai
```

## Quick Start

### Basic Setup

```python
from sherlock_ai import setup_logging, get_logger, log_performance
import time

# Initialize logging (call once at application startup)
setup_logging()

# Get a logger for your module
logger = get_logger(__name__)

@log_performance
def my_function():
    # Your code here
    try:
        time.sleep(1)
        logger.info("Processing completed")
        return "result"
    except Exception as e:
        logger.error(f"Error: {e}")
        raise

# This will log: PERFORMANCE | my_module.my_function | SUCCESS | 1.003s
result = my_function()
```

### Using Logger Name Constants

```python
from sherlock_ai import setup_logging, get_logger, LoggerNames, list_available_loggers

# Initialize logging
setup_logging()

# Use predefined logger names with autocomplete support
api_logger = get_logger(LoggerNames.API)
db_logger = get_logger(LoggerNames.DATABASE)
service_logger = get_logger(LoggerNames.SERVICES)

# Discover available loggers programmatically
available_loggers = list_available_loggers()
print(f"Available loggers: {available_loggers}")

# Use the loggers
api_logger.info("API request received")        # → logs/api.log
db_logger.info("Database query executed")     # → logs/database.log
service_logger.info("Service operation done") # → logs/services.log
```

### Advanced Configuration

```python
@log_performance(min_duration=0.1, include_args=True, log_level="DEBUG")
def slow_database_query(user_id, limit=10):
    # Only logs if execution time >= 0.1 seconds
    # Includes function arguments in the log
    pass
```

### Context Manager for Code Blocks

```python
from sherlock_ai.performance import PerformanceTimer

with PerformanceTimer("database_operation"):
    # Your code block here
    result = database.query("SELECT * FROM users")
    
# Logs: PERFORMANCE | database_operation | SUCCESS | 0.234s
```

### Async Function Support

```python
@log_performance
async def async_api_call():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com")
        return response.json()

# Works automatically with async functions
result = await async_api_call()
```

### Manual Time Logging

```python
from sherlock_ai.performance import log_execution_time
import time

start_time = time.time()
try:
    # Your code here
    result = complex_operation()
    log_execution_time("complex_operation", start_time, success=True)
except Exception as e:
    log_execution_time("complex_operation", start_time, success=False, error=str(e))
```

## Advanced Configuration

### Configuration Presets

```python
from sherlock_ai import setup_logging, LoggingPresets

# Development environment - debug level logging
setup_logging(LoggingPresets.development())

# Production environment - optimized performance
setup_logging(LoggingPresets.production())

# Minimal setup - only basic app logs
setup_logging(LoggingPresets.minimal())

# Performance monitoring only
setup_logging(LoggingPresets.performance_only())
```

### Custom Configuration

```python
from sherlock_ai import setup_logging, LoggingConfig, LogFileConfig, LoggerConfig

# Create completely custom configuration
config = LoggingConfig(
    logs_dir="my_app_logs",
    console_level="DEBUG",
    log_files={
        "application": LogFileConfig("my_app_logs/app.log", max_bytes=50*1024*1024),
        "errors": LogFileConfig("my_app_logs/errors.log", level="ERROR"),
        "performance": LogFileConfig("my_app_logs/perf.log"),
        "custom": LogFileConfig("my_app_logs/custom.log", backup_count=10)
    },
    loggers={
        "api": LoggerConfig("mycompany.api", log_files=["application", "custom"]),
        "database": LoggerConfig("mycompany.db", log_files=["application"]),
        "performance": LoggerConfig("PerformanceLogger", log_files=["performance"], propagate=False)
    }
)

setup_logging(config)
```

### Flexible Log Management

```python
from sherlock_ai import LoggingConfig

# Start with default configuration
config = LoggingConfig()

# Disable specific log files
config.log_files["api"].enabled = False
config.log_files["services"].enabled = False

# Change log levels
config.log_files["performance"].level = "DEBUG"
config.console_level = "WARNING"

# Modify file sizes and rotation
config.log_files["app"].max_bytes = 100 * 1024 * 1024  # 100MB
config.log_files["app"].backup_count = 15

# Apply the modified configuration
setup_logging(config)
```

### Custom File Names and Directories

```python
from sherlock_ai import LoggingPresets

# Use custom file names
config = LoggingPresets.custom_files({
    "app": "logs/application.log",
    "performance": "logs/metrics.log",
    "errors": "logs/error_tracking.log"
})

setup_logging(config)
```

### Environment-Specific Configuration

```python
import os
from sherlock_ai import setup_logging, LoggingPresets, LoggingConfig

# Configure based on environment
env = os.getenv("ENVIRONMENT", "development")

if env == "production":
    setup_logging(LoggingPresets.production())
elif env == "development":
    setup_logging(LoggingPresets.development())
elif env == "testing":
    config = LoggingConfig(
        logs_dir="test_logs",
        console_enabled=False,  # No console output during tests
        log_files={"test_results": LogFileConfig("test_logs/results.log")}
    )
    setup_logging(config)
else:
    setup_logging()  # Default configuration
```

### Development with FastAPI

The package is optimized for FastAPI development with auto-reload enabled:

```python
# main.py
from sherlock_ai import setup_logging
import uvicorn

if __name__ == "__main__":
    # Set up logging once in the main entry point
    setup_logging()
    
    # FastAPI auto-reload won't cause duplicate log entries
    uvicorn.run(
        "myapp.api:app",
        host="127.0.0.1",
        port=8000,
        reload=True  # ✅ Safe to use - no duplicate logs
    )
```

```python
# myapp/api.py
from fastapi import FastAPI
from sherlock_ai import get_logger, LoggerNames

# Don't call setup_logging() here - it's already done in main.py
app = FastAPI()
logger = get_logger(LoggerNames.API)

@app.get("/health")
def health_check():
    logger.info("Health check requested")
    return {"status": "healthy"}
```

## API Reference

### `@log_performance` Decorator

Parameters:
- `min_duration` (float): Only log if execution time >= this value in seconds (default: 0.0)
- `include_args` (bool): Whether to include function arguments in the log (default: False)
- `log_level` (str): Log level to use - INFO, DEBUG, WARNING, etc. (default: "INFO")

### `PerformanceTimer` Context Manager

Parameters:
- `name` (str): Name identifier for the operation
- `min_duration` (float): Only log if execution time >= this value in seconds (default: 0.0)

### `log_execution_time` Function

Parameters:
- `name` (str): Name identifier for the operation
- `start_time` (float): Start time from `time.time()`
- `success` (bool): Whether the operation succeeded (default: True)
- `error` (str): Error message if operation failed (default: None)

### Configuration Classes

#### `LoggingConfig`

Main configuration class for the logging system.

Parameters:
- `logs_dir` (str): Directory for log files (default: "logs")
- `log_format` (str): Log message format string
- `date_format` (str): Date format for timestamps
- `console_enabled` (bool): Enable console output (default: True)
- `console_level` (Union[str, int]): Console log level (default: INFO)
- `root_level` (Union[str, int]): Root logger level (default: INFO)
- `log_files` (Dict[str, LogFileConfig]): Log file configurations
- `loggers` (Dict[str, LoggerConfig]): Logger configurations
- `external_loggers` (Dict[str, Union[str, int]]): External library log levels

#### `LogFileConfig`

Configuration for individual log files.

Parameters:
- `filename` (str): Path to the log file
- `level` (Union[str, int]): Log level for this file (default: INFO)
- `max_bytes` (int): Maximum file size before rotation (default: 10MB)
- `backup_count` (int): Number of backup files to keep (default: 5)
- `encoding` (str): File encoding (default: "utf-8")
- `enabled` (bool): Whether this log file is enabled (default: True)

#### `LoggerConfig`

Configuration for individual loggers.

Parameters:
- `name` (str): Logger name
- `level` (Union[str, int]): Logger level (default: INFO)
- `log_files` (List[str]): List of log file names this logger writes to
- `propagate` (bool): Whether to propagate to parent loggers (default: True)
- `enabled` (bool): Whether this logger is enabled (default: True)

### Configuration Presets

#### `LoggingPresets.minimal()`
Basic setup with only console and app log.

#### `LoggingPresets.development()`
Debug-level logging for development environment.

#### `LoggingPresets.production()`
Optimized configuration for production use.

#### `LoggingPresets.performance_only()`
Only performance monitoring logs.

#### `LoggingPresets.custom_files(file_configs)`
Custom file names for standard log types.

Parameters:
- `file_configs` (Dict[str, str]): Mapping of log type to custom filename

### Logger Constants and Discovery

#### `LoggerNames`
Class containing constants for available logger names.

Available constants:
- `LoggerNames.API` - API logger name
- `LoggerNames.DATABASE` - Database logger name  
- `LoggerNames.SERVICES` - Services logger name
- `LoggerNames.PERFORMANCE` - Performance logger name

#### `list_available_loggers()`
Function to discover all available logger names.

Returns:
- `List[str]`: List of all available logger names

Example:
```python
from sherlock_ai import LoggerNames, list_available_loggers

# Use constants with autocomplete
logger = get_logger(LoggerNames.API)

# Discover available loggers
loggers = list_available_loggers()
print(f"Available: {loggers}")
```

## Configuration

### Basic Logging Setup

```python
from sherlock_ai import setup_logging, get_logger

# Initialize logging (call once at application startup)
setup_logging()

# Get a logger for your module
logger = get_logger(__name__)

# Use the logger
logger.info("Application started")
logger.error("Something went wrong")
```

**Default Log Files Created:**
When you call `setup_logging()` with no arguments, it automatically creates a `logs/` directory with these files:
- `app.log` - All INFO+ level logs from root logger
- `errors.log` - Only ERROR+ level logs from any logger
- `api.log` - Logs from `app.api` logger (empty unless you use this logger)
- `database.log` - Logs from `app.core.dbConnection` logger
- `services.log` - Logs from `app.services` logger  
- `performance.log` - Performance monitoring logs from your `@log_performance` decorators

### Using Specific Loggers

```python
import logging
from sherlock_ai import setup_logging

setup_logging()

# Use specific loggers to populate their respective log files
api_logger = logging.getLogger("app.api")
db_logger = logging.getLogger("app.core.dbConnection")
services_logger = logging.getLogger("app.services")

# These will go to their specific log files
api_logger.info("API request received")           # → api.log
db_logger.info("Database query executed")        # → database.log
services_logger.info("Service operation done")   # → services.log
```

### Request ID Tracking

```python
from sherlock_ai.utils.helper import get_request_id, set_request_id

# Set a request ID for the current context
request_id = set_request_id("req-12345")

# Get current request ID for distributed tracing
current_id = get_request_id()
```

### Complete Application Example

```python
from sherlock_ai import setup_logging, get_logger, log_performance, PerformanceTimer

# Initialize logging first
setup_logging()
logger = get_logger(__name__)

@log_performance
def main():
    logger.info("Application starting")
    
    with PerformanceTimer("initialization"):
        # Your initialization code
        pass
    
    logger.info("Application ready")

if __name__ == "__main__":
    main()
```

## Log Output Format

The package produces structured log messages in the following format:

```
PERFORMANCE | {function_name} | {STATUS} | {execution_time}s | {additional_info}
```

Examples:
```
PERFORMANCE | my_module.my_function | SUCCESS | 0.123s
PERFORMANCE | api_call | ERROR | 2.456s | Connection timeout
PERFORMANCE | database_query | SUCCESS | 0.089s | Args: ('user123',) | Kwargs: {'limit': 10}
```

## Use Cases

- **API Performance Monitoring**: Track response times for your web APIs with dedicated API logging
- **Database Query Optimization**: Monitor slow database operations with separate database logs
- **Microservices Debugging**: Trace execution times across service boundaries with request ID tracking
- **Algorithm Benchmarking**: Compare performance of different implementations using custom configurations
- **Production Monitoring**: Get insights into your application's performance characteristics with production presets
- **Environment-Specific Logging**: Use different configurations for development, testing, and production
- **Custom Log Management**: Create application-specific log files and directory structures
- **Compliance & Auditing**: Separate error logs and performance logs for security and compliance requirements
- **DevOps Integration**: Configure logging for containerized environments and CI/CD pipelines
- **FastAPI Development**: Optimized for FastAPI auto-reload with no duplicate log entries during development
- **Logger Organization**: Use predefined logger names with autocomplete support for better code maintainability

## Requirements

- Python >= 3.8
- Standard library only (no external dependencies)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Links

- **Homepage**: [https://github.com/pranawmishra/sherlock-ai](https://github.com/pranawmishra/sherlock-ai)
- **Repository**: [https://github.com/pranawmishra/sherlock-ai](https://github.com/pranawmishra/sherlock-ai)
- **Issues**: [https://github.com/pranawmishra/sherlock-ai/issues](https://github.com/pranawmishra/sherlock-ai/issues)