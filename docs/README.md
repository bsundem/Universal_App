# Universal App Documentation

This directory contains detailed documentation for the Universal App project.

## Contents

- [Architecture Overview](architecture.md): Overview of the application architecture
- [Configuration Guide](configuration.md): Instructions for configuring the application
- [Dependency Management](dependencies.md): Guide to handling project dependencies
- [Extending the DI Container](extending_di.md): Guide to adding new services

## Service Documentation

- [Actuarial Service](actuarial_service.md): Documentation for the actuarial service
- [Finance Service](finance_service.md): Documentation for the finance service

## Additional Documentation

The following documentation is also available in other parts of the codebase:

- **README.md**: Main project documentation in the root directory
- **CLAUDE.md**: Guidance for Claude Code when working with this repository
- **tests/README.md**: Information about testing strategies
- **r_scripts/README.md**: Documentation for R script integration
- **services/README.md**: Overview of the service layer

## Modules

The Universal App currently includes the following modules:

### Core Application
Basic application framework with a modern UI using ttkbootstrap, a configuration system, and a dependency injection container.

### Actuarial Module
Provides actuarial calculations including:
- Mortality table calculations
- Present value calculations
- Life expectancy projections
- Visualizations for actuarial data

### Finance Module
Provides financial calculations including:
- Yield curve calculations
- Option pricing models
- Portfolio metrics
- Financial visualization tools

## Getting Started

To get started with the Universal App:

1. See the main README.md for installation instructions
2. Review the architecture documentation to understand the application structure
3. Explore the configuration guide to set up your development environment
4. Check the extending documentation if you want to add new services