# R Scripts

This directory contains R scripts used by the Universal App for various calculations and analyses.

## Organization

- `actuarial/` - Scripts for actuarial calculations
- `common/` - Common utility functions and shared code

## Usage

These scripts are called from Python code via the R service interface. They should be kept
separate from the Python codebase to maintain a clean separation of concerns.

## Requirements

- R must be installed on the system
- Required R packages should be documented in each script
- Python must have the `rpy2` package installed to interface with these scripts