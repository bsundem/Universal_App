# Universal App

A unified application framework that hosts multiple projects in a single interface. This repository serves as a container for various projects until they grow large enough to be moved into their own repositories.

## Features

- Unified navigation system
- Modular project architecture
- Tkinter-based GUI (part of Python standard library)
- Service-oriented architecture for business logic
- R integration for specialized calculations
- Kaggle data exploration capabilities

## Project Structure

```
Universal_App/
├── core/               # Core application functionality
├── services/           # Business logic services
│   ├── actuarial/      # Actuarial calculation services
│   ├── kaggle/         # Kaggle data services
│   └── r_service.py    # R integration service
├── r_scripts/          # R scripts for specialized calculations
│   ├── actuarial/      # Actuarial R scripts
│   └── common/         # Common R utilities
├── ui/                 # User interface components
│   ├── components/     # Reusable UI components
│   └── pages/          # Application pages
└── utils/              # Utility functions and helpers
```

## Setup

### Installation

```bash
# Create and activate a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # Unix/macOS
# or
.venv\Scripts\activate     # Windows

# Install development dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Optional Dependencies

For full functionality, the following optional packages can be installed:

- **R Integration**: Install R and the rpy2 package
  ```bash
  # Install R from https://cran.r-project.org/
  # Then install the Python interface
  pip install rpy2
  ```

- **Data Analysis**: For Kaggle data exploration and visualization
  ```bash
  pip install pandas matplotlib kaggle
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

To add a new project module to the application:

1. Create a new page in `ui/pages/` (inherit from `BasePage`)
2. Add any required business logic in the `services/` directory
3. Add the page to the `MainWindow.setup_pages()` method in `ui/main_window.py`
4. Add a navigation button in the `Sidebar._setup_navigation()` method in `ui/components/sidebar.py`

### Services Architecture

The application follows a service-oriented architecture:

1. UI components should delegate business logic to services
2. Services are organized by domain (e.g., `actuarial`, `kaggle`)
3. Cross-cutting concerns have dedicated services (e.g., `r_service.py`)

### R Integration

For R-based calculations:

1. Place R scripts in the `r_scripts/` directory
2. Use the `r_service` to execute R code and exchange data
3. Create domain-specific services that use the R service

### Code Style

This project uses:
- Black for code formatting
- Flake8 for linting

Run formatting and linting:
```bash
black core ui utils services r_scripts
flake8 core ui utils services
```

### Testing

```bash
pytest
```