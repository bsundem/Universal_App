# Dependency Management Guide

This document outlines the dependency management strategy for the Universal App project.

## Dependency Categories

The project divides dependencies into several categories:

### Core Dependencies

These are required for the application to function and must be installed:

- **dependency-injector**: For the dependency injection container
- **requests**: For HTTP requests

### Optional Feature Dependencies

These are required only for specific features:

- **R Integration**:
  - rpy2: For R interoperability

- **Data Analysis**:
  - pandas: For data manipulation
  - numpy: For numerical operations
  - matplotlib: For data visualization

- **Kaggle Integration**:
  - kaggle: For Kaggle API access
  - Pillow: For image handling

### Development Dependencies

These are only needed for development and testing:

- **pytest**: For running tests
- **black**: For code formatting
- **flake8**: For linting

## Installation

### Basic Installation

To install just the core dependencies:

```bash
pip install -e .
```

### Feature-specific Installation

To install with specific features:

```bash
# For R integration
pip install -e ".[r]"

# For data analysis
pip install -e ".[data]"

# For Kaggle integration
pip install -e ".[kaggle]"

# For development tools
pip install -e ".[dev]"

# For all features and development tools
pip install -e ".[all]"
```

### Using requirements.txt

For development or to install all dependencies:

```bash
pip install -r requirements.txt
```

## Dependency Files

The project uses two primary files for managing dependencies:

### setup.py

Defines the package and its dependencies for distribution. This is the canonical source of dependency information.

```python
setup(
    # ...
    install_requires=[
        "dependency-injector>=4.41.0",
        "requests>=2.26.0",
    ],
    extras_require={
        "r": ["rpy2>=3.5.0"],
        "data": ["pandas>=1.3.0", "matplotlib>=3.5.0", "numpy>=1.20.0"],
        "kaggle": ["kaggle>=1.5.0", "Pillow>=8.0.0"],
        "dev": ["black>=23.0.0", "flake8>=6.0.0", "pytest>=7.0.0"],
        "all": [
            "rpy2>=3.5.0",
            "pandas>=1.3.0",
            "matplotlib>=3.5.0",
            "numpy>=1.20.0",
            "kaggle>=1.5.0",
            "Pillow>=8.0.0",
            "black>=23.0.0", 
            "flake8>=6.0.0", 
            "pytest>=7.0.0",
        ],
    },
    # ...
)
```

### requirements.txt

Lists all dependencies for development or for environments where installing via pip with extras is not available.

```
# Core dependencies
dependency-injector>=4.41.0
requests>=2.26.0

# Development tools
pytest>=7.0.0
black>=23.0.0
flake8>=6.0.0

# Optional dependencies for R integration
rpy2>=3.5.0

# Optional dependencies for data analysis
pandas>=1.3.0
numpy>=1.20.0
matplotlib>=3.4.0

# Optional dependencies for Kaggle integration
kaggle>=1.5.0
Pillow>=8.0.0  # For image handling
```

## Dependency Checking

The application checks for optional dependencies at runtime and gracefully degrades functionality if they're not available:

```python
# Example of runtime dependency checking
try:
    import pandas as pd
except ImportError:
    pd = None

if pd is not None:
    # Use pandas functionality
else:
    # Fall back to basic functionality or display appropriate message
```

## Version Management

- The project follows semantic versioning
- Minimum compatible versions are specified for all dependencies
- Upper version constraints are deliberately avoided where possible to allow for upgrades

## Adding New Dependencies

When adding a new dependency:

1. Determine if it's core, optional, or development-only
2. Update setup.py with the appropriate category
3. Update requirements.txt to match
4. If it's optional, implement runtime checks
5. Update documentation as needed

## Dependency Verification

To verify that dependencies are installed correctly:

```bash
# Run the dependency check utility
python -m utils.dependency_check

# Or use the app's built-in verification
universal-app --verify-dependencies
```