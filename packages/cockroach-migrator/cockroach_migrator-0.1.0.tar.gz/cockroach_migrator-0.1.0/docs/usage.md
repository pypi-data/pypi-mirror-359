# Usage Guide

## Quick Start

1. **Install the package**:
   ```bash
   pip install cockroach-migrator
   ```

2. **Create a configuration file**:
   ```bash
   cockroach-migrate --create-config
   ```

3. **Edit the configuration** with your specific values:
   ```bash
   # Edit migration_config.json with your settings
   ```

4. **Run the migration**:
   ```bash
   cockroach-migrate --config migration_config.json
   ```

## Command Line Interface

### Basic Commands

```bash
# Run migration with default config file (migration_config.json)
cockroach-migrate

# Run migration with custom config file
cockroach-migrate --config my_config.json

# Create sample configuration file
cockroach-migrate --create-config

# Show version information
cockroach-migrate --version

# Show help
cockroach-migrate --help
```

### Alternative Command

You can also use the shorter alias:

```bash
crdb-migrate --config my_config.json
```

### Validation Options

```bash
# Run validation only (no actual migration)
cockroach-migrate --validate-only

# Skip validation step (faster migration)
cockroach-migrate --skip-validation
```

## Configuration

### Configuration File Structure

The configuration file (`migration_config.json`) contains all settings needed for the migration:

```json
{
  "aws_access_key_id": "your_aws_access_key_here",
  "aws_secret_access_key": "your_aws_secret_key_here",
  "s3_backup_path": "s3://your-bucket/your-backup-path",
  "cockroach_version": "v24.3.5",
  "cockroach_port": 26257,
  "cockroach_http_port": 8080,
  "certs_dir": "cockroachdb/certs",
  "insecure_mode": true,
  "postgres_host": "localhost",
  "postgres_port": 5432,
  "postgres_database": "postgres",
  "postgres_username": "postgres",
  "postgres_password": "your_postgres_password_here",
  "postgres_version": "17.0",
  "skip_validation": false,
  "postgres_import_enabled": true,
  "test_postgresql_import": true,
  "test_postgres_port": 5433,
  "test_database_name": "migration_test",
  "test_username": "postgres",
  "test_password": "testpass123",
  "do_cleanup": true,
  "temp_dir": "",
  "chunk_size": 10000
}
```

### Configuration Options

| Option | Description | Default | Required |
|--------|-------------|---------|----------|
| `aws_access_key_id` | AWS Access Key ID | - | Yes |
| `aws_secret_access_key` | AWS Secret Access Key | - | Yes |
| `s3_backup_path` | S3 path to CockroachDB backup | - | Yes |
| `cockroach_version` | CockroachDB version to download | `v24.3.5` | No |
| `cockroach_port` | Port for temporary CockroachDB instance | `26257` | No |
| `cockroach_http_port` | HTTP port for CockroachDB | `8080` | No |
| `certs_dir` | Path to CockroachDB certificates | `cockroachdb/certs` | No |
| `insecure_mode` | Run CockroachDB in insecure mode | `false` | No |
| `postgres_host` | PostgreSQL host | `localhost` | No |
| `postgres_port` | PostgreSQL port | `5432` | No |
| `postgres_database` | Target PostgreSQL database | `postgres` | No |
| `postgres_username` | PostgreSQL username | `postgres` | No |
| `postgres_password` | PostgreSQL password | - | Yes |
| `postgres_version` | PostgreSQL client version | `17.0` | No |
| `skip_validation` | Skip validation step | `false` | No |
| `postgres_import_enabled` | Enable PostgreSQL import | `true` | No |
| `test_postgresql_import` | Test import with local PostgreSQL | `true` | No |
| `do_cleanup` | Clean up temporary files | `true` | No |
| `chunk_size` | Rows per chunk for large tables | `10000` | No |

## Migration Process

The migration follows these steps:

1. **Download Binaries**: Downloads CockroachDB and PostgreSQL binaries if needed
2. **Setup**: Creates temporary CockroachDB instance
3. **Restore**: Restores backup from S3
4. **Export**: Exports data as PostgreSQL-compatible SQL
5. **Validate**: Validates exported data (optional)
6. **Test Import**: Tests import with local PostgreSQL (optional)
7. **Import**: Imports data to target PostgreSQL
8. **Cleanup**: Removes temporary files (optional)

## Advanced Usage

### Validation-Only Mode

Run validation without performing the actual migration:

### Skip Validation

For faster migration when you trust the data quality:

```bash
cockroach-migrate --skip-validation
```

### Testing Mode

Test the migration process without affecting production:

```json
{
  "postgres_import_enabled": false,
  "do_cleanup": false,
  "test_postgresql_import": true
}
```

### Large Database Optimization

For very large databases, adjust chunking settings:

```json
{
  "chunk_size": 5000
}
```

## Python API Usage

You can also use the migration tool programmatically:

```python
from cockroach_migrator import CockroachMigrator

# Initialize migrator with config file
migrator = CockroachMigrator('migration_config.json')

# Run the migration
migrator.migrate()
```

## Logging and Monitoring

The tool provides comprehensive logging:

- **Console Output**: Real-time progress information
- **Log File**: Detailed logs saved to `migration.log`
- **Validation Report**: Detailed validation results in `validation_report.txt`

### Log Levels

- **INFO**: General progress information
- **WARNING**: Non-critical issues
- **ERROR**: Critical errors that stop migration
- **DEBUG**: Detailed debugging information

## Troubleshooting

### Common Issues

1. **AWS Credentials**: Ensure AWS credentials are correct and have S3 access
2. **PostgreSQL Connection**: Verify PostgreSQL is running and accessible
3. **Certificates**: For secure mode, ensure all certificates are present
4. **Disk Space**: Ensure sufficient disk space for temporary files
5. **Memory**: Large databases may require more memory

### Error Recovery

- **Partial Migration**: Use `do_cleanup: false` to preserve temporary files
- **Resume Migration**: Restart with existing temporary files
- **Validation Issues**: Check `validation_report.txt` for details

### Performance Tuning

- **Chunk Size**: Adjust `chunk_size` for optimal performance
- **Parallel Processing**: Future versions will support parallel processing
- **Memory Usage**: Monitor memory usage for large tables

## Examples

### Basic Migration
```bash
cockroach-migrate --config production_config.json
```

### Development Testing
```bash
cockroach-migrate --config dev_config.json --validate-only
```

### Fast Migration
```bash
cockroach-migrate --config config.json --skip-validation