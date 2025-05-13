"""
Service interfaces package for the Universal App.

This package contains protocol (interface) definitions for all services,
following the Interface Segregation Principle. These protocols define the
contract that service implementations must fulfill.

Using protocols instead of abstract base classes allows for:
- Better static type checking with mypy
- More flexibility in implementation
- Easier mocking for testing
"""