# Universal App

A unified application framework that hosts multiple projects in a single interface. This repository serves as a container for various projects until they grow large enough to be moved into their own repositories.

## Features

- Unified navigation system
- Modular project architecture
- Tkinter-based GUI (part of Python standard library)
- Service-oriented architecture with clean interfaces
- R integration for specialized calculations
- Kaggle data exploration capabilities
- Comprehensive testing framework
- Configuration management system
- Structured error handling
- Consistent logging strategy
- Implementation of SOLID design principles

## Project Structure

```
Universal_App/
├── config.json.template     # Configuration template
├── core/                    # Core application functionality
│   ├── app.py               # Main application class
│   └── config.py            # Configuration management
├── services/                # Business logic services
│   ├── actuarial/           # Actuarial calculation services
│   ├── interfaces/          # Service interfaces (ISP)
│   ├── kaggle/              # Kaggle data services
│   ├── container.py         # Dependency injection container (DIP)
│   ├── provider.py          # Legacy service provider (being replaced)
│   └── r_service.py         # R integration service
├── r_scripts/               # R scripts for specialized calculations
│   ├── actuarial/           # Actuarial R scripts
│   └── common/              # Common R utilities
├── tests/                   # Testing framework
│   ├── unit/                # Unit tests
│   ├── integration/         # Integration tests
│   └── functional/          # Functional tests
├── ui/                      # User interface components
│   ├── components/          # Reusable UI components
│   │   └── page_container.py # Page container (composition)
│   └── pages/               # Application pages
│       ├── content_page.py  # Base content page using composition
│       ├── home_page.py     # Home page
│       ├── kaggle_page.py   # Kaggle data explorer page
│       ├── actuarial_page.py # Actuarial calculations page
│       ├── settings_page.py # Settings page
│       └── example_page.py  # Example page demonstrating composition
└── utils/                   # Utility functions and helpers
    ├── error_handling.py    # Standardized error handling
    └── logging.py           # Logging strategy
```

## Setup

### Installation

#### Basic Setup

```bash
# Create and activate a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # Unix/macOS
# or
.venv\Scripts\activate     # Windows

# Install core dependencies
pip install -e .
```

#### Development Setup

```bash
# Install with development tools (black, flake8, pytest)
pip install -e ".[dev]"

# Or install all dependencies at once using requirements.txt
pip install -r requirements.txt
```

#### Installation Options

You can install specific feature sets as needed:

```bash
# Install R integration dependencies
pip install -e ".[r]"

# Install data analysis dependencies
pip install -e ".[data]"

# Install Kaggle integration dependencies
pip install -e ".[kaggle]"

# Install all optional dependencies
pip install -e ".[all]"
```

### External Dependencies

Some features require external software:

- **R Integration**: Requires R to be installed
  ```bash
  # Install R from https://cran.r-project.org/
  # The rpy2 package will be installed automatically with the [r] extra
  ```

- **Kaggle API**: Requires authentication setup
  ```bash
  # Create a Kaggle API token at https://www.kaggle.com/account
  # Place kaggle.json in ~/.kaggle/ or use the in-app setup wizard
  ```

### Running the Application

#### Method 1: Using run.py
```bash
python run.py
```

#### Method 2: After installing the package
```bash
universal-app
```

## Development

### Adding New Projects

## Complete Guide to Extending the Application

This section provides a comprehensive guide to adding a new project module to the application, following all the architectural principles and patterns established in the codebase.

### 1. Define Service Interfaces

First, define the interfaces for your new service in the appropriate file under `services/interfaces/`:

```python
# services/interfaces/weather_services.py
from typing import Protocol, Dict, Any, List, Optional

class WeatherServiceInterface(Protocol):
    """Protocol defining the interface for weather services."""

    def get_current_weather(self, location: str) -> Dict[str, Any]:
        """
        Get current weather for a location.

        Args:
            location: Location name or coordinates

        Returns:
            Dict with weather information
        """
        ...

    def get_forecast(self, location: str, days: int = 5) -> List[Dict[str, Any]]:
        """
        Get weather forecast for a location.

        Args:
            location: Location name or coordinates
            days: Number of days to forecast

        Returns:
            List of daily forecasts
        """
        ...
```

### 2. Implement the Service

Create the service implementation in a dedicated directory:

```python
# services/weather/weather_service.py
import requests
from typing import Dict, Any, List, Optional
from utils.error_handling import ServiceError, handle_service_errors
from utils.logging import get_logger

logger = get_logger(__name__)

class WeatherService:
    """Service for retrieving weather information."""

    def __init__(self):
        """Initialize the weather service."""
        self.api_key = "YOUR_API_KEY"  # Should come from config
        self.base_url = "https://api.weatherapi.com/v1"

    @handle_service_errors("Weather")
    def get_current_weather(self, location: str) -> Dict[str, Any]:
        """
        Get current weather for a location.

        Args:
            location: Location name or coordinates

        Returns:
            Dict with weather information
        """
        endpoint = f"{self.base_url}/current.json"
        params = {
            "key": self.api_key,
            "q": location
        }

        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise ServiceError(
                message=f"Failed to get weather for {location}: {str(e)}",
                service="Weather",
                operation="get_current_weather"
            )

    @handle_service_errors("Weather")
    def get_forecast(self, location: str, days: int = 5) -> List[Dict[str, Any]]:
        """
        Get weather forecast for a location.

        Args:
            location: Location name or coordinates
            days: Number of days to forecast

        Returns:
            List of daily forecasts
        """
        endpoint = f"{self.base_url}/forecast.json"
        params = {
            "key": self.api_key,
            "q": location,
            "days": days
        }

        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("forecast", {}).get("forecastday", [])
        except requests.RequestException as e:
            raise ServiceError(
                message=f"Failed to get forecast for {location}: {str(e)}",
                service="Weather",
                operation="get_forecast"
            )

# Export a singleton instance
weather_service = WeatherService()
```

### 3. Register the Service with the Container

Update the DI container to include your new service:

```python
# services/container.py
# Add this to the imports at the top
from services.interfaces.weather_services import WeatherServiceInterface
from services.weather.weather_service import weather_service

# Add this to the Container class
class Container(containers.DeclarativeContainer):
    # Existing providers...

    # Weather services
    weather_service_provider = providers.Singleton(lambda: weather_service)

# Add this helper function
def get_weather_service() -> WeatherServiceInterface:
    """Get the weather service implementation."""
    service = container.weather_service_provider()
    if service is None:
        raise RuntimeError("Weather service is not registered with the service provider")
    return service

# Add this to initialize_provider()
def initialize_provider():
    """Initialize the service provider with default implementations."""
    # Existing registrations...

    # Register weather service
    provider.register(WeatherServiceInterface, weather_service)
```

### 4. Create a Page for the New Project

Create a new page that uses the service via the container:

```python
# ui/pages/weather_page.py
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, List, Optional

from ui.pages.content_page import ContentPage
from utils.logging import get_logger
from services.container import get_weather_service

logger = get_logger(__name__)

class WeatherPage(ContentPage):
    """Page for displaying weather information."""

    def __init__(self, parent, controller):
        super().__init__(parent, title="Weather Dashboard")
        self.controller = controller

        # Get the weather service from the container
        self.weather_service = get_weather_service()

        logger.info("WeatherPage initialized")

    def setup_ui(self):
        """Set up the UI components for the weather page."""
        # Main container frame
        main_frame = ttk.Frame(self.content_frame, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Search section
        search_frame = ttk.LabelFrame(main_frame, text="Location Search", padding=10)
        search_frame.pack(fill=tk.X, pady=(0, 10))

        # Location entry
        ttk.Label(search_frame, text="Location:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        self.location_var = tk.StringVar()
        location_entry = ttk.Entry(search_frame, textvariable=self.location_var, width=30)
        location_entry.grid(row=0, column=1, sticky=tk.W, pady=5, padx=5)

        # Search button
        search_btn = ttk.Button(
            search_frame,
            text="Get Weather",
            command=self.fetch_weather
        )
        search_btn.grid(row=0, column=2, sticky=tk.W, pady=5, padx=5)

        # Results section
        self.results_frame = ttk.LabelFrame(main_frame, text="Weather Information", padding=10)
        self.results_frame.pack(fill=tk.BOTH, expand=True)

        # Initial message
        self.info_label = ttk.Label(
            self.results_frame,
            text="Enter a location to view weather information.",
            foreground="gray"
        )
        self.info_label.pack(expand=True)

    def fetch_weather(self):
        """Fetch weather for the specified location."""
        location = self.location_var.get().strip()
        if not location:
            messagebox.showwarning("Invalid Input", "Please enter a location.")
            return

        logger.info(f"Fetching weather for location: {location}")

        try:
            # Clear results frame
            for widget in self.results_frame.winfo_children():
                widget.destroy()

            # Show loading indicator
            loading_label = ttk.Label(
                self.results_frame,
                text=f"Loading weather data for {location}...",
                foreground="blue"
            )
            loading_label.pack(expand=True)
            self.update_idletasks()

            # Use the weather service to get data
            weather_data = self.weather_service.get_current_weather(location)
            forecast_data = self.weather_service.get_forecast(location)

            # Clear loading indicator
            loading_label.destroy()

            # Display current weather
            self.display_weather_data(weather_data, forecast_data)

        except Exception as e:
            # Handle error
            for widget in self.results_frame.winfo_children():
                widget.destroy()

            error_label = ttk.Label(
                self.results_frame,
                text=f"Error fetching weather data: {str(e)}",
                foreground="red"
            )
            error_label.pack(expand=True)
            logger.error(f"Error fetching weather: {str(e)}")

    def display_weather_data(self, weather_data: Dict[str, Any], forecast_data: List[Dict[str, Any]]):
        """Display weather data in the UI."""
        # Create a frame for current weather
        current_frame = ttk.Frame(self.results_frame, padding=10)
        current_frame.pack(fill=tk.X, pady=(0, 10))

        # Extract relevant data
        try:
            location = weather_data.get("location", {})
            current = weather_data.get("current", {})

            location_name = f"{location.get('name', 'Unknown')}, {location.get('country', '')}"
            temp_c = current.get("temp_c", "N/A")
            condition = current.get("condition", {}).get("text", "Unknown")
            humidity = current.get("humidity", "N/A")
            wind_kph = current.get("wind_kph", "N/A")

            # Create display
            ttk.Label(
                current_frame,
                text=location_name,
                font=("Arial", 16, "bold")
            ).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=5)

            ttk.Label(
                current_frame,
                text=f"Temperature: {temp_c}°C",
                font=("Arial", 12)
            ).grid(row=1, column=0, sticky=tk.W, pady=2)

            ttk.Label(
                current_frame,
                text=f"Condition: {condition}",
                font=("Arial", 12)
            ).grid(row=2, column=0, sticky=tk.W, pady=2)

            ttk.Label(
                current_frame,
                text=f"Humidity: {humidity}%",
                font=("Arial", 12)
            ).grid(row=3, column=0, sticky=tk.W, pady=2)

            ttk.Label(
                current_frame,
                text=f"Wind: {wind_kph} km/h",
                font=("Arial", 12)
            ).grid(row=4, column=0, sticky=tk.W, pady=2)

            # Forecast section
            if forecast_data:
                forecast_frame = ttk.LabelFrame(self.results_frame, text="5-Day Forecast", padding=10)
                forecast_frame.pack(fill=tk.BOTH, expand=True)

                # Create headers
                ttk.Label(forecast_frame, text="Date", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=10, pady=5)
                ttk.Label(forecast_frame, text="Condition", font=("Arial", 10, "bold")).grid(row=0, column=1, padx=10, pady=5)
                ttk.Label(forecast_frame, text="Min Temp", font=("Arial", 10, "bold")).grid(row=0, column=2, padx=10, pady=5)
                ttk.Label(forecast_frame, text="Max Temp", font=("Arial", 10, "bold")).grid(row=0, column=3, padx=10, pady=5)

                # Add forecast data
                for i, day in enumerate(forecast_data, 1):
                    date = day.get("date", "Unknown")
                    condition = day.get("day", {}).get("condition", {}).get("text", "Unknown")
                    min_temp = day.get("day", {}).get("mintemp_c", "N/A")
                    max_temp = day.get("day", {}).get("maxtemp_c", "N/A")

                    ttk.Label(forecast_frame, text=date).grid(row=i, column=0, padx=10, pady=2)
                    ttk.Label(forecast_frame, text=condition).grid(row=i, column=1, padx=10, pady=2)
                    ttk.Label(forecast_frame, text=f"{min_temp}°C").grid(row=i, column=2, padx=10, pady=2)
                    ttk.Label(forecast_frame, text=f"{max_temp}°C").grid(row=i, column=3, padx=10, pady=2)

        except Exception as e:
            # Handle parsing error
            ttk.Label(
                current_frame,
                text=f"Error parsing weather data: {str(e)}",
                foreground="red"
            ).grid(row=0, column=0, pady=5)
            logger.error(f"Error parsing weather data: {str(e)}")
```

### 5. Add the Page to the Main Window

Update the `MainWindow` class to include the new page:

```python
# ui/main_window.py
# Add this import
from ui.pages.weather_page import WeatherPage

# Update setup_pages method
def setup_pages(self):
    """Setup the application pages."""
    # Create pages - all pages use ContentPage (composition)
    home_page = HomePage(self.content_frame, self)
    actuarial_page = ActuarialPage(self.content_frame, self)
    kaggle_page = KagglePage(self.content_frame, self)
    weather_page = WeatherPage(self.content_frame, self)  # Add new page
    project_three = ProjectPage(self.content_frame, "Project Three", self)
    example_page = ExamplePage(self.content_frame, self)
    settings_page = SettingsPage(self.content_frame, self)

    # Add pages to our list
    self.pages = [
        home_page,
        actuarial_page,
        kaggle_page,
        weather_page,  # Add new page
        project_three,
        example_page,
        settings_page
    ]

    # Update page names in show_page method
    page_map = {
        "home": 0,
        "actuarial": 1,
        "kaggle": 2,
        "weather": 3,  # Add new page
        "project_three": 4,
        "example": 5,
        "settings": 6
    }
```

### 6. Add to the Sidebar Navigation

Update the sidebar to include a button for the new page:

```python
# ui/components/sidebar.py
# Update _setup_navigation method

def _setup_navigation(self):
    """Set up the navigation buttons."""
    # Create buttons for pages
    self.add_nav_button("Home", 0, icon="🏠")
    self.add_nav_button("Actuarial", 1, icon="📊")
    self.add_nav_button("Kaggle", 2, icon="📈")
    self.add_nav_button("Weather", 3, icon="🌤️")  # Add new button
    self.add_nav_button("Project Three", 4, icon="📋")
    self.add_nav_button("Example", 5, icon="📝")
    self.add_nav_button("Settings", 6, icon="⚙️")
```

### 7. Create Unit Tests

Create unit tests for your new service:

```python
# tests/unit/services/test_weather_service.py
import pytest
from unittest.mock import patch, MagicMock
from services.container import get_weather_service, override_provider, reset_overrides

class TestWeatherService:
    """Test cases for the WeatherService class."""

    @pytest.fixture
    def setup_mocks(self):
        """Set up mocks for testing."""
        # Create a mock weather service
        mock_weather_service = MagicMock()
        mock_weather_service.get_current_weather.return_value = {
            "location": {"name": "London", "country": "UK"},
            "current": {"temp_c": 18.0, "condition": {"text": "Partly cloudy"}}
        }
        mock_weather_service.get_forecast.return_value = [
            {"date": "2023-05-01", "day": {"maxtemp_c": 20, "mintemp_c": 15}}
        ]

        # Override the service in the container
        override_provider("weather_service", mock_weather_service)
        yield mock_weather_service

        # Reset after test
        reset_overrides()

    def test_get_current_weather(self, setup_mocks):
        """Test getting current weather."""
        mock_service = setup_mocks

        # Get service from container (will be our mock)
        weather_service = get_weather_service()

        # Call method
        result = weather_service.get_current_weather("London")

        # Verify mock was called correctly
        mock_service.get_current_weather.assert_called_once_with("London")

        # Verify result
        assert result["location"]["name"] == "London"
        assert result["current"]["temp_c"] == 18.0

    def test_get_forecast(self, setup_mocks):
        """Test getting weather forecast."""
        mock_service = setup_mocks

        # Get service from container (will be our mock)
        weather_service = get_weather_service()

        # Call method
        result = weather_service.get_forecast("London", days=5)

        # Verify mock was called correctly
        mock_service.get_forecast.assert_called_once_with("London", days=5)

        # Verify result
        assert len(result) == 1
        assert result[0]["date"] == "2023-05-01"
```

### Summary

To add a new project module to the application:

1. **Define Service Interfaces**: Create protocol classes in `services/interfaces/`
2. **Implement Services**: Create service implementations in `services/your_module/`
3. **Register with Container**: Add services to the DI container in `services/container.py`
4. **Create UI**: Create a page class using `ContentPage` in `ui/pages/`
5. **Add to Navigation**: Update `MainWindow.setup_pages()` and `Sidebar._setup_navigation()`
6. **Write Tests**: Create unit tests for your services

This approach ensures your new module follows the established architecture, adheres to SOLID principles, and is properly integrated with the dependency injection system.

The application exclusively uses the composition pattern for page creation, which provides better flexibility and testability than inheritance.

### Services Architecture

The application follows a service-oriented architecture with interfaces:

1. UI components should delegate business logic to services
2. Services are organized by domain (e.g., `actuarial`, `kaggle`)
3. Service interfaces define contracts in `services/interfaces/`
4. Cross-cutting concerns have dedicated services (e.g., `r_service.py`)
5. Services are accessed through a dependency injection container to enforce the Dependency Inversion Principle
6. Error handling is standardized through the error handling utilities
7. Logging is consistent across all services

#### Dependency Injection Container

The application uses a proper dependency injection container to implement the Dependency Inversion Principle:

```python
from services.container import get_r_service, get_actuarial_service

# Get service implementations through the container
r_service = get_r_service()
actuarial_service = get_actuarial_service()

# Use services through their interfaces
if r_service.is_available():
    # Do something with the R service
```

This ensures that components depend on abstractions (interfaces/protocols) rather than concrete implementations.

#### Testing with the Container

For testing, the container provides utilities to override service implementations with mocks:

```python
from services.container import override_provider, reset_overrides
from unittest.mock import MagicMock

# Create a mock implementation
mock_r_service = MagicMock()
mock_r_service.is_available.return_value = True

# Override the service for testing
override_provider("r_service", mock_r_service)

# Run tests with the mock service

# Reset all overrides when done
reset_overrides()
```

This makes it easy to test components in isolation without dependencies on actual implementations.

### Design Principles

The application implements SOLID design principles:

1. **Single Responsibility Principle**: Each class has one responsibility
2. **Open/Closed Principle**: Classes are open for extension but closed for modification
3. **Liskov Substitution Principle**: Subtypes must be substitutable for their base types
4. **Interface Segregation Principle**: Clients shouldn't depend on methods they don't use
5. **Dependency Inversion Principle**: High-level modules depend on abstractions, not implementations
   - Interfaces defined as protocols in `services/interfaces/`
   - Service provider mechanism in `services/provider.py`
   - Components request services by interface rather than importing concrete implementations

Additionally, the application follows:

1. **Composition Over Inheritance**: Using composition (e.g., `PageContainer`) instead of inheritance
2. **Dependency Injection**: Services are injected into classes that need them
3. **Separation of Concerns**: UI, business logic, and data access are separated

### R Integration

For R-based calculations:

1. Place R scripts in the `r_scripts/` directory
2. Use the `r_service` to execute R code and exchange data
3. Create domain-specific services that use the R service

### Configuration Management

The application uses a centralized configuration system:

1. **Configuration Sources**:
   - Default values defined in config.py
   - Environment variables (e.g., `APP_LOGGING_LEVEL=DEBUG`)
   - Configuration files (searched for in standard locations)

2. **Creating a Configuration File**:
   ```bash
   # Copy the template
   cp config.json.template config.json

   # Edit as needed
   nano config.json
   ```

3. **Configuration Sections**:
   - `app`: General application settings
   - `logging`: Logging configuration
   - `r`: R integration settings
   - `kaggle`: Kaggle API settings

### Error Handling

The application uses a standardized error handling approach:

1. **Error Classes**:
   - `AppError`: Base exception class
   - `ServiceError`: For service-related errors
   - `ValidationError`: For input validation
   - `DataError`: For data-related issues
   - `ConfigurationError`: For configuration problems

2. **Using Error Handling**:
   ```python
   from utils.error_handling import ServiceError, handle_service_errors

   @handle_service_errors("MyService")
   def my_function():
       # Function body
       if error_condition:
           raise ServiceError("Error message", "service", "operation")
   ```

### Logging System

The application includes a comprehensive logging system:

1. **Getting a Logger**:
   ```python
   from utils.logging import get_logger

   logger = get_logger(__name__)
   logger.info("This is an info message")
   logger.error("This is an error message")
   ```

2. **Logging Context**:
   ```python
   from utils.logging import LoggingContext

   with LoggingContext(logger, user_id="123", action="login"):
       logger.info("User action")  # Will include user_id and action in log
   ```

3. **Logging Function Calls**:
   ```python
   from utils.logging import log_function_call

   @log_function_call()
   def my_function():
       # Function body
   ```

### Testing Framework

The project includes a comprehensive testing framework:

1. **Unit Tests**: Test individual components in isolation
   ```bash
   # Run all unit tests
   pytest tests/unit

   # Run unit tests for specific components
   pytest tests/unit/services
   ```

2. **Integration Tests**: Test interactions between components
   ```bash
   pytest tests/integration
   ```

3. **Functional Tests**: Test the system from a user perspective
   ```bash
   pytest tests/functional
   ```

4. **Test Categories**: Tests are categorized with markers
   ```bash
   # Run only tests that require R
   pytest -m r_dependent

   # Skip tests that require R
   pytest -k "not r_dependent"
   ```

For more details on the testing framework, see the [tests README](tests/README.md).

### Code Style

This project uses:
- Black for code formatting
- Flake8 for linting
- Type annotations throughout

Run formatting and linting:
```bash
black core ui utils services r_scripts tests
flake8 core ui utils services tests
```