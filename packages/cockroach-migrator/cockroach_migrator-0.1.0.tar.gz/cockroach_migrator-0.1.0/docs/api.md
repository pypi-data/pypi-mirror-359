# API Reference

## Overview

The `cockroach-migrator` package provides both a command-line interface and a Python API for migrating data from CockroachDB to PostgreSQL.

## Python API

### Main Classes

#### CockroachMigrator

The main class that handles the migration process.

```python
from cockroach_migrator import CockroachMigrator

migrator = CockroachMigrator(config_path="migration_config.json")
migrator.migrate()
```

##### Constructor

```python
CockroachMigrator(config_path: str)
```

**Parameters:**
- `config_path` (str): Path to the JSON configuration file

**Raises:**
- `FileNotFoundError`: If configuration file doesn't exist
- `json.JSONDecodeError`: If configuration file contains invalid JSON
- `SystemExit`: If required configuration values are missing

##### Methods

###### migrate()

Executes the complete migration process.

```python
def migrate() -> None
```

**Process:**
1. Downloads required binaries
2. Sets up temporary CockroachDB instance
3. Restores backup from S3
4. Exports data to SQL
5. Validates data (optional)
6. Tests PostgreSQL import (optional)
7. Imports to target PostgreSQL
8. Cleans up temporary resources

**Raises:**
- `Exception`: Various exceptions for different failure modes

###### _load_config(config_path: str) -> Dict

Loads configuration from JSON file.

**Parameters:**
- `config_path` (str): Path to configuration file

**Returns:**
- `Dict`: Configuration dictionary

###### _get_aws_credentials() -> Tuple[str, str]

Extracts AWS credentials from configuration.

**Returns:**
- `Tuple[str, str]`: (access_key, secret_key)

###### _get_postgres_config() -> Dict

Gets PostgreSQL connection configuration.

**Returns:**
- `Dict`: PostgreSQL connection parameters

### Module Functions

#### CLI Functions

##### main()

Main entry point for the command-line interface.

```python
from cockroach_migrator.cli import main

main()  # Processes sys.argv arguments
```

##### create_sample_config()

Creates a sample configuration file.

```python
from cockroach_migrator.cli import create_sample_config

create_sample_config()  # Creates migration_config.json
```

### Configuration Schema

The configuration file must be a JSON object with the following structure:

```python
{
    # AWS Configuration (Required)
    "aws_access_key_id": str,
    "aws_secret_access_key": str,
    "s3_backup_path": str,
    
    # CockroachDB Configuration
    "cockroach_version": str = "v24.3.5",
    "cockroach_port": int = 26257,
    "cockroach_http_port": int = 8080,
    "certs_dir": str = "cockroachdb/certs",
    "insecure_mode": bool = False,
    
    # PostgreSQL Configuration (Required password)
    "postgres_host": str = "localhost",
    "postgres_port": int = 5432,
    "postgres_database": str = "postgres",
    "postgres_username": str = "postgres",
    "postgres_password": str,  # Required
    "postgres_version": str = "17.0",
    
    # Migration Options
    "skip_validation": bool = False,
    "postgres_import_enabled": bool = True,
    "test_postgresql_import": bool = True,
    "do_cleanup": bool = True,
    "temp_dir": str = "",
    
    # Performance Tuning
    "chunk_size": int = 10000,
    
    # Test PostgreSQL Configuration
    "test_postgres_port": int = 5433,
    "test_database_name": str = "migration_test",
    "test_username": str = "postgres",
    "test_password": str = "testpass123"
}
```

### Exceptions

The package may raise various exceptions:

#### Configuration Errors
- `FileNotFoundError`: Configuration file not found
- `json.JSONDecodeError`: Invalid JSON in configuration
- `SystemExit`: Missing required configuration values

#### Migration Errors
- `subprocess.CalledProcessError`: External command failures
- `ConnectionError`: Database connection issues
- `Exception`: General migration failures

### Logging

The package uses Python's standard logging module:

```python
import logging

# Configure logging before importing
logging.basicConfig(level=logging.INFO)

from cockroach_migrator import CockroachMigrator
```

**Log Levels:**
- `DEBUG`: Detailed debugging information
- `INFO`: General progress information
- `WARNING`: Non-critical issues
- `ERROR`: Critical errors

**Log Outputs:**
- Console (stdout)
- File (`migration.log`)
- Validation report (`validation_report.txt`)

## Advanced Usage Examples

### Custom Configuration

```python
import json
from cockroach_migrator import CockroachMigrator

# Create configuration programmatically
config = {
    "aws_access_key_id": "AKIA...",
    "aws_secret_access_key": "secret...",
    "s3_backup_path": "s3://my-bucket/backup",
    "postgres_password": "mypassword",
}

# Save to file
with open("custom_config.json", "w") as f:
    json.dump(config, f, indent=2)

# Use with migrator
migrator = CockroachMigrator("custom_config.json")
migrator.migrate()
```

### Error Handling

```python
from cockroach_migrator import CockroachMigrator
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    migrator = CockroachMigrator("config.json")
    migrator.migrate()
    logger.info("Migration completed successfully")
except FileNotFoundError:
    logger.error("Configuration file not found")
except Exception as e:
    logger.error(f"Migration failed: {e}")
    # Handle cleanup or retry logic
```

### Validation Only

```python
from cockroach_migrator import CockroachMigrator

migrator = CockroachMigrator("config.json")

# Disable import and cleanup for validation-only
migrator.postgres_import_enabled = False
migrator.do_cleanup = False

migrator.migrate()
print("Check validation_report.txt for results")
```

### Programmatic Configuration Override

```python
from cockroach_migrator import CockroachMigrator

migrator = CockroachMigrator("base_config.json")

# Override specific settings
migrator.chunk_size = 5000
migrator.postgres_import_enabled = False
migrator.do_cleanup = False

migrator.migrate()
```

## Module Structure

```
cockroach_migrator/
├── __init__.py          # Package initialization and exports
├── cli.py               # Command-line interface
├── migrate.py           # Main migration logic
├── migrate_cockroach.py # CockroachDB operations
├── migrate_postgresql.py # PostgreSQL operations
├── migrate_conversion.py # Data conversion utilities
├── migrate_validate.py  # Validation utilities
├── config/              # Default configuration files
└── templates/           # Configuration templates
```

## Version Information

```python
import cockroach_migrator

print(cockroach_migrator.__version__)  # "0.1.0"
print(cockroach_migrator.__author__)   # "Nomos"
print(cockroach_migrator.__email__)    # "oss@ordicio.com"
```

## Type Hints

The package includes comprehensive type hints for better IDE support:

```python
from typing import Dict, Optional, Tuple
from cockroach_migrator import CockroachMigrator

def run_migration(config_file: str) -> bool:
    """Run migration and return success status."""
    try:
        migrator: CockroachMigrator = CockroachMigrator(config_file)
        migrator.migrate()
        return True
    except Exception:
        return False
```

## Testing

The package includes a test suite. Run tests with:

```bash
# Install with test dependencies
pip install -e ".[test]"

# Run tests
pytest tests/

# Run with coverage
pytest --cov=cockroach_migrator tests/