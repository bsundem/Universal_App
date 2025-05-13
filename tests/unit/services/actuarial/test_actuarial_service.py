"""
Tests for the actuarial service in services/actuarial/actuarial_service.py.
"""
import os
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock

from services.actuarial.actuarial_service import ActuarialService
from utils.error_handling import ServiceError


@pytest.fixture
def mock_r_service():
    """Create a mock R service."""
    mock = MagicMock()
    mock.is_available.return_value = True
    mock.execute_script.return_value = True
    
    # Setup for mortality data calculation
    mock_mortality_result = MagicMock()
    mock_mortality_result.rx2.side_effect = lambda x: {
        'Age': [30, 31, 32],
        'qx': [0.001, 0.0011, 0.0012],
        'px': [0.999, 0.9989, 0.9988],
        'lx': [100000, 99900, 99789],
        'ex': [50, 49, 48],
        'ax': [14.8, 14.6, 14.4]
    }[x]
    mock.call_function.return_value = mock_mortality_result
    
    # Setup for present value calculation
    mock_pv_result = MagicMock()
    mock_pv_result.rx2.side_effect = lambda x: {
        'present_value': [100000.0],
        'expected_duration': [15.3],
        'monthly_equivalent': [550.0]
    }[x]
    
    return mock


@pytest.fixture
def mock_get_r_service(mock_r_service):
    """Mock the get_r_service function to return our mock."""
    with patch('services.actuarial.actuarial_service.get_r_service', return_value=mock_r_service):
        yield mock_r_service


@pytest.fixture
def actuarial_service(mock_get_r_service):
    """Create an actuarial service instance with mocked R service."""
    with patch('os.makedirs'):
        with patch('tempfile.mkdtemp', return_value='/tmp/test_dir'):
            return ActuarialService(data_dir='/test/actuarial/data')


class TestActuarialService:
    """Test cases for the ActuarialService class."""
    
    def test_init(self, actuarial_service):
        """Test initialization of actuarial service."""
        assert actuarial_service.data_dir == '/test/actuarial/data'
        assert actuarial_service.temp_dir == '/tmp/test_dir'
        assert actuarial_service.mortality_script_path == 'actuarial/mortality.R'
        assert actuarial_service.present_value_script_path == 'actuarial/present_value.R'
    
    def test_is_r_available(self, actuarial_service, mock_get_r_service):
        """Test is_r_available method."""
        mock_get_r_service.is_available.return_value = True
        
        result = actuarial_service.is_r_available()
        
        assert result is True
        mock_get_r_service.is_available.assert_called_once()
    
    def test_calculate_mortality_data_success(self, actuarial_service, mock_get_r_service):
        """Test calculate_mortality_data method for successful calculation."""
        # Call the method
        result = actuarial_service.calculate_mortality_data(
            age_from=30,
            age_to=32,
            interest_rate=0.035,
            table_type='soa_2012',
            gender='male'
        )
        
        # Verify R service interactions
        mock_get_r_service.execute_script.assert_called_with('actuarial/mortality.R')
        mock_get_r_service.call_function.assert_called_with(
            'calculate_mortality',
            age_from=30,
            age_to=32,
            interest_rate=0.035,
            table_type='soa_2012',
            gender='male'
        )
        
        # Verify the result
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        assert list(result.columns) == ['Age', 'qx', 'px', 'lx', 'ex', 'ax']
        assert list(result['Age']) == [30, 31, 32]
    
    def test_calculate_mortality_data_error(self, actuarial_service, mock_get_r_service):
        """Test calculate_mortality_data method when R calculation fails."""
        # Setup R service to raise an exception
        mock_get_r_service.call_function.side_effect = Exception("R calculation failed")
        
        # Attempt to call the method, expect a ServiceError
        with pytest.raises(ServiceError) as excinfo:
            actuarial_service.calculate_mortality_data(
                age_from=30,
                age_to=32,
                interest_rate=0.035,
                table_type='soa_2012',
                gender='male'
            )
        
        assert "Failed to calculate mortality data" in str(excinfo.value)
    
    def test_calculate_mortality_data_none_result(self, actuarial_service, mock_get_r_service):
        """Test calculate_mortality_data method when R returns None."""
        # Setup R service to return None
        mock_get_r_service.call_function.return_value = None
        
        # Attempt to call the method, expect a ServiceError
        with pytest.raises(ServiceError) as excinfo:
            actuarial_service.calculate_mortality_data(
                age_from=30,
                age_to=32,
                interest_rate=0.035,
                table_type='soa_2012',
                gender='male'
            )
        
        assert "R calculation returned None" in str(excinfo.value)
    
    def test_calculate_present_value_success(self, actuarial_service, mock_get_r_service):
        """Test calculate_present_value method for successful calculation."""
        # Call the method
        result = actuarial_service.calculate_present_value(
            age=35,
            payment=10000,
            interest_rate=0.035,
            term=20,
            frequency='Annual',
            table_type='soa_2012',
            gender='female'
        )
        
        # Verify R service interactions
        mock_get_r_service.execute_script.assert_called_with('actuarial/present_value.R')
        mock_get_r_service.call_function.assert_called_with(
            'calculate_pv',
            age=35,
            payment=10000,
            interest_rate=0.035,
            term=20,
            freq_factor=1,  # Annual
            table_type='soa_2012',
            gender='female'
        )
        
        # Verify the result
        assert isinstance(result, dict)
        assert 'present_value' in result
        assert 'expected_duration' in result
        assert 'monthly_equivalent' in result
        assert result['present_value'] == 100000.0
        assert result['expected_duration'] == 15.3
        assert result['monthly_equivalent'] == 550.0
    
    def test_calculate_present_value_frequency_mapping(self, actuarial_service, mock_get_r_service):
        """Test calculate_present_value method with different frequency values."""
        # Test with Semi-annual frequency
        actuarial_service.calculate_present_value(
            age=35, payment=10000, interest_rate=0.035, term=20,
            frequency='Semi-annual', table_type='soa_2012', gender='female'
        )
        mock_get_r_service.call_function.assert_called_with(
            'calculate_pv', age=35, payment=10000, interest_rate=0.035,
            term=20, freq_factor=2, table_type='soa_2012', gender='female'
        )
        
        # Test with Quarterly frequency
        actuarial_service.calculate_present_value(
            age=35, payment=10000, interest_rate=0.035, term=20,
            frequency='Quarterly', table_type='soa_2012', gender='female'
        )
        mock_get_r_service.call_function.assert_called_with(
            'calculate_pv', age=35, payment=10000, interest_rate=0.035,
            term=20, freq_factor=4, table_type='soa_2012', gender='female'
        )
        
        # Test with Monthly frequency
        actuarial_service.calculate_present_value(
            age=35, payment=10000, interest_rate=0.035, term=20,
            frequency='Monthly', table_type='soa_2012', gender='female'
        )
        mock_get_r_service.call_function.assert_called_with(
            'calculate_pv', age=35, payment=10000, interest_rate=0.035,
            term=20, freq_factor=12, table_type='soa_2012', gender='female'
        )
    
    def test_calculate_present_value_error(self, actuarial_service, mock_get_r_service):
        """Test calculate_present_value method when R calculation fails."""
        # Setup R service to raise an exception
        mock_get_r_service.call_function.side_effect = Exception("R calculation failed")
        
        # Attempt to call the method, expect a ServiceError
        with pytest.raises(ServiceError) as excinfo:
            actuarial_service.calculate_present_value(
                age=35,
                payment=10000,
                interest_rate=0.035,
                term=20,
                frequency='Annual',
                table_type='soa_2012',
                gender='female'
            )
        
        assert "Failed to calculate present value" in str(excinfo.value)
    
    def test_get_available_mortality_tables_success(self, actuarial_service, mock_get_r_service):
        """Test get_available_mortality_tables method for successful retrieval."""
        # Setup mock for get_available_tables function
        mock_tables_result = MagicMock()
        mock_tables_result.rx2.side_effect = lambda x: {
            'id': ['soa_2012', 'cso_2001'],
            'name': ['SOA 2012 IAM', 'CSO 2001'],
            'description': [
                'Society of Actuaries 2012 Individual Annuity Mortality',
                '2001 Commissioners Standard Ordinary Mortality Table'
            ]
        }[x]
        mock_get_r_service.call_function.return_value = mock_tables_result
        
        # Call the method
        result = actuarial_service.get_available_mortality_tables()
        
        # Verify R service interactions
        mock_get_r_service.execute_script.assert_called_with('actuarial/mortality.R')
        mock_get_r_service.call_function.assert_called_with('get_available_tables')
        
        # Verify the result
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]['id'] == 'soa_2012'
        assert result[0]['name'] == 'SOA 2012 IAM'
        assert result[1]['id'] == 'cso_2001'
    
    def test_get_available_mortality_tables_r_none(self, actuarial_service, mock_get_r_service):
        """Test get_available_mortality_tables method when R returns None."""
        # Setup R service to return None
        mock_get_r_service.call_function.return_value = None
        
        # Call the method - should return default tables instead of raising an error
        result = actuarial_service.get_available_mortality_tables()
        
        # Verify the result contains default tables
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]['id'] == 'soa_2012'
        assert result[1]['id'] == 'cso_2001'
    
    def test_get_available_mortality_tables_r_error(self, actuarial_service, mock_get_r_service):
        """Test get_available_mortality_tables method when R call raises an error."""
        # Setup R service to raise an exception
        mock_get_r_service.call_function.side_effect = Exception("R error")
        
        # Attempt to call the method, expect a ServiceError
        with pytest.raises(ServiceError) as excinfo:
            actuarial_service.get_available_mortality_tables()
        
        assert "Failed to get available mortality tables" in str(excinfo.value)