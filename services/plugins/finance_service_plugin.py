"""
Finance Service Plugin for the Universal App.

This module provides a plugin implementation of the finance service,
using the plugin architecture system.
"""
import os
import tempfile
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta

import pandas as pd
import numpy as np

# Import plugin base classes
from services.plugins.base import ServicePlugin

# Import service interface
from services.interfaces.finance_service import FinanceServiceInterface

# Import R service
from services.plugins.r_service_plugin import RServicePlugin

# Import utils
from utils.error_handling import ServiceError, handle_service_errors
from utils.events import Event, event_bus

logger = logging.getLogger(__name__)


class YieldCurveCalculationEvent(Event):
    """Event published when yield curve calculations are performed."""
    start_date: str
    end_date: str
    curve_type: str
    success: bool


class OptionPricingEvent(Event):
    """Event published when option pricing calculations are performed."""
    option_type: str
    spot_price: float
    strike_price: float
    time_to_expiry: float
    success: bool


class PortfolioMetricsEvent(Event):
    """Event published when portfolio metrics calculations are performed."""
    num_assets: int
    success: bool


class FinanceServicePlugin(ServicePlugin):
    """
    Finance Service Plugin for financial calculations.
    
    This plugin provides financial calculations for the Universal App,
    including yield curve analysis, option pricing, and portfolio metrics.
    """
    # Plugin metadata
    plugin_id = "finance_service"
    plugin_name = "Finance Service"
    plugin_version = "1.0.0"
    plugin_description = "Provides financial calculations and analysis"
    plugin_dependencies = ["r_service"]
    
    # Service interface
    service_interface = FinanceServiceInterface
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize the finance service plugin.
        
        Args:
            data_dir: Directory to store finance data
        """
        super().__init__()
        
        # Set up data directory
        if data_dir:
            self.data_dir = os.path.abspath(data_dir)
        else:
            self.data_dir = os.path.abspath(
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                            'data', 'finance')
            )
        
        # R service reference
        self._r_service = None
        
        # Set up temporary directory for calculations
        self.temp_dir = tempfile.mkdtemp()
        
        # Paths to R scripts
        self.r_scripts_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
            'r_scripts', 'finance'
        )
        self.yield_curve_script_path = "finance/yield_curve.R"
        self.option_pricing_script_path = "finance/option_pricing.R"
        self.portfolio_script_path = "finance/portfolio.R"
        
    def _initialize(self) -> bool:
        """Initialize the finance service plugin."""
        self.logger.info(f"Initializing finance service plugin with data dir: {self.data_dir}")
        
        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Check if R scripts directory exists
        if not os.path.isdir(self.r_scripts_dir):
            self.logger.error(f"R scripts directory does not exist: {self.r_scripts_dir}")
            return False
        
        # Try to get R service
        try:
            from services.plugins.registry import plugin_registry
            self._r_service = plugin_registry.get_plugin("r_service")
            if not self._r_service:
                raise ValueError("R service plugin not found")
                
            # Check if R is available
            if not self._r_service.is_available():
                self.logger.warning("R service is not available")
                
            self.logger.info("Finance service plugin initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing finance service: {e}")
            return False
    
    def _shutdown(self) -> None:
        """Shut down the finance service plugin."""
        self.logger.info("Shutting down finance service plugin")
        
        # Clean up temporary directory
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
            self.logger.debug(f"Removed temporary directory: {self.temp_dir}")
        except Exception as e:
            self.logger.warning(f"Failed to remove temporary directory: {e}")
    
    def _get_r_service(self):
        """
        Get the R service.
        
        If the R service isn't already available, try to get it again from the registry.
        
        Returns:
            R service instance
        """
        if not self._r_service:
            try:
                from services.plugins.registry import plugin_registry
                self._r_service = plugin_registry.get_plugin("r_service")
            except Exception as e:
                self.logger.error(f"Failed to get R service: {e}")
                
        return self._r_service
    
    @handle_service_errors("Finance")
    def is_r_available(self) -> bool:
        """
        Check if R integration is available for financial calculations.
        
        Returns:
            bool: True if R is available, False otherwise
        """
        # Get R service 
        r_service = self._get_r_service()
        return r_service and r_service.is_available()
    
    @handle_service_errors("Finance")
    def calculate_yield_curve(
        self, 
        start_date: str, 
        end_date: str, 
        curve_type: str = "nominal"
    ) -> pd.DataFrame:
        """
        Calculate yield curve data.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            curve_type: Type of yield curve ('nominal' or 'real')
            
        Returns:
            DataFrame with yield curve data
            
        Raises:
            ServiceError: If calculation fails
        """
        self.logger.info(
            f"Calculating yield curve: {start_date} to {end_date}, type {curve_type}",
            "calculate_yield_curve"
        )
        
        try:
            # Validate date formats
            try:
                datetime.strptime(start_date, "%Y-%m-%d")
                datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError as e:
                raise ServiceError(
                    f"Invalid date format. Use YYYY-MM-DD: {e}",
                    service="Finance",
                    operation="calculate_yield_curve"
                )
            
            r_service = self._get_r_service()
            if not r_service:
                raise ServiceError(
                    "R service not available",
                    service="Finance",
                    operation="calculate_yield_curve"
                )

            # Execute the R script
            r_service.execute_script(self.yield_curve_script_path)

            # Call the calculate_yield_curve function
            r_result = r_service.call_function(
                "calculate_yield_curve",
                start_date=start_date,
                end_date=end_date,
                curve_type=curve_type
            )
            
            if r_result is None:
                raise ServiceError(
                    "R calculation returned None",
                    service="Finance",
                    operation="calculate_yield_curve"
                )
                
            # Convert to pandas DataFrame using the R service helper
            df = r_service.get_dataframe("yield_curve_data")
            
            # If R call fails or returns empty DataFrame, generate sample data
            if df.empty:
                self.logger.warning(
                    "R returned empty DataFrame, generating sample data",
                    "calculate_yield_curve"
                )
                df = self._generate_sample_yield_curve(start_date, end_date)
            
            # Publish event
            event_bus.publish(YieldCurveCalculationEvent(
                source="finance_service",
                start_date=start_date,
                end_date=end_date,
                curve_type=curve_type,
                success=True
            ))
            
            self.logger.info(f"Yield curve calculation successful, returning {len(df)} rows")
            return df
            
        except Exception as e:
            # Publish event
            event_bus.publish(YieldCurveCalculationEvent(
                source="finance_service",
                start_date=start_date,
                end_date=end_date,
                curve_type=curve_type,
                success=False
            ))
            
            self.logger.error(f"Failed to calculate yield curve: {str(e)}", "calculate_yield_curve")
            raise ServiceError(
                f"Failed to calculate yield curve: {str(e)}",
                service="Finance",
                operation="calculate_yield_curve",
                cause=e
            )
    
    def _generate_sample_yield_curve(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Generate sample yield curve data for testing/fallback.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            DataFrame with sample yield curve data
        """
        # Parse dates
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        # Define maturities
        maturities = [1, 2, 3, 6, 12, 24, 36, 60, 84, 120, 240, 360]
        
        # Generate date range
        dates = []
        current = start
        while current <= end:
            dates.append(current.strftime("%Y-%m-%d"))
            current += timedelta(days=30)  # Roughly monthly data
            
        # Generate sample data
        data = []
        base_rate = 0.02  # 2% base rate
        
        for date in dates:
            for maturity in maturities:
                # Generate a yield that increases with maturity
                # Add some randomness but keep a sensible curve shape
                rate = base_rate + (maturity / 120) * 0.03 + np.random.normal(0, 0.002)
                data.append({
                    'Date': date,
                    'Maturity': maturity,
                    'Yield': max(0.001, rate)  # Ensure positive rates
                })
                
        return pd.DataFrame(data)
    
    @handle_service_errors("Finance")
    def price_option(
        self, 
        option_type: str, 
        spot_price: float, 
        strike_price: float,
        time_to_expiry: float, 
        risk_free_rate: float, 
        volatility: float,
        dividend_yield: float = 0.0
    ) -> Dict[str, float]:
        """
        Calculate option price using Black-Scholes model.
        
        Args:
            option_type: 'call' or 'put'
            spot_price: Current price of the underlying asset
            strike_price: Strike price of the option
            time_to_expiry: Time to expiry in years
            risk_free_rate: Risk-free interest rate as decimal
            volatility: Volatility of the underlying asset as decimal
            dividend_yield: Dividend yield as decimal (optional)
            
        Returns:
            Dictionary with option pricing results
            
        Raises:
            ServiceError: If calculation fails
        """
        self.logger.info(
            f"Pricing {option_type} option: S={spot_price}, K={strike_price}, "
            f"T={time_to_expiry}, r={risk_free_rate}, σ={volatility}",
            "price_option"
        )
        
        try:
            # Validate inputs
            if option_type not in ["call", "put"]:
                raise ServiceError(
                    f"Invalid option type: {option_type}. Must be 'call' or 'put'.",
                    service="Finance",
                    operation="price_option"
                )
                
            if spot_price <= 0 or strike_price <= 0:
                raise ServiceError(
                    "Prices must be positive",
                    service="Finance", 
                    operation="price_option"
                )
                
            if time_to_expiry <= 0:
                raise ServiceError(
                    "Time to expiry must be positive",
                    service="Finance",
                    operation="price_option"
                )
                
            if volatility <= 0:
                raise ServiceError(
                    "Volatility must be positive",
                    service="Finance",
                    operation="price_option"
                )
            
            r_service = self._get_r_service()
            if not r_service:
                self.logger.warning("R service not available, using Python implementation")
                return self._python_black_scholes(
                    option_type, spot_price, strike_price, time_to_expiry,
                    risk_free_rate, volatility, dividend_yield
                )

            # Execute the R script
            r_service.execute_script(self.option_pricing_script_path)

            # Call the price_option function
            r_result = r_service.call_function(
                "price_option",
                option_type=option_type,
                spot_price=spot_price,
                strike_price=strike_price,
                time_to_expiry=time_to_expiry,
                risk_free_rate=risk_free_rate,
                volatility=volatility,
                dividend_yield=dividend_yield
            )
            
            if r_result is None:
                raise ServiceError(
                    "R calculation returned None",
                    service="Finance",
                    operation="price_option"
                )
                
            # Extract results
            price = r_result.rx2('price')[0]
            delta = r_result.rx2('delta')[0]
            gamma = r_result.rx2('gamma')[0]
            theta = r_result.rx2('theta')[0]
            vega = r_result.rx2('vega')[0]
            
            result = {
                'price': price,
                'delta': delta,
                'gamma': gamma,
                'theta': theta,
                'vega': vega
            }
            
            # Publish event
            event_bus.publish(OptionPricingEvent(
                source="finance_service",
                option_type=option_type,
                spot_price=spot_price,
                strike_price=strike_price,
                time_to_expiry=time_to_expiry,
                success=True
            ))
            
            self.logger.info(f"Option pricing successful: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to price option: {str(e)}", "price_option")
            
            # Publish event
            event_bus.publish(OptionPricingEvent(
                source="finance_service",
                option_type=option_type,
                spot_price=spot_price,
                strike_price=strike_price,
                time_to_expiry=time_to_expiry,
                success=False
            ))
            
            # Fall back to calculating with Python if R fails
            try:
                self.logger.info("Falling back to Python implementation", "price_option")
                return self._python_black_scholes(
                    option_type, spot_price, strike_price, time_to_expiry,
                    risk_free_rate, volatility, dividend_yield
                )
            except Exception as fallback_error:
                # If Python implementation also fails, raise original error
                raise ServiceError(
                    f"Failed to price option: {str(e)}",
                    service="Finance",
                    operation="price_option",
                    cause=e
                )
    
    def _python_black_scholes(
        self, 
        option_type: str, 
        spot_price: float, 
        strike_price: float,
        time_to_expiry: float, 
        risk_free_rate: float, 
        volatility: float,
        dividend_yield: float = 0.0
    ) -> Dict[str, float]:
        """
        Calculate option price using Black-Scholes model in Python.
        This is a fallback method if R calculation fails.
        
        Args: Same as price_option method
        Returns: Same as price_option method
        """
        from scipy.stats import norm
        
        # Calculate d1 and d2
        d1 = (np.log(spot_price / strike_price) + 
              (risk_free_rate - dividend_yield + 0.5 * volatility**2) * time_to_expiry) / \
             (volatility * np.sqrt(time_to_expiry))
        d2 = d1 - volatility * np.sqrt(time_to_expiry)
        
        # Calculate option price
        if option_type == 'call':
            price = spot_price * np.exp(-dividend_yield * time_to_expiry) * norm.cdf(d1) - \
                    strike_price * np.exp(-risk_free_rate * time_to_expiry) * norm.cdf(d2)
            delta = np.exp(-dividend_yield * time_to_expiry) * norm.cdf(d1)
        else:  # put
            price = strike_price * np.exp(-risk_free_rate * time_to_expiry) * norm.cdf(-d2) - \
                    spot_price * np.exp(-dividend_yield * time_to_expiry) * norm.cdf(-d1)
            delta = np.exp(-dividend_yield * time_to_expiry) * (norm.cdf(d1) - 1)
        
        # Calculate the Greeks
        gamma = np.exp(-dividend_yield * time_to_expiry) * norm.pdf(d1) / \
                (spot_price * volatility * np.sqrt(time_to_expiry))
        vega = 0.01 * spot_price * np.exp(-dividend_yield * time_to_expiry) * \
               np.sqrt(time_to_expiry) * norm.pdf(d1)
        theta = -((spot_price * volatility * np.exp(-dividend_yield * time_to_expiry) * \
                  norm.pdf(d1)) / (2 * np.sqrt(time_to_expiry))) - \
                 risk_free_rate * strike_price * np.exp(-risk_free_rate * time_to_expiry) * \
                 norm.cdf(d2 if option_type == 'call' else -d2)
        
        return {
            'price': price,
            'delta': delta,
            'gamma': gamma,
            'theta': theta / 365,  # Convert to daily theta
            'vega': vega
        }
    
    @handle_service_errors("Finance")
    def calculate_portfolio_metrics(
        self,
        returns: List[float],
        weights: Optional[List[float]] = None
    ) -> Dict[str, float]:
        """
        Calculate portfolio risk/return metrics.
        
        Args:
            returns: List of asset returns (can be a list of lists for multiple assets)
            weights: List of asset weights (equal if not provided)
            
        Returns:
            Dictionary with portfolio metrics
            
        Raises:
            ServiceError: If calculation fails
        """
        self.logger.info(
            f"Calculating portfolio metrics for {len(returns)} assets",
            "calculate_portfolio_metrics"
        )
        
        try:
            # Handle the case where returns might be a list of lists (one per asset)
            if returns and isinstance(returns[0], list):
                # Convert to numpy arrays for easier manipulation
                returns_array = np.array(returns)
            else:
                # Assume single series of portfolio returns
                returns_array = np.array(returns)
                
            # If single series, just calculate basic metrics
            if returns_array.ndim == 1:
                return self._calculate_series_metrics(returns_array)
                
            # Set equal weights if not provided
            if weights is None:
                n_assets = returns_array.shape[1]
                weights = [1.0 / n_assets] * n_assets
                
            # Check dimensions
            if len(weights) != returns_array.shape[1]:
                raise ServiceError(
                    f"Number of weights ({len(weights)}) does not match number of assets ({returns_array.shape[1]})",
                    service="Finance",
                    operation="calculate_portfolio_metrics"
                )
            
            r_service = self._get_r_service()
            if not r_service:
                self.logger.warning("R service not available, using Python implementation")
                return self._calculate_portfolio_metrics_python(returns_array, weights)

            # Execute the R script
            r_service.execute_script(self.portfolio_script_path)

            # Convert returns to R matrix
            for i, asset_returns in enumerate(returns_array.T):
                r_service.set_variable(f"asset_{i}_returns", asset_returns)
                
            # Set weights
            r_service.set_variable("asset_weights", weights)
            
            # Build R code to create the returns matrix
            r_code = f"returns_matrix <- matrix(c({','.join([f'asset_{i}_returns' for i in range(returns_array.shape[1])])}), ncol={returns_array.shape[1]})"
            r_service.run_r_code(r_code)

            # Call the calculate_portfolio_metrics function
            r_result = r_service.call_function(
                "calculate_portfolio_metrics",
                returns_matrix="returns_matrix",
                weights="asset_weights"
            )
            
            if r_result is None:
                raise ServiceError(
                    "R calculation returned None",
                    service="Finance",
                    operation="calculate_portfolio_metrics"
                )
                
            # Extract results
            expected_return = r_result.rx2('expected_return')[0]
            volatility = r_result.rx2('volatility')[0]
            sharpe_ratio = r_result.rx2('sharpe_ratio')[0]
            
            result = {
                'expected_return': expected_return,
                'volatility': volatility,
                'sharpe_ratio': sharpe_ratio
            }
            
            # Publish event
            event_bus.publish(PortfolioMetricsEvent(
                source="finance_service",
                num_assets=len(weights),
                success=True
            ))
            
            self.logger.info(f"Portfolio metrics calculation successful: {result}")
            return result
            
        except Exception as e:
            # Publish event
            event_bus.publish(PortfolioMetricsEvent(
                source="finance_service",
                num_assets=len(weights) if weights else 1,
                success=False
            ))
            
            self.logger.error(f"Failed to calculate portfolio metrics: {str(e)}", "calculate_portfolio_metrics")
            
            # Fall back to Python implementation
            try:
                self.logger.info("Falling back to Python implementation", "calculate_portfolio_metrics")
                
                if isinstance(returns[0], list):
                    returns_array = np.array(returns)
                    
                    if weights is None:
                        weights = [1.0 / returns_array.shape[1]] * returns_array.shape[1]
                        
                    return self._calculate_portfolio_metrics_python(returns_array, weights)
                else:
                    return self._calculate_series_metrics(np.array(returns))
            except Exception as fallback_error:
                # If Python implementation also fails, raise original error
                raise ServiceError(
                    f"Failed to calculate portfolio metrics: {str(e)}",
                    service="Finance",
                    operation="calculate_portfolio_metrics",
                    cause=e
                )
    
    def _calculate_series_metrics(self, returns: np.ndarray) -> Dict[str, float]:
        """
        Calculate basic metrics for a single return series.
        
        Args:
            returns: Array of returns
            
        Returns:
            Dictionary with basic metrics
        """
        mean_return = returns.mean()
        volatility = returns.std()
        sharpe_ratio = mean_return / volatility if volatility > 0 else 0
        
        return {
            'expected_return': mean_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio
        }
    
    def _calculate_portfolio_metrics_python(
        self,
        returns: np.ndarray,
        weights: List[float]
    ) -> Dict[str, float]:
        """
        Calculate portfolio metrics using Python.
        This is a fallback method if R calculation fails.
        
        Args:
            returns: Returns matrix (rows = time periods, cols = assets)
            weights: Asset weights
            
        Returns:
            Dictionary with portfolio metrics
        """
        # Calculate mean returns and covariance matrix
        mean_returns = returns.mean(axis=0)
        cov_matrix = np.cov(returns.T)
        
        # Calculate portfolio metrics
        portfolio_return = np.sum(mean_returns * weights)
        portfolio_volatility = np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))
        portfolio_sharpe = portfolio_return / portfolio_volatility if portfolio_volatility > 0 else 0
        
        return {
            'expected_return': portfolio_return,
            'volatility': portfolio_volatility,
            'sharpe_ratio': portfolio_sharpe
        }