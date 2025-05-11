# Configuration Guide

This document provides information about the configuration system for the Universal App.

## Configuration Sources

The application uses a hierarchical configuration system with the following sources (in order of precedence):

1. **Environment variables**: `APP_SECTION_KEY=value`
2. **Configuration file**: `config.json`
3. **Default values**: Defined in `core/config.py`

## Configuration File

The application looks for a configuration file in the following locations (in order):

1. `./config.json`
2. `./config/config.json`
3. `~/.config/universal_app/config.json`

To create a configuration file, copy the template:

```bash
cp config.json.template config.json
```

## Configuration Sections

### App Configuration

```json
"app": {
  "debug": false,
  "title": "Universal App",
  "theme": "default",
  "temp_dir": null,
  "data_dir": "data"
}
```

- **debug**: Enable debug mode (boolean)
- **title**: Application window title (string)
- **theme**: UI theme name (string)
- **temp_dir**: Temporary directory for files (string, null for OS default)
- **data_dir**: Data storage directory (string)

### Logging Configuration

```json
"logging": {
  "level": "INFO",
  "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
  "date_format": "%Y-%m-%d %H:%M:%S",
  "file": null,
  "max_size": 10485760,
  "backup_count": 5
}
```

- **level**: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **format**: Log message format
- **date_format**: Log date format
- **file**: Log file path (null for console only)
- **max_size**: Maximum log file size in bytes
- **backup_count**: Number of backup log files

### R Integration Configuration

```json
"r": {
  "enabled": true,
  "scripts_dir": "r_scripts",
  "libraries": [
    "base",
    "stats"
  ]
}
```

- **enabled**: Enable R integration
- **scripts_dir**: Directory containing R scripts
- **libraries**: R packages to load by default

### Kaggle Integration Configuration

```json
"kaggle": {
  "enabled": true,
  "credentials_file": "~/.kaggle/kaggle.json",
  "timeout": 60,
  "max_dataset_size_mb": 1000
}
```

- **enabled**: Enable Kaggle integration
- **credentials_file**: Path to Kaggle API credentials
- **timeout**: API request timeout in seconds
- **max_dataset_size_mb**: Maximum size of datasets to download

## Environment Variables

You can override any configuration value using environment variables in the format `APP_SECTION_KEY`.

Examples:

```bash
# Set debug mode
export APP_APP_DEBUG=true

# Change log level
export APP_LOGGING_LEVEL=DEBUG

# Disable Kaggle integration
export APP_KAGGLE_ENABLED=false
```

## Configuration API

You can access configuration values in code using the `config` object:

```python
from core.config import config

# Access configuration values
app_title = config.app.title
log_level = config.logging.level
r_enabled = config.r.enabled

# Check if a section exists
if hasattr(config, 'kaggle'):
    kaggle_timeout = config.kaggle.timeout
```

## Configuration Validation

The configuration system validates the types of values based on their default types. For example, if a value is defined as a boolean in the default configuration, the system will convert string values to booleans.

Example conversions:

- **Booleans**: "true", "yes", "1", "on" → `True`
- **Lists**: Comma-separated strings → `List`
- **Numbers**: Strings → `int` or `float` based on the default type