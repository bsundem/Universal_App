"""
Finance Service Interface module.

Defines the protocol for financial calculation services.
"""
from typing import Protocol, Any, Optional, Dict, List, Union, Tuple
from pandas import DataFrame


class FinanceServiceInterface(Protocol):
    """
    Protocol defining the interface for finance services.
    
    This interface defines the contract that any finance service implementation
    must fulfill, allowing for different implementations (like mock services for testing).
    """
    
    def is_r_available(self) -> bool:
        """
        Check if R integration is available for financial calculations.
        
        Returns:
            True if R is available, False otherwise
        """
        ...
    
    def calculate_yield_curve(
        self, 
        start_date: str, 
        end_date: str, 
        curve_type: str
    ) -> DataFrame:
        """
        Calculate yield curve data.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            curve_type: Type of yield curve to calculate
            
        Returns:
            DataFrame with yield curve data
        """
        ...
    
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
        """
        ...
        
    def calculate_portfolio_metrics(
        self,
        returns: List[float],
        weights: Optional[List[float]] = None
    ) -> Dict[str, float]:
        """
        Calculate portfolio risk/return metrics.
        
        Args:
            returns: List of asset returns
            weights: List of asset weights (equal if not provided)
            
        Returns:
            Dictionary with portfolio metrics
        """
        ...