"""
Unit tests for the dependency injection container.
"""
import pytest
from unittest.mock import MagicMock

from services.container import (
    container,
    get_r_service,
    get_actuarial_service,
    get_actuarial_data_manager,
    get_kaggle_service,
    get_kaggle_data_manager,
    override_provider,
    reset_overrides
)


@pytest.mark.container
class TestDIContainer:
    """Test cases for the dependency injection container."""
    
    def test_get_providers(self, reset_container):
        """Test that all providers return non-None values."""
        # Get services
        r_service = get_r_service()
        actuarial_service = get_actuarial_service()
        actuarial_dm = get_actuarial_data_manager()
        kaggle_service = get_kaggle_service()
        kaggle_dm = get_kaggle_data_manager()
        
        # Verify all services are not None
        assert r_service is not None
        assert actuarial_service is not None
        assert actuarial_dm is not None
        assert kaggle_service is not None
        assert kaggle_dm is not None
    
    def test_override_provider(self, reset_container):
        """Test overriding a provider."""
        # Get the original R service
        original_r_service = get_r_service()
        
        # Create a mock service
        mock_r_service = MagicMock()
        mock_r_service.is_available.return_value = True
        
        # Override the provider
        override_provider("r_service", mock_r_service)
        
        # Get the service again
        r_service = get_r_service()
        
        # Verify it's now our mock
        assert r_service is mock_r_service
        assert r_service is not original_r_service
        
        # Call a method on the mock service
        result = r_service.is_available()
        
        # Verify the mock method was called
        mock_r_service.is_available.assert_called_once()
        assert result is True
    
    def test_reset_overrides(self, reset_container):
        """Test resetting provider overrides."""
        # Get the original R service
        original_r_service = get_r_service()
        
        # Create a mock service
        mock_r_service = MagicMock()
        
        # Override the provider
        override_provider("r_service", mock_r_service)
        
        # Verify override worked
        assert get_r_service() is mock_r_service
        
        # Reset overrides
        reset_overrides()
        
        # Get the service again
        r_service = get_r_service()
        
        # The reset should have restored the original provider
        assert r_service is not mock_r_service
    
    def test_override_invalid_provider(self, reset_container):
        """Test overriding an invalid provider."""
        # Create a mock service
        mock_service = MagicMock()
        
        # Attempt to override a non-existent provider
        with pytest.raises(ValueError):
            override_provider("non_existent_service", mock_service)
    
    def test_provider_singleton(self, reset_container):
        """Test that providers return singleton instances."""
        # Get services multiple times
        r_service1 = get_r_service()
        r_service2 = get_r_service()
        
        # Verify they are the same instance
        assert r_service1 is r_service2