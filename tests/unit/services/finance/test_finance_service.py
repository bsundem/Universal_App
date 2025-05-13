"""
Tests for the finance service in services/finance/finance_service.py.
"""
import os
import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock

from services.finance.finance_service import FinanceService
from utils.error_handling import ServiceError


@pytest.fixture
def mock_r_service():
    """Create a mock R service."""
    mock = MagicMock()
    mock.is_available.return_value = True
    mock.execute_script.return_value = True
    
    # Setup for yield curve calculation
    mock_yield_curve_data = pd.DataFrame({
        'Date': ['2023-01-01', '2023-01-01', '2023-01-01'],
        'Maturity': [1, 5, 10],
        'Yield': [0.025, 0.035, 0.04]
    })
    mock.get_dataframe.return_value = mock_yield_curve_data
    
    # Setup for option pricing
    mock_option_result = MagicMock()
    mock_option_result.rx2.side_effect = lambda x: {
        'price': [25.32],
        'delta': [0.65],
        'gamma': [0.02],
        'theta': [-0.15],
        'vega': [0.35]
    }[x]
    
    # Setup for portfolio metrics
    mock_portfolio_result = MagicMock()
    mock_portfolio_result.rx2.side_effect = lambda x: {
        'expected_return': [0.08],
        'volatility': [0.12],
        'sharpe_ratio': [0.67]
    }[x]
    
    # Switch call_function results based on function name
    def mock_call_function(func_name, **kwargs):
        if func_name == 'calculate_yield_curve':
            return MagicMock()  # Yield curve uses get_dataframe
        elif func_name == 'price_option':
            return mock_option_result
        elif func_name == 'calculate_portfolio_metrics':
            return mock_portfolio_result
        return None
    
    mock.call_function.side_effect = mock_call_function
    
    return mock


@pytest.fixture
def mock_get_r_service(mock_r_service):
    """Mock the get_r_service function to return our mock."""
    with patch('services.finance.finance_service.get_r_service', return_value=mock_r_service):
        yield mock_r_service


@pytest.fixture
def finance_service(mock_get_r_service):
    """Create a finance service instance with mocked R service."""
    with patch('os.makedirs'):
        with patch('tempfile.mkdtemp', return_value='/tmp/test_dir'):
            return FinanceService(data_dir='/test/finance/data')


class TestFinanceService:
    """Test cases for the FinanceService class."""
    
    def test_init(self, finance_service):
        """Test initialization of finance service."""
        assert finance_service.data_dir == '/test/finance/data'
        assert finance_service.temp_dir == '/tmp/test_dir'
        assert finance_service.yield_curve_script_path == 'finance/yield_curve.R'
        assert finance_service.option_pricing_script_path == 'finance/option_pricing.R'
        assert finance_service.portfolio_script_path == 'finance/portfolio.R'
    
    def test_is_r_available(self, finance_service, mock_get_r_service):
        """Test is_r_available method."""
        mock_get_r_service.is_available.return_value = True
        
        result = finance_service.is_r_available()
        
        assert result is True
        mock_get_r_service.is_available.assert_called_once()
    
    def test_calculate_yield_curve_success(self, finance_service, mock_get_r_service):
        """Test calculate_yield_curve method for successful calculation."""
        # Call the method
        result = finance_service.calculate_yield_curve(
            start_date='2023-01-01',
            end_date='2023-01-31',
            curve_type='nominal'
        )
        
        # Verify R service interactions
        mock_get_r_service.execute_script.assert_called_with('finance/yield_curve.R')
        mock_get_r_service.call_function.assert_called_with(
            'calculate_yield_curve',
            start_date='2023-01-01',
            end_date='2023-01-31',
            curve_type='nominal'
        )
        mock_get_r_service.get_dataframe.assert_called_with('yield_curve_data')
        
        # Verify the result
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        assert list(result.columns) == ['Date', 'Maturity', 'Yield']
    
    def test_calculate_yield_curve_invalid_date(self, finance_service):
        """Test calculate_yield_curve method with invalid date format."""
        with pytest.raises(ServiceError) as excinfo:
            finance_service.calculate_yield_curve(
                start_date='01/01/2023',  # Invalid format, should be YYYY-MM-DD
                end_date='2023-01-31',
                curve_type='nominal'
            )
        
        assert "Invalid date format" in str(excinfo.value)
    
    def test_calculate_yield_curve_r_error(self, finance_service, mock_get_r_service):
        """Test calculate_yield_curve method when R calculation fails."""
        # Setup R service to return None
        mock_get_r_service.call_function.return_value = None
        mock_get_r_service.get_dataframe.side_effect = ServiceError(
            "Failed to get dataframe",
            service="R",
            operation="get_dataframe"
        )
        
        # Call the method - should fall back to sample data
        result = finance_service.calculate_yield_curve(
            start_date='2023-01-01',
            end_date='2023-01-31',
            curve_type='nominal'
        )
        
        # Verify result is a fallback DataFrame
        assert isinstance(result, pd.DataFrame)
        assert 'Date' in result.columns
        assert 'Maturity' in result.columns
        assert 'Yield' in result.columns
    
    def test_generate_sample_yield_curve(self, finance_service):
        """Test _generate_sample_yield_curve method."""
        result = finance_service._generate_sample_yield_curve(
            start_date='2023-01-01',
            end_date='2023-01-31'
        )
        
        assert isinstance(result, pd.DataFrame)
        assert 'Date' in result.columns
        assert 'Maturity' in result.columns
        assert 'Yield' in result.columns
        assert len(result) > 0
    
    def test_price_option_success(self, finance_service, mock_get_r_service):
        """Test price_option method for successful calculation."""
        # Call the method
        result = finance_service.price_option(
            option_type='call',
            spot_price=100,
            strike_price=105,
            time_to_expiry=1.0,
            risk_free_rate=0.03,
            volatility=0.2
        )
        
        # Verify R service interactions
        mock_get_r_service.execute_script.assert_called_with('finance/option_pricing.R')
        mock_get_r_service.call_function.assert_called_with(
            'price_option',
            option_type='call',
            spot_price=100,
            strike_price=105,
            time_to_expiry=1.0,
            risk_free_rate=0.03,
            volatility=0.2,
            dividend_yield=0.0
        )
        
        # Verify the result
        assert isinstance(result, dict)
        assert 'price' in result
        assert 'delta' in result
        assert 'gamma' in result
        assert 'theta' in result
        assert 'vega' in result
        assert result['price'] == 25.32
    
    def test_price_option_invalid_type(self, finance_service):
        """Test price_option method with invalid option type."""
        with pytest.raises(ServiceError) as excinfo:
            finance_service.price_option(
                option_type='invalid',  # Should be 'call' or 'put'
                spot_price=100,
                strike_price=105,
                time_to_expiry=1.0,
                risk_free_rate=0.03,
                volatility=0.2
            )
        
        assert "Invalid option type" in str(excinfo.value)
    
    def test_price_option_invalid_parameters(self, finance_service):
        """Test price_option method with invalid parameter values."""
        # Test with negative spot price
        with pytest.raises(ServiceError) as excinfo:
            finance_service.price_option(
                option_type='call',
                spot_price=-100,  # Should be positive
                strike_price=105,
                time_to_expiry=1.0,
                risk_free_rate=0.03,
                volatility=0.2
            )
        assert "Prices must be positive" in str(excinfo.value)
        
        # Test with negative time to expiry
        with pytest.raises(ServiceError) as excinfo:
            finance_service.price_option(
                option_type='call',
                spot_price=100,
                strike_price=105,
                time_to_expiry=-1.0,  # Should be positive
                risk_free_rate=0.03,
                volatility=0.2
            )
        assert "Time to expiry must be positive" in str(excinfo.value)
        
        # Test with negative volatility
        with pytest.raises(ServiceError) as excinfo:
            finance_service.price_option(
                option_type='call',
                spot_price=100,
                strike_price=105,
                time_to_expiry=1.0,
                risk_free_rate=0.03,
                volatility=-0.2  # Should be positive
            )
        assert "Volatility must be positive" in str(excinfo.value)
    
    def test_price_option_r_error_fallback(self, finance_service, mock_get_r_service):
        """Test price_option method falls back to Python implementation when R fails."""
        # Setup R service to raise an exception
        mock_get_r_service.call_function.side_effect = Exception("R calculation failed")
        
        # Call the method - should fall back to Python implementation
        with patch.object(finance_service, '_python_black_scholes') as mock_py_bs:
            mock_py_bs.return_value = {'price': 24.0, 'delta': 0.6}
            
            result = finance_service.price_option(
                option_type='call',
                spot_price=100,
                strike_price=105,
                time_to_expiry=1.0,
                risk_free_rate=0.03,
                volatility=0.2
            )
            
            # Verify fallback was called
            mock_py_bs.assert_called_once()
            assert result['price'] == 24.0
    
    def test_python_black_scholes_call(self, finance_service):
        """Test _python_black_scholes method for call options."""
        result = finance_service._python_black_scholes(
            option_type='call',
            spot_price=100,
            strike_price=100,
            time_to_expiry=1.0,
            risk_free_rate=0.05,
            volatility=0.2
        )
        
        assert isinstance(result, dict)
        assert 'price' in result
        assert 'delta' in result
        assert 'gamma' in result
        assert 'theta' in result
        assert 'vega' in result
        assert result['price'] > 0
    
    def test_python_black_scholes_put(self, finance_service):
        """Test _python_black_scholes method for put options."""
        result = finance_service._python_black_scholes(
            option_type='put',
            spot_price=100,
            strike_price=100,
            time_to_expiry=1.0,
            risk_free_rate=0.05,
            volatility=0.2
        )
        
        assert isinstance(result, dict)
        assert 'price' in result
        assert 'delta' in result
        assert result['price'] > 0
        assert result['delta'] < 0  # Put delta is negative
    
    def test_calculate_portfolio_metrics_success(self, finance_service, mock_get_r_service):
        """Test calculate_portfolio_metrics method for successful calculation."""
        # Call the method with multiple assets
        returns = [[0.01, 0.02, -0.01], [0.02, 0.03, -0.02]]  # 2 assets, 3 time periods
        weights = [0.6, 0.4]
        
        result = finance_service.calculate_portfolio_metrics(returns, weights)
        
        # Verify R service interactions
        mock_get_r_service.execute_script.assert_called_with('finance/portfolio.R')
        
        # Verify values were set
        assert mock_get_r_service.set_variable.call_count >= 3
        
        # Verify the result
        assert isinstance(result, dict)
        assert 'expected_return' in result
        assert 'volatility' in result
        assert 'sharpe_ratio' in result
        assert result['expected_return'] == 0.08
        assert result['volatility'] == 0.12
        assert result['sharpe_ratio'] == 0.67
    
    def test_calculate_portfolio_metrics_single_series(self, finance_service):
        """Test calculate_portfolio_metrics method with a single return series."""
        returns = [0.01, 0.02, -0.01, 0.03, -0.02]  # Single series of returns
        
        result = finance_service.calculate_portfolio_metrics(returns)
        
        # Verify the result
        assert isinstance(result, dict)
        assert 'expected_return' in result
        assert 'volatility' in result
        assert 'sharpe_ratio' in result
    
    def test_calculate_portfolio_metrics_r_error_fallback(self, finance_service, mock_get_r_service):
        """Test calculate_portfolio_metrics method falls back to Python when R fails."""
        # Setup R service to raise an exception
        mock_get_r_service.call_function.side_effect = Exception("R calculation failed")
        
        # Call the method with multiple assets
        returns = [[0.01, 0.02, -0.01], [0.02, 0.03, -0.02]]
        weights = [0.6, 0.4]
        
        # Patch the fallback methods
        with patch.object(finance_service, '_calculate_portfolio_metrics_python') as mock_py_port:
            mock_py_port.return_value = {
                'expected_return': 0.075,
                'volatility': 0.11,
                'sharpe_ratio': 0.68
            }
            
            result = finance_service.calculate_portfolio_metrics(returns, weights)
            
            # Verify fallback was called
            mock_py_port.assert_called_once()
            assert result['expected_return'] == 0.075
    
    def test_calculate_series_metrics(self, finance_service):
        """Test _calculate_series_metrics method."""
        returns = np.array([0.01, 0.02, -0.01, 0.03, -0.02])
        
        result = finance_service._calculate_series_metrics(returns)
        
        assert isinstance(result, dict)
        assert 'expected_return' in result
        assert 'volatility' in result
        assert 'sharpe_ratio' in result
        assert result['expected_return'] == returns.mean()
        assert result['volatility'] == returns.std()
    
    def test_calculate_portfolio_metrics_python(self, finance_service):
        """Test _calculate_portfolio_metrics_python method."""
        returns = np.array([[0.01, 0.02, -0.01], [0.02, 0.03, -0.02]]).T  # 3 time periods, 2 assets
        weights = [0.6, 0.4]
        
        result = finance_service._calculate_portfolio_metrics_python(returns, weights)
        
        assert isinstance(result, dict)
        assert 'expected_return' in result
        assert 'volatility' in result
        assert 'sharpe_ratio' in result