# R Scripts Directory

This directory contains R scripts used by the Universal App for various calculations and analyses.

## Purpose

The R scripts in this directory provide specialized calculations and statistical analysis capabilities that are used by Python code via the R service interface. By keeping R code separate from Python code, we maintain a clean separation of concerns while leveraging the power of R for statistical analysis.

## Directory Structure

- `actuarial/`: Scripts for actuarial calculations
  - `mortality.R`: Functions for calculating mortality tables
  - `present_value.R`: Functions for present value calculations of annuities
- `common/`: Common utility functions and shared code

## Usage from Python

These scripts are called from Python code using the `r_service` interface in `services/r_service.py`. The typical pattern is:

1. Python code calls a method on a domain-specific service (e.g., `actuarial_service`)
2. The domain service delegates to `r_service` for R-specific operations
3. The `r_service` executes the appropriate R script and returns the result
4. The domain service converts the result to appropriate Python types

## Adding New R Scripts

When adding new R scripts:

1. Place them in the appropriate subdirectory
2. Follow R best practices and coding standards
3. Document the purpose and inputs/outputs of each function
4. Create appropriate service methods in Python to call the R functions

## Requirements

To use these scripts:

- R must be installed on the system (https://cran.r-project.org/)
- Required R packages should be documented at the top of each script
- Python must have the `rpy2` package installed (`pip install rpy2`)

## Testing

When writing R scripts, it's recommended to test them both in R directly and via the Python interface to ensure they work correctly in both environments.