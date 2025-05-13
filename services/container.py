"""
Dependency Injection Container for the Universal App.

This module provides a dependency injection container using the 
dependency-injector library, following the Dependency Inversion Principle.
The container manages service instances and their dependencies.
"""
import logging
from typing import Dict, Any, Optional
from dependency_injector import containers, providers

# Import services
from services.r_service import RService
from services.actuarial.actuarial_service import ActuarialService
from services.finance.finance_service import FinanceService
from core.config import config_manager

logger = logging.getLogger(__name__)


class Container(containers.DeclarativeContainer):
    """
    Dependency Injection container that manages all application services.
    
    This container follows the Dependency Inversion Principle, allowing high-level
    modules to depend on abstractions rather than concrete implementations.
    """
    
    # Configuration
    config = providers.Configuration()
    
    # Services
    r_service = providers.Singleton(
        RService,
        scripts_dir=config.services.r_integration.scripts_dir
    )
    
    actuarial_service = providers.Singleton(
        ActuarialService,
        data_dir=config.services.actuarial.data_dir
    )
    
    finance_service = providers.Singleton(
        FinanceService,
        data_dir=config.services.finance.data_dir
    )
    
    # Other resources
    resources = providers.Dict()
    

class ContainerManager:
    """
    Manager class for the dependency injection container.
    
    This class provides a simplified interface to the container and helper
    methods for service retrieval.
    """
    
    def __init__(self):
        """Initialize the container manager."""
        self._container = Container()
        self._container.config.from_dict(config_manager.get_config().model_dump())
        self._initialized = False
    
    def init_resources(self, **kwargs) -> None:
        """
        Initialize container resources.
        
        Args:
            **kwargs: Resources to add to the container
        """
        if not self._initialized:
            self._container.resources.update(kwargs)
            self._initialized = True
            logger.info("Container resources initialized")
    
    def get_container(self) -> Container:
        """
        Get the dependency injection container.
        
        Returns:
            The container instance
        """
        return self._container
    
    def override_provider(self, provider_name: str, provider_instance: Any) -> None:
        """
        Override a provider with a different implementation.
        
        This is useful for testing when you want to inject mock services.
        
        Args:
            provider_name: Name of the provider to override
            provider_instance: Instance to use instead
        """
        if hasattr(self._container, provider_name):
            provider = getattr(self._container, provider_name)
            provider.override(providers.Object(provider_instance))
            logger.debug(f"Provider {provider_name} overridden")
        else:
            logger.warning(f"Provider {provider_name} not found, cannot override")
    
    def reset_overrides(self) -> None:
        """Reset all provider overrides to their original implementations."""
        self._container.reset_override()
        logger.debug("All provider overrides reset")


# Global container manager instance
container = ContainerManager()


# Helper functions for retrieving services
def get_r_service() -> RService:
    """
    Get the R service instance.
    
    Returns:
        R service instance
    """
    return container.get_container().r_service()


def get_actuarial_service() -> ActuarialService:
    """
    Get the actuarial service instance.
    
    Returns:
        Actuarial service instance
    """
    return container.get_container().actuarial_service()


def get_finance_service() -> FinanceService:
    """
    Get the finance service instance.
    
    Returns:
        Finance service instance
    """
    return container.get_container().finance_service()