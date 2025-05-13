# Finance Service

This document provides documentation for the Finance Service module in the Universal App.

## Overview

The Finance Service provides financial calculations and visualizations through a combination of Python implementations and R script integration. It follows the SOLID principles with a clean interface design and dependency injection.

## Service Interface

The Finance Service implements the `FinanceServiceInterface` protocol:

```python
class FinanceServiceInterface(Protocol):
    """Protocol defining the interface for finance services."""
    
    def calculate_yield_curve(self, rates: Dict[str, float], dates: List[str]) -> Dict[str, Any]:
        """
        Calculate yield curve based on provided rates and dates.
        
        Args:
            rates: Dictionary of rates with maturity as keys
            dates: List of dates for the yield curve
            
        Returns:
            Dictionary containing yield curve data and metadata
        """
        ...
    
    def price_option(self, 
                    option_type: str,
                    strike_price: float, 
                    current_price: float, 
                    time_to_expiry: float, 
                    volatility: float, 
                    risk_free_rate: float) -> Dict[str, Any]:
        """
        Calculate option price using Black-Scholes model.
        
        Args:
            option_type: Type of option ('call' or 'put')
            strike_price: Strike price of the option
            current_price: Current price of the underlying asset
            time_to_expiry: Time to expiry in years
            volatility: Volatility of the underlying asset
            risk_free_rate: Risk-free interest rate
            
        Returns:
            Dictionary containing option price and Greeks
        """
        ...
    
    def calculate_portfolio_metrics(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate various portfolio metrics.
        
        Args:
            portfolio_data: Portfolio data with assets, weights, and historical returns
            
        Returns:
            Dictionary containing portfolio metrics (return, volatility, Sharpe ratio, etc.)
        """
        ...
    
    def generate_financial_visualization(self, data_type: str, data: Dict[str, Any]) -> bytes:
        """
        Generate a visualization for financial data.
        
        Args:
            data_type: Type of visualization to generate
            data: Data for the visualization
            
        Returns:
            Visualization as bytes (PNG format)
        """
        ...
```

## Implementation

The Finance Service implementation provides:

1. **Yield Curve Calculations**:
   - Term structure modeling
   - Interpolation methods
   - Visual representation

2. **Option Pricing Models**:
   - Black-Scholes model
   - Greeks calculations (delta, gamma, theta, vega, rho)
   - Binomial tree model as fallback

3. **Portfolio Analysis**:
   - Return calculations
   - Risk metrics (volatility, Value at Risk)
   - Performance ratios (Sharpe, Sortino)
   - Asset allocation analysis

4. **Financial Visualizations**:
   - Yield curve graphs
   - Option payoff diagrams
   - Portfolio composition charts
   - Risk/return scatter plots

## R Integration

The Finance Service leverages R scripts for advanced calculations:

- `yield_curve.R`: Advanced yield curve modeling and visualization
- `option_pricing.R`: Option pricing models including Black-Scholes and more complex models
- `portfolio_analytics.R`: Portfolio optimization and risk analysis

Example R script usage:

```python
from services.container import get_r_service

r_service = get_r_service()
result = r_service.execute_script(
    "finance/yield_curve.R",
    params={
        "rates": {"1M": 0.01, "3M": 0.015, "6M": 0.02, "1Y": 0.025, "2Y": 0.03},
        "dates": ["2023-01-01", "2023-03-01", "2023-06-01", "2024-01-01", "2025-01-01"],
    }
)
```

## Fallback Mechanism

For reliability, the Finance Service includes Python implementations as fallbacks when R is unavailable:

```python
def calculate_yield_curve(self, rates: Dict[str, float], dates: List[str]) -> Dict[str, Any]:
    """Calculate yield curve with rates and dates."""
    try:
        # Try using R for advanced calculations
        result = self.r_service.execute_script(
            "finance/yield_curve.R",
            params={"rates": rates, "dates": dates}
        )
        return result
    except Exception as e:
        self.logger.warning(f"R calculation failed, using Python fallback: {e}")
        # Fallback to Python implementation
        return self._calculate_yield_curve_python(rates, dates)
```

## Usage Example

```python
from services.container import get_finance_service

# Get the service
finance_service = get_finance_service()

# Calculate option price
option_result = finance_service.price_option(
    option_type="call",
    strike_price=100.0,
    current_price=105.0,
    time_to_expiry=1.0,
    volatility=0.2,
    risk_free_rate=0.03
)

print(f"Option price: {option_result['price']}")
print(f"Delta: {option_result['greeks']['delta']}")

# Portfolio analysis
portfolio_data = {
    "assets": ["AAPL", "MSFT", "GOOG"],
    "weights": [0.4, 0.3, 0.3],
    "returns": [...],  # Historical returns data
}

metrics = finance_service.calculate_portfolio_metrics(portfolio_data)
print(f"Expected return: {metrics['expected_return']}")
print(f"Volatility: {metrics['volatility']}")
print(f"Sharpe ratio: {metrics['sharpe_ratio']}")

# Generate visualization
viz_data = {
    "portfolio": portfolio_data,
    "benchmark": {...}  # Benchmark data
}

image_bytes = finance_service.generate_financial_visualization(
    data_type="portfolio_performance", 
    data=viz_data
)

# Save visualization
with open("portfolio_performance.png", "wb") as f:
    f.write(image_bytes)
```

## User Interface Integration

The Finance Service is integrated into the UI through the Finance Page:

- Yield curve visualization with interactive parameters
- Option pricing calculator with results and Greeks display
- Portfolio analysis tools with asset allocation visualization
- Financial metric dashboards

## Testing

The Finance Service includes comprehensive tests:

- Unit tests for all calculation methods
- Integration tests for R script integration
- Mock tests for UI integration
- Validation tests for financial calculations

Example test:

```python
def test_option_pricing(mock_r_service):
    # Setup
    finance_service = get_finance_service()
    
    # Test
    result = finance_service.price_option(
        option_type="call",
        strike_price=100,
        current_price=100,
        time_to_expiry=1,
        volatility=0.2,
        risk_free_rate=0.03
    )
    
    # Assert
    assert "price" in result
    assert "greeks" in result
    assert "delta" in result["greeks"]
    # Verify the calculation is approximately correct
    assert 7.5 <= result["price"] <= 8.5  # Approximate range for this example
```