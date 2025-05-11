"""
Logging utility for the Universal App.

This module provides standardized logging capabilities throughout the application.
"""
import os
import logging
import logging.handlers
from typing import Dict, Any, Optional
import datetime

from core.config import config


# Set up global logger registry
LOGGERS = {}


class LoggerManager:
    """
    Manager for creating and retrieving loggers throughout the application.
    
    This class ensures that we have a consistent logging setup and that
    loggers are only created once per name.
    """
    
    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """
        Get a logger with the given name.
        
        Args:
            name: Name of the logger to retrieve or create
            
        Returns:
            Configured logger instance
        """
        # Return existing logger if already created
        if name in LOGGERS:
            return LOGGERS[name]
            
        # Create and configure a new logger
        logger = logging.getLogger(name)
        
        # Get logging configuration
        log_level = config.logging.get_log_level()
        log_format = config.logging.format
        date_format = config.logging.date_format
        log_file = config.logging.file
        max_size = config.logging.max_size
        backup_count = config.logging.backup_count
        
        # Configure logger level
        logger.setLevel(log_level)
        
        # Create formatter
        formatter = logging.Formatter(log_format, date_format)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # Create file handler if log file is specified
        if log_file:
            # Create log directory if it doesn't exist
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
                
            # Use rotating file handler to manage log size
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=max_size,
                backupCount=backup_count
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        # Store logger in registry
        LOGGERS[name] = logger
        
        return logger


# Module-level convenience function
def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the given name.
    
    Args:
        name: Name of the logger to retrieve or create
        
    Returns:
        Configured logger instance
    """
    return LoggerManager.get_logger(name)


# Create module-level logger for this module
logger = get_logger(__name__)


# Log configuration on import
logger.info("Logging initialized")
logger.debug(f"Logging configuration: level={config.logging.level}, "
             f"file={config.logging.file or 'None'}")


class LoggingContext:
    """
    Context manager for additional logging context.
    
    This allows adding context to log messages within a specific code block.
    """
    
    def __init__(self, logger: logging.Logger, **context):
        """
        Initialize the logging context.
        
        Args:
            logger: Logger to use
            **context: Context key-value pairs to add to log messages
        """
        self.logger = logger
        self.context = context
        self.original_factory = None
        
    def __enter__(self):
        # Store current log record factory
        self.original_factory = logging.getLogRecordFactory()
        
        # Create new factory that adds our context
        old_factory = self.original_factory
        context = self.context
        
        def record_factory(*args, **kwargs):
            record = old_factory(*args, **kwargs)
            for key, value in context.items():
                setattr(record, key, value)
            return record
            
        # Set the new factory
        logging.setLogRecordFactory(record_factory)
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore original factory
        logging.setLogRecordFactory(self.original_factory)


# Decorator for logging function calls
def log_function_call(logger_name: Optional[str] = None):
    """
    Decorator to log function entry and exit.
    
    Args:
        logger_name: Name of the logger to use, defaults to module name if None
        
    Returns:
        Decorated function
    """
    def decorator(func):
        # Get the module name from the function
        module_name = func.__module__
        
        # Use provided logger name or default to module name
        logger_to_use = get_logger(logger_name or module_name)
        
        def wrapper(*args, **kwargs):
            function_name = func.__name__
            logger_to_use.debug(f"Entering {function_name}")
            
            try:
                result = func(*args, **kwargs)
                logger_to_use.debug(f"Exiting {function_name}")
                return result
            except Exception as e:
                logger_to_use.exception(f"Exception in {function_name}: {str(e)}")
                raise
        
        return wrapper
    
    return decorator