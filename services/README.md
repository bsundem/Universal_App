# Services Directory

This directory contains service modules that implement the business logic for the Universal App.

## Purpose

The services in this directory follow the service-oriented architecture pattern, providing clear separation between UI components and business logic. Each service is responsible for a specific domain or cross-cutting concern.

## Architecture Principles

1. **Separation of Concerns**: Services contain business logic, while UI components handle presentation
2. **Single Responsibility**: Each service has a focused purpose
3. **Statelessness**: Services should be stateless when possible
4. **Reusability**: Services can be reused across different UI components

## Directory Structure

- `actuarial/`: Services for actuarial calculations
  - `actuarial_service.py`: Service for mortality tables and present value calculations
- `kaggle/`: Services for Kaggle data interaction
  - `kaggle_service.py`: Service for searching, downloading, and processing Kaggle datasets
- `r_service.py`: Service for R integration and executing R scripts

## Using Services

Services are typically exposed as singleton instances that can be imported directly:

```python
# Example: Using the Kaggle service
from services.kaggle.kaggle_service import kaggle_service

# Use the service
datasets = kaggle_service.get_dataset_list(search_term="machine learning")
```

## Adding New Services

When adding new services:

1. Create a new directory for domain-specific services
2. Implement the service class with clear responsibilities
3. Export a singleton instance for easy importing
4. Use type hints for better code readability
5. Document the public methods and their parameters

## Dependencies

Services should follow these dependency rules:

1. Services can depend on other services
2. Services should not depend on UI components
3. UI components should depend on services, not vice versa
4. Cross-cutting services (like `r_service.py`) should be used by domain-specific services

## Configuration

Services that require configuration should:

1. Accept configuration parameters in their constructor
2. Provide sensible defaults when possible
3. Document required configuration