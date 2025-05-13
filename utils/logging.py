"""
Logging utilities for the Universal App.

This module provides enhanced logging functionality beyond Python's standard
logging module, including:
- Custom log formatting
- Service-specific logging configuration
- Performance logging decorators
"""
import time
import logging
import functools
from typing import Any, Callable, Optional, TypeVar, cast

from core.config import config_manager

# Type variable for better typing support in decorators
F = TypeVar('F', bound=Callable[..., Any])


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.
    
    This is a convenience wrapper around logging.getLogger that ensures
    consistent logger configuration.
    
    Args:
        name: Logger name, typically __name__ or a module path
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Check if a handler is already configured for this logger
    if not logger.handlers and not logger.parent.handlers:
        # Configure a basic handler if none is configured
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            config_manager.logging.format,
            datefmt=config_manager.logging.date_format
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    return logger


def log_call(level: int = logging.DEBUG) -> Callable[[F], F]:
    """
    Decorator to log function calls with arguments and return values.
    
    Args:
        level: Logging level to use
        
    Returns:
        Decorated function
    """
    def decorator(func: F) -> F:
        logger = logging.getLogger(func.__module__)
        
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            func_name = func.__name__
            arg_str = ", ".join(
                [str(a) for a in args] + 
                [f"{k}={v}" for k, v in kwargs.items()]
            )
            
            logger.log(level, f"Calling {func_name}({arg_str})")
            try:
                result = func(*args, **kwargs)
                logger.log(level, f"{func_name} returned: {result}")
                return result
            except Exception as e:
                logger.log(level, f"{func_name} raised: {type(e).__name__}: {e}")
                raise
                
        return cast(F, wrapper)
    return decorator


def log_performance(level: int = logging.DEBUG) -> Callable[[F], F]:
    """
    Decorator to log function execution time.
    
    Args:
        level: Logging level to use
        
    Returns:
        Decorated function
    """
    def decorator(func: F) -> F:
        logger = logging.getLogger(func.__module__)
        
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            func_name = func.__name__
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                elapsed_time = (time.time() - start_time) * 1000  # ms
                logger.log(level, f"{func_name} executed in {elapsed_time:.2f}ms")
                return result
            except Exception as e:
                elapsed_time = (time.time() - start_time) * 1000  # ms
                logger.log(level, f"{func_name} failed after {elapsed_time:.2f}ms: {e}")
                raise
                
        return cast(F, wrapper)
    return decorator


class ServiceLogger:
    """
    Logger class for services with consistent formatting and context.
    
    This class provides a wrapper around the standard logging.Logger with
    additional features specific to services.
    """
    
    def __init__(self, service_name: str):
        """
        Initialize a ServiceLogger.
        
        Args:
            service_name: Name of the service for context in log messages
        """
        self.service_name = service_name
        self.logger = logging.getLogger(f"services.{service_name}")
        
    def _format_message(self, message: str, operation: Optional[str] = None) -> str:
        """
        Format a log message with service context.
        
        Args:
            message: Original log message
            operation: Optional operation name for additional context
            
        Returns:
            Formatted message
        """
        if operation:
            return f"[{self.service_name}.{operation}] {message}"
        return f"[{self.service_name}] {message}"
        
    def debug(self, message: str, operation: Optional[str] = None) -> None:
        """Log a debug message."""
        self.logger.debug(self._format_message(message, operation))
        
    def info(self, message: str, operation: Optional[str] = None) -> None:
        """Log an info message."""
        self.logger.info(self._format_message(message, operation))
        
    def warning(self, message: str, operation: Optional[str] = None) -> None:
        """Log a warning message."""
        self.logger.warning(self._format_message(message, operation))
        
    def error(self, message: str, operation: Optional[str] = None, exc_info: Any = None) -> None:
        """Log an error message."""
        self.logger.error(self._format_message(message, operation), exc_info=exc_info)
        
    def critical(self, message: str, operation: Optional[str] = None, exc_info: Any = None) -> None:
        """Log a critical message."""
        self.logger.critical(self._format_message(message, operation), exc_info=exc_info)
        
    def exception(self, message: str, operation: Optional[str] = None) -> None:
        """Log an exception message with stack trace."""
        self.logger.exception(self._format_message(message, operation))