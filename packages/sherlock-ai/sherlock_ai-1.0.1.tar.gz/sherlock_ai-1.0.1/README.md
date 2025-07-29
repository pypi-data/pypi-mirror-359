# Sherlock AI

A Python package for performance monitoring and logging utilities that helps you track execution times and debug your applications with ease.

## Features

- 🎯 **Performance Decorators**: Easy-to-use decorators for tracking function execution times
- ⏱️ **Context Managers**: Monitor code block execution with simple context managers
- 🔧 **Flexible Configuration**: Customizable logging levels, minimum duration thresholds, and argument logging
- 🔄 **Async/Sync Support**: Works seamlessly with both synchronous and asynchronous functions
- 📊 **Request Tracking**: Built-in request ID tracking for distributed systems
- 🚀 **Zero Dependencies**: Lightweight with minimal external dependencies

## Installation

```bash
pip install sherlock-ai
```

## Quick Start

### Basic Setup

```python
from sherlock_ai.logging_config import setup_logging
from sherlock_ai.performance import log_performance

# Initialize logging (call once at application startup)
setup_logging()

@log_performance
def my_function():
    # Your code here
    time.sleep(1)
    return "result"

# This will log: PERFORMANCE | my_module.my_function | SUCCESS | 1.003s
result = my_function()
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

## Configuration

### Logging Setup

```python
from sherlock_ai.logging_config import setup_logging, get_logger

# Initialize logging (call once at application startup)
setup_logging()

# Get a logger for your module
logger = get_logger(__name__)

# Use the logger
logger.info("Application started")
logger.error("Something went wrong")
```

**Log Files Created:**
When you call `setup_logging()`, it automatically creates a `logs/` directory with these files:
- `app.log` - All INFO+ level logs
- `errors.log` - Only ERROR+ level logs  
- `api.log` - API-related logs
- `database.log` - Database operation logs
- `services.log` - Service operation logs
- `performance.log` - Performance monitoring logs

### Request ID Tracking

```python
from sherlock_ai.utils.helper import get_request_id

# Get current request ID for distributed tracing
request_id = get_request_id()
```

### Complete Application Example

```python
from sherlock_ai.logging_config import setup_logging, get_logger
from sherlock_ai.performance import log_performance, PerformanceTimer

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

- **API Performance Monitoring**: Track response times for your web APIs
- **Database Query Optimization**: Monitor slow database operations
- **Microservices Debugging**: Trace execution times across service boundaries
- **Algorithm Benchmarking**: Compare performance of different implementations
- **Production Monitoring**: Get insights into your application's performance characteristics

## Requirements

- Python >= 3.13
- Standard library only (no external dependencies)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Links

- **Homepage**: [https://github.com/pranawmishra/sherlock-ai](https://github.com/pranawmishra/sherlock-ai)
- **Repository**: [https://github.com/pranawmishra/sherlock-ai](https://github.com/pranawmishra/sherlock-ai)
- **Issues**: [https://github.com/pranawmishra/sherlock-ai/issues](https://github.com/pranawmishra/sherlock-ai/issues)