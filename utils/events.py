"""
Event system for inter-service communication.

This module provides an event bus implementation that allows for publish-subscribe
communication patterns between services and components without direct dependencies.
"""
import logging
import inspect
import asyncio
import traceback
from typing import Any, Callable, Dict, List, Optional, Set, Type, TypeVar, Union, get_type_hints

from pydantic import BaseModel, Field, create_model, ValidationError

logger = logging.getLogger(__name__)

# Type definitions
TEvent = TypeVar('TEvent', bound='Event')
EventHandler = Callable[[TEvent], Any]


class Event(BaseModel):
    """
    Base class for all events in the system.
    
    All events must inherit from this class and define their own
    attributes for the event data.
    """
    event_id: str = Field(default="", description="Unique identifier for this event instance")
    timestamp: float = Field(default_factory=lambda: asyncio.get_event_loop().time(), 
                             description="Time the event was created")
    source: str = Field(default="", description="Source component that generated the event")
    
    def __init__(self, **data):
        """Initialize event with metadata."""
        # Set default event_id if not provided
        if 'event_id' not in data:
            data['event_id'] = f"{self.__class__.__name__}_{id(self)}"
        
        # Set source if not provided - try to get from caller frame
        if 'source' not in data:
            # Try to determine source from the call stack
            frame = inspect.currentframe()
            if frame:
                try:
                    frame = frame.f_back  # Get the caller's frame
                    if frame:
                        module = inspect.getmodule(frame)
                        if module:
                            data['source'] = module.__name__
                except Exception:
                    pass  # Failed to get source automatically
            
        super().__init__(**data)
    
    class Config:
        """Pydantic model configuration."""
        arbitrary_types_allowed = True


class EventBus:
    """
    Event bus for publishing and subscribing to events.
    
    This class implements the publish-subscribe pattern allowing
    components to communicate without direct dependencies.
    """
    
    def __init__(self):
        """Initialize the event bus."""
        # Map of event types to sets of handler functions
        self._handlers: Dict[Type[Event], List[EventHandler]] = {}
        
        # Map of handler functions to event types
        self._handler_to_event: Dict[EventHandler, Set[Type[Event]]] = {}
        
        # Current subscriptions for debug/tracing
        self._subscriptions: Dict[Type[Event], Set[str]] = {}
        
        logger.debug("Event bus initialized")
    
    def subscribe(self, event_type: Type[TEvent], handler: EventHandler) -> None:
        """
        Subscribe a handler function to a specific event type.
        
        Args:
            event_type: The type of event to subscribe to
            handler: Function to call when an event of this type is published
        """
        # Create handler list for this event type if it doesn't exist
        if event_type not in self._handlers:
            self._handlers[event_type] = []
            self._subscriptions[event_type] = set()
        
        # Add the handler if not already present
        if handler not in self._handlers[event_type]:
            self._handlers[event_type].append(handler)
            
            # Track event types for this handler
            if handler not in self._handler_to_event:
                self._handler_to_event[handler] = set()
            self._handler_to_event[handler].add(event_type)
            
            # Log the subscription
            handler_name = getattr(handler, "__qualname__", str(handler))
            handler_module = getattr(handler, "__module__", "unknown")
            subscription = f"{handler_module}.{handler_name}"
            self._subscriptions[event_type].add(subscription)
            
            logger.debug(f"Subscribed {subscription} to {event_type.__name__}")
    
    def unsubscribe(self, event_type: Type[TEvent], handler: EventHandler) -> bool:
        """
        Unsubscribe a handler from an event type.
        
        Args:
            event_type: The type of event to unsubscribe from
            handler: The handler function to unsubscribe
            
        Returns:
            True if the handler was unsubscribed, False otherwise
        """
        if event_type in self._handlers and handler in self._handlers[event_type]:
            self._handlers[event_type].remove(handler)
            
            # Clean up the handler_to_event mapping
            if handler in self._handler_to_event:
                self._handler_to_event[handler].discard(event_type)
                if not self._handler_to_event[handler]:
                    del self._handler_to_event[handler]
            
            # Clean up the subscriptions tracking
            handler_name = getattr(handler, "__qualname__", str(handler))
            handler_module = getattr(handler, "__module__", "unknown")
            subscription = f"{handler_module}.{handler_name}"
            if event_type in self._subscriptions:
                self._subscriptions[event_type].discard(subscription)
            
            logger.debug(f"Unsubscribed {subscription} from {event_type.__name__}")
            return True
        return False
    
    def unsubscribe_all(self, handler: EventHandler) -> int:
        """
        Unsubscribe a handler from all event types.
        
        Args:
            handler: The handler function to unsubscribe
            
        Returns:
            Number of event types unsubscribed from
        """
        if handler not in self._handler_to_event:
            return 0
        
        event_types = list(self._handler_to_event[handler])
        count = 0
        
        for event_type in event_types:
            if self.unsubscribe(event_type, handler):
                count += 1
        
        return count
    
    def publish(self, event: Event) -> List[Any]:
        """
        Publish an event to all subscribed handlers.
        
        Args:
            event: The event to publish
            
        Returns:
            List of results from the handlers
        """
        results = []
        event_type = type(event)
        
        # Find and call all matching handlers
        handlers_to_call = []
        
        # Exact match handlers
        if event_type in self._handlers:
            handlers_to_call.extend(self._handlers[event_type])
        
        # Handlers for parent classes (inheritance)
        for registered_type, handlers in self._handlers.items():
            if event_type != registered_type and issubclass(event_type, registered_type):
                handlers_to_call.extend(handlers)
        
        # Call all handlers and collect results
        for handler in handlers_to_call:
            try:
                result = handler(event)
                results.append(result)
            except Exception as e:
                logger.error(
                    f"Error in event handler {handler.__qualname__} for {event_type.__name__}: {e}",
                    exc_info=True
                )
                results.append(None)
        
        logger.debug(f"Published {event_type.__name__} to {len(handlers_to_call)} handlers")
        return results
    
    def publish_async(self, event: Event) -> asyncio.Future:
        """
        Publish an event asynchronously to all subscribed handlers.
        
        This will not block the caller thread.
        
        Args:
            event: The event to publish
            
        Returns:
            Future that will contain the list of results when complete
        """
        loop = asyncio.get_event_loop()
        return loop.run_in_executor(None, self.publish, event)
    
    def get_subscription_info(self) -> Dict[str, List[str]]:
        """
        Get information about current subscriptions for debugging.
        
        Returns:
            Dictionary mapping event types to lists of subscriber descriptions
        """
        result = {}
        for event_type, subscriptions in self._subscriptions.items():
            if subscriptions:  # Only include event types with actual subscriptions
                result[event_type.__name__] = sorted(list(subscriptions))
        return result


# Global event bus instance
event_bus = EventBus()


def subscribe(event_type: Type[TEvent]) -> Callable[[EventHandler], EventHandler]:
    """
    Decorator for subscribing a function to an event type.
    
    Example:
        @subscribe(UserCreatedEvent)
        def handle_user_created(event: UserCreatedEvent):
            # Process the event
            pass
    
    Args:
        event_type: The type of event to subscribe to
            
    Returns:
        Decorator function that will register the decorated function as an event handler
    """
    def decorator(func: EventHandler) -> EventHandler:
        event_bus.subscribe(event_type, func)
        return func
    return decorator


def publish(event: Event) -> List[Any]:
    """
    Publish an event to all subscribed handlers.
    
    This is a convenience function that uses the global event bus.
    
    Args:
        event: The event to publish
        
    Returns:
        List of results from the handlers
    """
    return event_bus.publish(event)


def publish_async(event: Event) -> asyncio.Future:
    """
    Publish an event asynchronously to all subscribed handlers.
    
    This is a convenience function that uses the global event bus.
    
    Args:
        event: The event to publish
        
    Returns:
        Future that will contain the list of results when complete
    """
    return event_bus.publish_async(event)


# Standard system events

class SystemEvent(Event):
    """Base class for system-level events."""
    pass


class ServiceEvent(Event):
    """Base class for service-level events."""
    service_name: str = Field(description="Name of the service that generated the event")


class UIEvent(Event):
    """Base class for UI-level events."""
    component: str = Field(description="Name of the UI component that generated the event")


class ApplicationStartedEvent(SystemEvent):
    """Event published when the application starts."""
    version: str = Field(description="Application version")


class ApplicationShuttingDownEvent(SystemEvent):
    """Event published when the application is shutting down."""
    pass


class ServiceInitializedEvent(ServiceEvent):
    """Event published when a service is initialized."""
    pass


class ServiceErrorEvent(ServiceEvent):
    """Event published when a service encounters an error."""
    error_message: str = Field(description="Error message")
    stack_trace: str = Field(default="", description="Stack trace if available")
    
    def __init__(self, service_name: str, error: Exception, **data):
        """Initialize with error details."""
        data['service_name'] = service_name
        data['error_message'] = str(error)
        data['stack_trace'] = "".join(traceback.format_exception(type(error), error, error.__traceback__))
        super().__init__(**data)


class ConfigurationChangedEvent(SystemEvent):
    """Event published when configuration changes."""
    changes: Dict[str, Any] = Field(default_factory=dict, description="Map of changed keys to new values")


class PageNavigationEvent(UIEvent):
    """Event published when navigating between pages."""
    from_page: str = Field(description="Page navigated from")
    to_page: str = Field(description="Page navigated to")
    params: Dict[str, Any] = Field(default_factory=dict, description="Navigation parameters")