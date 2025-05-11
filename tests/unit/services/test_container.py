"""
Unit tests for the dependency injection container.
"""
import pytest
from unittest.mock import patch, MagicMock
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


class TestContainer:
    """Test cases for the dependency injection container."""
    
    def test_get_r_service(self):
        """Test retrieving the R service."""
        r_service = get_r_service()
        assert r_service is not None
    
    def test_get_actuarial_service(self):
        """Test retrieving the actuarial service."""
        actuarial_service = get_actuarial_service()
        assert actuarial_service is not None
    
    def test_get_actuarial_data_manager(self):
        """Test retrieving the actuarial data manager."""
        data_manager = get_actuarial_data_manager()
        assert data_manager is not None
    
    def test_get_kaggle_service(self):
        """Test retrieving the Kaggle service."""
        kaggle_service = get_kaggle_service()
        assert kaggle_service is not None
    
    def test_get_kaggle_data_manager(self):
        """Test retrieving the Kaggle data manager."""
        data_manager = get_kaggle_data_manager()
        assert data_manager is not None
    
    def test_override_provider(self):
        """Test overriding a provider for testing."""
        # Create a mock implementation
        mock_r_service = MagicMock()
        mock_r_service.is_available.return_value = True
        
        try:
            # Override the r_service provider
            override_provider("r_service", mock_r_service)
            
            # Get the service - should be our mock
            service = get_r_service()
            
            # Verify it's our mock
            assert service is mock_r_service
            assert service.is_available() is True
            
            # Test invalid provider name
            with pytest.raises(ValueError):
                override_provider("non_existent_service", MagicMock())
                
        finally:
            # Reset all overrides to not affect other tests
            reset_overrides()
    
    def test_reset_overrides(self):
        """Test resetting provider overrides."""
        # Create a mock implementation
        mock_r_service = MagicMock()
        
        # Get the original implementation
        original_service = get_r_service()
        
        try:
            # Override the r_service provider
            override_provider("r_service", mock_r_service)
            
            # Verify override worked
            assert get_r_service() is mock_r_service
            
            # Reset overrides
            reset_overrides()
            
            # Verify we get the original implementation back
            assert get_r_service() is original_service
            
        finally:
            # Make sure overrides are reset
            reset_overrides()