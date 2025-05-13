# Actuarial Service

This document provides documentation for the Actuarial Service module in the Universal App.

## Overview

The Actuarial Service provides actuarial calculations and visualizations through a combination of Python implementations and R script integration. It follows the SOLID principles with a clean interface design and dependency injection.

## Service Interface

The Actuarial Service implements the `ActuarialServiceInterface` protocol:

```python
class ActuarialServiceInterface(Protocol):
    """Protocol defining the interface for actuarial services."""
    
    def calculate_mortality(self, age: int, gender: str, smoker: bool) -> Dict[str, Any]:
        """
        Calculate mortality probabilities based on age, gender, and smoking status.
        
        Args:
            age: Age of the individual
            gender: Gender of the individual ('M' or 'F')
            smoker: Whether the individual is a smoker
            
        Returns:
            Dictionary containing mortality data and metadata
        """
        ...
    
    def calculate_present_value(self, 
                              cashflows: List[float], 
                              times: List[float], 
                              interest_rate: float) -> Dict[str, Any]:
        """
        Calculate the present value of a series of cashflows.
        
        Args:
            cashflows: List of cashflow amounts
            times: List of times when cashflows occur (in years)
            interest_rate: Annual interest rate for discounting
            
        Returns:
            Dictionary containing present value and related metrics
        """
        ...
    
    def calculate_life_expectancy(self, age: int, gender: str, smoker: bool) -> Dict[str, Any]:
        """
        Calculate life expectancy based on age, gender, and smoking status.
        
        Args:
            age: Age of the individual
            gender: Gender of the individual ('M' or 'F')
            smoker: Whether the individual is a smoker
            
        Returns:
            Dictionary containing life expectancy and related metrics
        """
        ...
    
    def generate_actuarial_visualization(self, data_type: str, data: Dict[str, Any]) -> bytes:
        """
        Generate a visualization for actuarial data.
        
        Args:
            data_type: Type of visualization to generate
            data: Data for the visualization
            
        Returns:
            Visualization as bytes (PNG format)
        """
        ...
```

## Implementation

The Actuarial Service implementation provides:

1. **Mortality Calculations**:
   - Age-based mortality rates
   - Gender-specific mortality tables
   - Smoker/non-smoker adjustments
   - Projected mortality improvements

2. **Present Value Calculations**:
   - Discounted cashflow analysis
   - Annuity calculations
   - Term structure considerations
   - Sensitivity analysis

3. **Life Expectancy Projections**:
   - Expected remaining lifetime
   - Cohort-based projections
   - Probability of survival to specific ages
   - Standard deviation of lifetime

4. **Actuarial Visualizations**:
   - Mortality curves
   - Survival probabilities
   - Present value graphs
   - Age-based analysis charts

## R Integration

The Actuarial Service leverages R scripts for specialized calculations:

- `mortality.R`: Advanced mortality table calculations including select and ultimate tables
- `present_value.R`: Complex present value calculations with stochastic interest rates
- `life_expectancy.R`: Life expectancy projections with mortality improvements

Example R script usage:

```python
from services.container import get_r_service

r_service = get_r_service()
result = r_service.execute_script(
    "actuarial/mortality.R",
    params={
        "age": 45,
        "gender": "M",
        "smoker": True,
        "table": "2012IAM"
    }
)
```

## Fallback Mechanism

For reliability, the Actuarial Service includes Python implementations as fallbacks when R is unavailable:

```python
def calculate_mortality(self, age: int, gender: str, smoker: bool) -> Dict[str, Any]:
    """Calculate mortality based on age, gender, and smoking status."""
    try:
        # Try using R for advanced calculations
        result = self.r_service.execute_script(
            "actuarial/mortality.R",
            params={"age": age, "gender": gender, "smoker": smoker}
        )
        return result
    except Exception as e:
        self.logger.warning(f"R calculation failed, using Python fallback: {e}")
        # Fallback to Python implementation
        return self._calculate_mortality_python(age, gender, smoker)
```

## Usage Example

```python
from services.container import get_actuarial_service

# Get the service
actuarial_service = get_actuarial_service()

# Calculate mortality
mortality_result = actuarial_service.calculate_mortality(
    age=65,
    gender="F",
    smoker=False
)

print(f"Mortality rate: {mortality_result['mortality_rate']}")
print(f"Table used: {mortality_result['table']}")

# Calculate present value
pv_result = actuarial_service.calculate_present_value(
    cashflows=[100, 100, 100, 100, 100],
    times=[1, 2, 3, 4, 5],
    interest_rate=0.03
)

print(f"Present value: {pv_result['present_value']}")
print(f"Duration: {pv_result['duration']}")

# Calculate life expectancy
le_result = actuarial_service.calculate_life_expectancy(
    age=45,
    gender="M",
    smoker=False
)

print(f"Life expectancy: {le_result['life_expectancy']} years")
print(f"Probability of living to age 85: {le_result['survival_probabilities']['85']}")

# Generate visualization
viz_data = {
    "age_range": range(20, 100),
    "gender": "F",
    "smoker": False
}

image_bytes = actuarial_service.generate_actuarial_visualization(
    data_type="mortality_curve", 
    data=viz_data
)

# Save visualization
with open("mortality_curve.png", "wb") as f:
    f.write(image_bytes)
```

## User Interface Integration

The Actuarial Service is integrated into the UI through the Actuarial Page:

- Mortality calculator with interactive parameters
- Present value calculator with visualization
- Life expectancy projections with probability charts
- Interactive mortality tables with filtering options

## Testing

The Actuarial Service includes comprehensive tests:

- Unit tests for all calculation methods
- Integration tests for R script integration
- Mock tests for UI integration
- Validation tests against industry-standard tables

Example test:

```python
def test_present_value_calculation(mock_r_service):
    # Setup
    actuarial_service = get_actuarial_service()
    
    # Test
    result = actuarial_service.calculate_present_value(
        cashflows=[100, 100, 100, 100, 100],
        times=[1, 2, 3, 4, 5],
        interest_rate=0.03
    )
    
    # Assert
    assert "present_value" in result
    assert "duration" in result
    # Verify the calculation is correct (sum of discounted cashflows)
    expected_pv = sum(100 / (1.03 ** t) for t in range(1, 6))
    assert abs(result["present_value"] - expected_pv) < 0.01
```