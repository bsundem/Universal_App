"""
Example calculator plugin for the Universal App.

This module provides a simple calculator service plugin that
demonstrates how to implement the Plugin interface and integrate
with the application.
"""
import logging
from typing import Dict, Any, Optional, List, Protocol

from services.plugins.base import ServicePlugin
from utils.events import subscribe, ServiceEvent, Event

logger = logging.getLogger(__name__)


class CalculationPerformedEvent(Event):
    """Event published when a calculation is performed."""
    operation: str
    inputs: Dict[str, Any]
    result: Any


class CalculatorServiceInterface(Protocol):
    """Interface for calculator services."""
    
    def add(self, a: float, b: float) -> float:
        """Add two numbers."""
        ...
        
    def subtract(self, a: float, b: float) -> float:
        """Subtract b from a."""
        ...
        
    def multiply(self, a: float, b: float) -> float:
        """Multiply two numbers."""
        ...
        
    def divide(self, a: float, b: float) -> float:
        """Divide a by b."""
        ...
        
    def get_history(self) -> List[Dict[str, Any]]:
        """Get calculation history."""
        ...


class CalculatorPlugin(ServicePlugin):
    """
    Example calculator service plugin.
    
    This plugin provides a simple calculator service that demonstrates
    how to implement a service plugin.
    """
    # Plugin metadata
    plugin_id = "calculator"
    plugin_name = "Calculator"
    plugin_version = "1.0.0"
    plugin_description = "Example calculator service plugin"
    
    # Service interface
    service_interface = CalculatorServiceInterface
    
    def __init__(self):
        """Initialize the calculator plugin."""
        super().__init__()
        self._history = []
        
    def _initialize(self) -> bool:
        """Initialize the plugin."""
        self.logger.info("Initializing calculator plugin")
        return True
        
    def _shutdown(self) -> None:
        """Shut down the plugin."""
        self.logger.info("Shutting down calculator plugin")
        self._history.clear()
        
    def add(self, a: float, b: float) -> float:
        """
        Add two numbers.
        
        Args:
            a: First number
            b: Second number
            
        Returns:
            Sum of a and b
        """
        result = a + b
        self._record_calculation("add", {"a": a, "b": b}, result)
        return result
        
    def subtract(self, a: float, b: float) -> float:
        """
        Subtract b from a.
        
        Args:
            a: First number
            b: Second number
            
        Returns:
            Difference of a and b
        """
        result = a - b
        self._record_calculation("subtract", {"a": a, "b": b}, result)
        return result
        
    def multiply(self, a: float, b: float) -> float:
        """
        Multiply two numbers.
        
        Args:
            a: First number
            b: Second number
            
        Returns:
            Product of a and b
        """
        result = a * b
        self._record_calculation("multiply", {"a": a, "b": b}, result)
        return result
        
    def divide(self, a: float, b: float) -> float:
        """
        Divide a by b.
        
        Args:
            a: First number
            b: Second number
            
        Returns:
            Quotient of a and b
            
        Raises:
            ZeroDivisionError: If b is zero
        """
        if b == 0:
            raise ZeroDivisionError("Cannot divide by zero")
            
        result = a / b
        self._record_calculation("divide", {"a": a, "b": b}, result)
        return result
        
    def get_history(self) -> List[Dict[str, Any]]:
        """
        Get calculation history.
        
        Returns:
            List of calculation records
        """
        return self._history.copy()
        
    def _record_calculation(self, operation: str, inputs: Dict[str, Any], result: Any) -> None:
        """
        Record a calculation in the history.
        
        Args:
            operation: Name of the operation
            inputs: Input parameters
            result: Calculation result
        """
        record = {
            "operation": operation,
            "inputs": inputs,
            "result": result,
            "timestamp": self.logger.handlers[0].formatter.converter()
        }
        
        self._history.append(record)
        
        # Limit history size
        if len(self._history) > 100:
            self._history.pop(0)
            
        # Publish event
        from utils.events import publish
        publish(CalculationPerformedEvent(
            source=f"plugin.{self.plugin_id}",
            operation=operation,
            inputs=inputs,
            result=result
        ))
        
        self.logger.debug(f"Recorded calculation: {operation}({inputs}) = {result}")


@subscribe(CalculationPerformedEvent)
def on_calculation_performed(event: CalculationPerformedEvent) -> None:
    """
    Handle calculation performed event.
    
    This is an example of how to subscribe to events from a plugin.
    
    Args:
        event: The calculation performed event
    """
    logger.info(
        f"Calculation performed: {event.operation} with inputs {event.inputs} = {event.result}"
    )