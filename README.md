# Universal App

A modern application framework built with SOLID architecture principles, providing unified services for actuarial and financial calculations with visualizations.

## Overview

Universal App is a Python-based application that demonstrates clean architecture with strict separation of concerns. It includes:

- Modern UI with ttkbootstrap styling
- Service-oriented architecture with dependency injection
- R integration for advanced statistical calculations 
- Comprehensive error handling and logging

## Features

- **Actuarial Tools**
  - Mortality table visualization
  - Present value calculator for annuities
  
- **Finance Tools**
  - Yield curve visualization (3D and line plots)
  - Options pricing calculator with Greeks

## Getting Started

### Prerequisites

- Python 3.8+
- R (for statistical calculations)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/Universal_App.git
   cd Universal_App
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a configuration file (optional):
   ```bash
   cp config.json.template config.json
   ```

5. Run the application:
   ```bash
   python run.py
   ```

## Architecture

The Universal App follows SOLID design principles and clean architecture patterns:

### Project Structure

```
Universal_App/
├── config.json                 # Configuration file
├── core/                       # Core application functionality
│   ├── app.py                  # Main application class
│   └── config.py               # Configuration management
├── data/                       # Data storage
│   ├── actuarial/              # Actuarial data
│   └── finance/                # Finance data
├── r_scripts/                  # R scripts for calculations
│   ├── actuarial/              # Actuarial calculations
│   │   ├── mortality.R         # Mortality table calculations
│   │   └── present_value.R     # Present value calculations
│   └── finance/                # Finance calculations
│       ├── yield_curve.R       # Yield curve functions
│       ├── option_pricing.R    # Option pricing models
│       └── portfolio.R         # Portfolio analysis
├── services/                   # Business logic services
│   ├── interfaces/             # Service interfaces (protocols)
│   │   ├── r_service.py        # R service interface
│   │   ├── actuarial_service.py # Actuarial service interface
│   │   └── finance_service.py  # Finance service interface
│   ├── actuarial/              # Actuarial service implementations
│   │   └── actuarial_service.py # Actuarial service
│   ├── finance/                # Finance service implementations
│   │   └── finance_service.py  # Finance service
│   ├── container.py            # Dependency injection container
│   └── r_service.py            # R integration service
├── ui/                         # User interface components
│   ├── components/             # Reusable UI components
│   │   ├── page_container.py   # Base page container
│   │   └── sidebar.py          # Navigation sidebar
│   ├── pages/                  # Application pages
│   │   ├── home_page.py        # Home/dashboard page
│   │   ├── actuarial_page.py   # Actuarial tools page
│   │   └── finance_page.py     # Finance tools page
│   └── main_window.py          # Main application window
├── utils/                      # Utility functions
│   ├── error_handling.py       # Error handling utilities
│   └── logging.py              # Logging utilities
├── requirements.txt            # Python dependencies
└── run.py                      # Application entry point
```

## Developer Guide

### SOLID Design Principles

1. **Single Responsibility Principle**
   - Each class has a single responsibility
   - UI components handle only presentation
   - Services handle only business logic

2. **Open/Closed Principle**
   - Classes are open for extension but closed for modification
   - Service interfaces allow new implementations without changing existing code

3. **Liskov Substitution Principle**
   - Implementations can be substituted for their interfaces
   - Error handling and logging work consistently across implementations

4. **Interface Segregation Principle**
   - Focused interfaces ensure clients depend only on what they use
   - UI components only use the services they need

5. **Dependency Inversion Principle**
   - High-level modules depend on abstractions, not implementations
   - UI components depend on service interfaces, not concrete classes
   - Dependency injection container manages service instantiation

### Adding a New Service

1. Define a service interface in `services/interfaces/`:

```python
from typing import Protocol, Any

class MyServiceInterface(Protocol):
    """Protocol for my new service."""
    
    def my_method(self, param: str) -> Any:
        """Method documentation."""
        ...
```

2. Implement the service in a dedicated module:

```python
from services.interfaces.my_service import MyServiceInterface
from utils.error_handling import handle_service_errors

class MyService:
    """Implementation of my service."""
    
    def __init__(self):
        """Initialize the service."""
        pass
        
    @handle_service_errors("MyService")
    def my_method(self, param: str) -> Any:
        """Implementation of my_method."""
        # Implementation here
        return result
```

3. Register the service in the container (`services/container.py`):

```python
# Add to Container class
my_service = providers.Singleton(MyService)

# Add helper function
def get_my_service() -> MyService:
    """Get my service instance."""
    return container.get_container().my_service()
```

### Adding a New Page

1. Create a new page class in `ui/pages/`:

```python
from ui.components.page_container import PageContainer

class MyPage(PageContainer):
    """My new page."""
    
    def __init__(self, parent, navigation_callback=None):
        """Initialize the page."""
        super().__init__(
            parent,
            page_id="my_page",
            title="My Page",
            navigation_callback=navigation_callback
        )
        
        # Initialize services
        self.my_service = get_my_service()
        
        # Set up content
        self.setup_content()
        
    def setup_content(self):
        """Set up the page content."""
        # Create UI components here
        pass
```

2. Register the page in `main_window.py`:

```python
# In _setup_pages method
self.pages['my_page'] = MyPage(
    self.content_frame,
    navigation_callback=self.navigate
)

# Add to sidebar
self.sidebar.add_item("my_page", "My Page", row=position)
```

### Working with R Integration

The Universal App uses `rpy2` to integrate with R. To create new R functionality:

1. **Create an R Script**: Add your R functions in a script file under `r_scripts/`:

```R
# r_scripts/my_module/my_calculation.R

# Define an R function
perform_calculation <- function(input1, input2) {
    # R calculations here
    result <- data.frame(
        value1 = input1 * 2,
        value2 = input2 * 3
    )
    return(result)
}
```

2. **Call from Python**: Use the R service to execute your functions:

```python
from services.container import get_r_service

# Get the R service
r_service = get_r_service()

# Execute the R script
r_service.execute_script("my_module/my_calculation.R")

# Call the R function
result = r_service.call_function(
    "perform_calculation", 
    input1=10, 
    input2=20
)

# Convert to pandas DataFrame
df = r_service.get_dataframe("result")
```

### Error Handling

Use the `@handle_service_errors` decorator for service methods:

```python
@handle_service_errors("MyService")
def my_method(self):
    # Implementation that might raise exceptions
    pass
```

In UI components, use try/except with the page's error display:

```python
try:
    result = self.my_service.my_method()
    # Handle successful result
except Exception as e:
    self.show_error(f"Operation failed: {str(e)}")
    logger.error(f"Error in my_method: {e}", exc_info=True)
```

### Logging

Get a logger for your module:

```python
import logging

logger = logging.getLogger(__name__)

# Or for services:
from utils.logging import ServiceLogger
logger = ServiceLogger("my_service")

# Usage
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message", exc_info=True)
```

## Running Tests

The project is set up for testing with pytest:

```bash
# Install test dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Run tests with coverage
pytest --cov=core --cov=services --cov=ui --cov=utils

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.