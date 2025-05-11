"""
Unit tests for service registration functionality.

These tests focus on the dynamic service registration and resolution functions
of the dependency injection container.
"""
import pytest
from unittest.mock import MagicMock, patch
from typing import Protocol

from services.container import (
    container,
    registry,
    register_service,
    get_service_by_interface,
    reset_overrides,
    reset_single_provider,
    get_all_services
)


# Define a test interface
class TestServiceInterface(Protocol):
    """Protocol for testing service registration."""

    def test_method(self) -> str:
        """A test method."""
        ...


# Define a test service implementation
class TestService:
    """Test service implementation."""

    def test_method(self) -> str:
        """Implementation of test method."""
        return "test result"

    # Prevent pytest from treating this as a test
    test_method.__test__ = False


# Test factory function for the test service
def create_test_service_provider():
    """Factory function for test service provider."""
    from dependency_injector import providers
    test_service = TestService()
    return providers.Singleton(lambda: test_service)


@pytest.mark.container
class TestServiceRegistration:
    """Test cases for service registration functionality."""
    
    def setup_method(self):
        """Set up test environment before each test method."""
        # Reset the container before each test
        reset_overrides()

        # Clean up test services from registry if they exist
        for service_name in ['test_service', 'another_test_service', 'none_service']:
            if service_name in registry._registry:
                del registry._registry[service_name]

            interface_type = TestServiceInterface
            if interface_type in registry._interface_registry:
                del registry._interface_registry[interface_type]

            # Clean up the provider from container if exists
            provider_attr = f"{service_name}_provider"
            if hasattr(container, provider_attr):
                delattr(container, provider_attr)

        # Create a fresh test service for each test
        self.test_service = TestService()

    def teardown_method(self):
        """Clean up after each test method."""
        # Reset the container after each test
        reset_overrides()

        # Clean up test services from registry if they exist
        for service_name in ['test_service', 'another_test_service', 'none_service']:
            if service_name in registry._registry:
                del registry._registry[service_name]

            interface_type = TestServiceInterface
            if interface_type in registry._interface_registry:
                del registry._interface_registry[interface_type]

            # Clean up the provider from container if exists
            provider_attr = f"{service_name}_provider"
            if hasattr(container, provider_attr):
                delattr(container, provider_attr)
    
    def test_register_new_service(self):
        """Test registering a new service."""
        # Register a new service
        register_service(
            "test_service", 
            self.test_service, 
            TestServiceInterface, 
            create_test_service_provider
        )
        
        # Verify it was registered
        assert hasattr(container, "test_service_provider")
        
        # Verify we can get it by interface
        service = get_service_by_interface(TestServiceInterface)
        assert service is not None
        assert service.test_method() == "test result"
        
        # Verify it appears in all services
        all_services = get_all_services()
        assert "test_service" in all_services
        assert all_services["test_service"]["interface"] == "TestServiceInterface"
    
    def test_register_duplicate_service(self):
        """Test attempting to register a service with the same name."""
        # Register a service
        register_service(
            "test_service", 
            self.test_service, 
            TestServiceInterface, 
            create_test_service_provider
        )
        
        # Now try to register another service with the same name
        with pytest.raises(ValueError) as exc_info:
            register_service(
                "test_service", 
                TestService(), 
                TestServiceInterface, 
                create_test_service_provider
            )
        
        assert "already registered" in str(exc_info.value)
    
    def test_get_service_by_unregistered_interface(self):
        """Test getting a service by an interface that isn't registered."""
        # Define a new interface that we won't register
        class UnregisteredInterface(Protocol):
            def some_method(self): ...

        # Try to get a service by the unregistered interface
        with pytest.raises(ValueError) as exc_info:
            get_service_by_interface(UnregisteredInterface)

        assert "No service registered for interface" in str(exc_info.value)

        # Also test get_all_services_by_interface with unregistered interface
        from services.container import get_all_services_by_interface
        with pytest.raises(ValueError) as exc_info:
            get_all_services_by_interface(UnregisteredInterface)

        assert "Error retrieving services for interface" in str(exc_info.value)
    
    def test_interface_resolution_with_multiple_registrations(self):
        """Test that interface resolution works correctly with multiple registrations."""
        # Register our test service
        register_service(
            "test_service",
            self.test_service,
            TestServiceInterface,
            create_test_service_provider
        )

        # Create a second implementation
        class AnotherTestService:
            def test_method(self) -> str:
                return "another test result"

        another_service = AnotherTestService()

        # Define a factory function
        def create_another_service_provider():
            from dependency_injector import providers
            return providers.Singleton(lambda: another_service)

        # Register the second service with a different name but same interface
        register_service(
            "another_test_service",
            another_service,
            TestServiceInterface,
            create_another_service_provider
        )

        # The interface registry should now point to the last registered service
        service = get_service_by_interface(TestServiceInterface)
        assert service is not None
        assert service.test_method() == "another test result"
        assert service is another_service

        # Test getting all implementations of the interface
        from services.container import get_all_services_by_interface
        services = get_all_services_by_interface(TestServiceInterface)

        # Verify we get both implementations
        assert len(services) == 2
        assert "test_service" in services
        assert "another_test_service" in services

        # Verify the service methods return the expected results
        assert services["test_service"].test_method() == "test result"
        assert services["another_test_service"].test_method() == "another test result"

        # Verify the second service has the expected identity
        assert services["another_test_service"] is another_service
    
    def test_reset_single_provider_after_registration(self):
        """Test resetting a single provider after registration."""
        # Register a service
        register_service(
            "test_service", 
            self.test_service, 
            TestServiceInterface, 
            create_test_service_provider
        )
        
        # Override the provider
        from dependency_injector import providers
        mock_service = MagicMock()
        mock_service.test_method.return_value = "mock result"
        container.test_service_provider.override(providers.Object(mock_service))
        
        # Verify the override worked
        service = get_service_by_interface(TestServiceInterface)
        assert service.test_method() == "mock result"
        
        # Reset just this provider
        reset_single_provider("test_service")
        
        # Verify we're back to the original
        service = get_service_by_interface(TestServiceInterface)
        assert service.test_method() == "test result"
        assert service is self.test_service


@pytest.mark.container
class TestServiceRegistrationEdgeCases:
    """Test edge cases for service registration functionality."""
    
    def setup_method(self):
        """Set up test environment before each test method."""
        reset_overrides()

        # Clean up test services from registry if they exist
        service_names = ['test_service', 'another_service', 'specialized_service', 'none_service']
        for service_name in service_names:
            if service_name in registry._registry:
                del registry._registry[service_name]

            # Clean up the provider from container if exists
            provider_attr = f"{service_name}_provider"
            if hasattr(container, provider_attr):
                delattr(container, provider_attr)

        # Also clean up interfaces
        interfaces = [TestServiceInterface]

        # Clean up any locally defined interfaces
        if hasattr(self, 'interfaces_to_clean'):
            interfaces.extend(self.interfaces_to_clean)

        for interface_type in interfaces:
            if interface_type in registry._interface_registry:
                del registry._interface_registry[interface_type]

    def teardown_method(self):
        """Clean up after each test method."""
        reset_overrides()

        # Clean up test services from registry if they exist
        service_names = ['test_service', 'another_service', 'specialized_service', 'none_service']
        for service_name in service_names:
            if service_name in registry._registry:
                del registry._registry[service_name]

            # Clean up the provider from container if exists
            provider_attr = f"{service_name}_provider"
            if hasattr(container, provider_attr):
                delattr(container, provider_attr)

        # Also clean up interfaces
        interfaces = [TestServiceInterface]

        # Clean up any locally defined interfaces
        if hasattr(self, 'interfaces_to_clean'):
            interfaces.extend(self.interfaces_to_clean)

        for interface_type in interfaces:
            if interface_type in registry._interface_registry:
                del registry._interface_registry[interface_type]
    
    def test_inheritance_based_interfaces(self):
        """Test registering and resolving services with inheritance-based interfaces."""
        # Define a hierarchy of interfaces
        class BaseInterface(Protocol):
            def base_method(self) -> str: ...

        class SpecializedInterface(BaseInterface, Protocol):
            def specialized_method(self) -> str: ...

        # Store interfaces for cleanup
        self.interfaces_to_clean = [BaseInterface, SpecializedInterface]

        # Define implementations
        class BaseService:
            def base_method(self) -> str:
                return "base method"

        class SpecializedService:
            def base_method(self) -> str:
                return "base from specialized"

            def specialized_method(self) -> str:
                return "specialized method"

        # Create factory functions
        def create_base_provider():
            from dependency_injector import providers
            return providers.Singleton(lambda: BaseService())

        def create_specialized_provider():
            from dependency_injector import providers
            return providers.Singleton(lambda: SpecializedService())

        # Register the services
        base_service = BaseService()
        specialized_service = SpecializedService()

        register_service("test_service", base_service, BaseInterface, create_base_provider)
        register_service("specialized_service", specialized_service, SpecializedInterface, create_specialized_provider)

        # Test resolving by base interface
        # (should return the base service since it was registered with that interface)
        base = get_service_by_interface(BaseInterface)
        assert base.base_method() == "base method"

        # Test resolving by specialized interface
        specialized = get_service_by_interface(SpecializedInterface)
        assert specialized.base_method() == "base from specialized"
        assert specialized.specialized_method() == "specialized method"
    
    def test_factory_function_called_during_registration(self):
        """Test that the factory function is actually called during registration."""
        called = False
        
        def create_test_provider():
            nonlocal called
            called = True
            from dependency_injector import providers
            return providers.Singleton(lambda: TestService())
        
        register_service("test_service", TestService(), TestServiceInterface, create_test_provider)
        
        assert called, "Factory function should be called during registration"
    
    def test_none_instance_registration(self):
        """Test registering None as a service instance."""
        def create_none_provider():
            from dependency_injector import providers
            return providers.Singleton(lambda: None)
        
        register_service("none_service", None, TestServiceInterface, create_none_provider)
        
        # Get the service instance
        service = get_service_by_interface(TestServiceInterface)
        assert service is None