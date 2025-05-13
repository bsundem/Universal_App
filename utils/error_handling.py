"""
Error handling utilities for the Universal App.

This module provides standardized error handling mechanisms:
- Custom exception classes
- Error handling decorators
- Error reporting utilities
"""
import sys
import logging
import traceback
from functools import wraps
from types import TracebackType
from typing import Any, Callable, Dict, Optional, Type, TypeVar, Union, cast

logger = logging.getLogger(__name__)

# Type variable for better typing support in decorators
F = TypeVar('F', bound=Callable[..., Any])


class ServiceError(Exception):
    """
    Base exception class for service-related errors.
    
    This exception includes context information about the service and operation
    that caused the error, making it easier to diagnose and handle problems.
    """
    
    def __init__(
        self, 
        message: str, 
        service: str, 
        operation: str,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        """
        Initialize a ServiceError.
        
        Args:
            message: Error message
            service: Name of the service where the error occurred
            operation: Name of the operation that failed
            details: Additional details about the error
            cause: Original exception that caused this error, if any
        """
        self.service = service
        self.operation = operation
        self.details = details or {}
        self.cause = cause
        
        # Add cause info to the message if available
        full_message = message
        if cause:
            full_message = f"{message} [Caused by: {type(cause).__name__}: {str(cause)}]"
            
        super().__init__(full_message)


class ConfigError(Exception):
    """Exception raised for configuration-related errors."""
    
    def __init__(self, message: str, section: Optional[str] = None, key: Optional[str] = None):
        """
        Initialize a ConfigError.
        
        Args:
            message: Error message
            section: Configuration section where the error occurred
            key: Specific configuration key that caused the error
        """
        self.section = section
        self.key = key
        
        if section and key:
            full_message = f"{message} (Section: {section}, Key: {key})"
        elif section:
            full_message = f"{message} (Section: {section})"
        else:
            full_message = message
            
        super().__init__(full_message)


class UIError(Exception):
    """Exception raised for UI-related errors."""
    
    def __init__(self, message: str, component: Optional[str] = None):
        """
        Initialize a UIError.
        
        Args:
            message: Error message
            component: UI component where the error occurred
        """
        self.component = component
        
        if component:
            full_message = f"{message} (Component: {component})"
        else:
            full_message = message
            
        super().__init__(full_message)


def handle_service_errors(service_name: str) -> Callable[[F], F]:
    """
    Decorator for handling service method errors.
    
    This decorator catches all exceptions in a service method, logs them
    appropriately, and re-raises them as ServiceError with proper context.
    
    Args:
        service_name: Name of the service for context in error messages
        
    Returns:
        Decorated function
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            operation_name = func.__name__
            try:
                return func(*args, **kwargs)
            except ServiceError:
                # Don't wrap ServiceError again, just re-raise
                raise
            except Exception as e:
                # Log the error with a stack trace
                logger.error(
                    f"Error in {service_name}.{operation_name}: {str(e)}",
                    exc_info=True
                )
                
                # Re-raise as ServiceError
                raise ServiceError(
                    message=f"Service operation failed: {str(e)}",
                    service=service_name,
                    operation=operation_name,
                    cause=e
                ) from e
                
        return cast(F, wrapper)
    return decorator


def report_error(
    error: Exception,
    title: str = "Error",
    show_details: bool = True
) -> None:
    """
    Report an error to the user and log it.
    
    Args:
        error: The exception to report
        title: Title for the error message dialog
        show_details: Whether to show error details in the dialog
    """
    # Log the error
    logger.error(f"{title}: {str(error)}", exc_info=error)
    
    # Get error details
    error_type = type(error).__name__
    error_message = str(error)
    
    error_details = f"{error_type}: {error_message}"
    if show_details:
        tb = traceback.format_exception(type(error), error, error.__traceback__)
        error_details += "\n\nDetails:\n" + "".join(tb)
    
    # In GUI context, we should show a dialog, but here we'll just print
    # since the UI may not be available yet
    print(f"ERROR: {title}\n{error_details}", file=sys.stderr)
    
    # TODO: When UI is implemented, show a proper error dialog
    # from ui.dialogs import show_error_dialog
    # show_error_dialog(title, error_message, error_details if show_details else None)


def log_exception_handler(
    exc_type: Type[BaseException],
    exc_value: BaseException,
    exc_traceback: Optional[TracebackType]
) -> None:
    """
    Global exception handler that logs unhandled exceptions.
    
    This can be set as sys.excepthook to catch and log exceptions that
    would otherwise crash the application.
    
    Args:
        exc_type: The exception type
        exc_value: The exception instance
        exc_traceback: The traceback object
    """
    if issubclass(exc_type, KeyboardInterrupt):
        # Don't log keyboard interrupt
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
        
    logger.critical(
        "Unhandled exception",
        exc_info=(exc_type, exc_value, exc_traceback)
    )
    
    # Call the original exception handler
    sys.__excepthook__(exc_type, exc_value, exc_traceback)


# Set the global exception handler
sys.excepthook = log_exception_handler