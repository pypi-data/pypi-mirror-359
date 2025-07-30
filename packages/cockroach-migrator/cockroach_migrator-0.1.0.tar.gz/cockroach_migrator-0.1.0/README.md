# CockroachDB to PostgreSQL Migration

A tool for migrating data from a CockroachDB backup stored in S3 to a PostgreSQL database.

## 🚀 Quick Start

Get up and running in 4 simple steps:

### 1. Install

```bash
pip install cockroach-migrator
```

### 2. Configure

```bash
# Create a sample configuration file
cockroach-migrate --create-config

# Edit the configuration with your details
nano migration_config.json
```

### 3. Test the Conversion

```bash
# Test schema conversion and data processing (recommended)
# This creates a temporary PostgreSQL instance to validate the migration
cockroach-migrate --config migration_config.json
```

The tool will automatically test the conversion by:

- Setting up a temporary PostgreSQL test instance
- Converting your CockroachDB schema to PostgreSQL format
- Importing data into the test instance to verify compatibility
- Generating a validation report with any issues found

### 4. Production Migration

Once testing is successful, the same command will proceed to import into your target PostgreSQL database specified in the configuration.

**The tool automatically handles:**

- Download of required CockroachDB and PostgreSQL binaries
- Temporary instance setup for data processing and testing
- S3 backup restoration and schema conversion
- Data validation and compatibility testing
- Import to target PostgreSQL database
- Cleanup of all temporary resources

> **Need help?** Check the detailed [Usage](#usage) section below or run `cockroach-migrate --help`

## Overview

The migration process involves:

1. **Download**: Automatically downloads the appropriate CockroachDB binary for your platform as well as postgresql (for a temporary export and testing instance)
2. **Setup**: Creates a temporary CockroachDB instance using existing certificates
3. **Restore**: Restores the backup from S3 using AWS credentials
4. **Export**: Exports all databases and data as SQL using memory-efficient chunked processing
5. **Import**: Imports the SQL data into PostgreSQL, first onto a test deployment, then to the target system.
6. **Cleanup**: Removes all temporary files and processes (can be disabled)

## Prerequisites

### Required Software

- Python 3.7 or higher
- PostgreSQL client tools (`psql` command) - **Now automatically downloaded if missing**
- Internet connection (for downloading CockroachDB and PostgreSQL binaries)

### Required Files (when using insecure_mode=false)

- **Certificates**: CockroachDB certificates must be present in `cockroachdb/certs/`
  - `ca.crt`
  - `client.root.crt`
  - `client.root.key`
  - `node.crt`
  - `node.key`
- **AWS Credentials**: Either in config file or AWS keys file
- **PostgreSQL**: Target PostgreSQL instance must be running and accessible

## Configuration

### 1. Edit Configuration File

Edit `migration_config.json` with your specific values:

```json
{
  "aws_access_key_id":"myawskeyid",
  "aws_secret_access_key":"myawssecret",
  "s3_backup_path": "s3://mybucket/mybackup",
  "cockroach_version": "v24.3.5",
  "cockroach_port": 26257,
  "cockroach_http_port": 8080,
  "certs_dir": "cockroachdb/certs",
  "insecure_mode": true,
  "postgres_host": "localhost",
  "postgres_port": 5432,
  "postgres_database": "postgres",
  "postgres_username": "postgres",
  "postgres_version": "17.0",
  "postgres_password": "somepasswordhere",
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

### 2. Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `aws_keys_file` | Path to AWS credentials file | Required |
| `aws_access_key_id` | AWS Access Key ID (alternative to keys file) | - |
| `aws_secret_access_key` | AWS Secret Access Key (alternative to keys file) | - |
| `s3_backup_path` | S3 path to CockroachDB backup | Required |
| `cockroach_version` | CockroachDB version to download | `v24.3.5` |
| `cockroach_port` | Port for temporary CockroachDB instance | `26257` |
| `cockroach_http_port` | HTTP port for temporary CockroachDB instance | `8080` |
| `certs_dir` | Path to CockroachDB certificates directory | `cockroachdb/certs` |
| `postgres_host` | PostgreSQL host | `localhost` |
| `postgres_port` | PostgreSQL port | `5432` |
| `postgres_database` | Target PostgreSQL database | `postgres` |
| `postgres_username` | PostgreSQL username | `postgres` |
| `postgres_password` | PostgreSQL password | Required |
| `postgres_version` | PostgreSQL client version to download | `17.0` |
| `postgres_import_enabled` | Enable/disable PostgreSQL import | `true` |
| `do_cleanup` | Enable/disable cleanup of temporary resources | `true` |
| `temp_dir` | Absolute path for the temporary directory. If empty, the system's temporary folder is used. | `""` |
| `skip_validation` | Skip validation step entirely | `false` |
| `chunk_size` | Number of rows to process per chunk for all tables | `10000` |

### 3. AWS Credentials

The script supports two methods for AWS credentials:

#### Method 1: AWS Keys File (Recommended)

```json
{
  "aws_keys_file": "AWS/keys/mykey.txt"
}
```

The keys file should contain:

```bash
export AWS_ACCESS_KEY=AKIA...
export AWS_SECRET_KEY=123...
```

#### Method 2: Direct Configuration

```json
{
  "aws_access_key_id": "AKIA...",
  "aws_secret_access_key": "123..."
}
```

## Installation

### 1. From PyPI (Recommended)

```bash
pip install cockroach-migrator
```

### 2. From Source (Development)

```bash
git clone <repository-url>
cd cockroach-migrator
pip install -e .
```

### 3. Update Local Installation

If you're working with the source code and want to update your pip installation with the latest local changes:

**Windows:**

```cmd
update_local_install.bat
```

**Linux/macOS:**

```bash
./update_local_install.sh
```

These scripts will:

- Uninstall the existing cockroach-migrator package
- Install the package from the current directory in editable mode
- Verify the installation was successful

## Usage

### 1. Basic Migration

```bash
cockroach-migrate --config migration_config.json
```

### 2. Validation Options

The migration tool includes comprehensive validation capabilities that can be configured in the JSON config file or overridden via command-line arguments:

#### Configuration-Based Validation Control

**Skip Validation** (in config file):

```json
{
  "skip_validation": true
}
```

#### Command-Line Overrides

**Skip Validation**:

```bash
cockroach-migrate --skip-validation
```

Command-line arguments take precedence over configuration file settings.

#### Validation Features

**Validation-Only Mode**:

- Exports data from CockroachDB
- Performs comprehensive validation
- Generates detailed validation report
- Skips PostgreSQL import
- Preserves temporary files for inspection

**Skip Validation**:

- Bypasses validation for faster migration
- Use when confident about data quality
- Reduces migration time significantly

#### Validation Report

After validation, check `validation_report.txt` for:

- Schema analysis (tables, indexes, constraints)
- Data analysis (row counts, data types)
- Cross-validation (schema-data consistency)
- PostgreSQL compatibility issues
- Recommendations for addressing issues

### 3. Create Sample Configuration

```bash
cockroach-migrate --create-config
```

This creates a `migration_config.json` template file.

### 4. Verbose Logging

The script automatically logs to both console and `migration.log` file. Check the log file for detailed progress and debugging information.

## Process Details

### 1. Platform Detection

The script automatically detects your operating system and architecture to download the correct CockroachDB binary:

- Linux (x86_64, ARM64)
- macOS (Intel, Apple Silicon)
- Windows (x86_64)

### 2. Temporary CockroachDB Instance

- Creates a temporary data directory
- Starts CockroachDB in single-node mode
- Uses existing certificates for secure connections
- Automatically assigns available ports

### 3. S3 Restore Process

- Constructs authenticated S3 URL with AWS credentials
- Executes `RESTORE FROM LATEST IN` command
- Handles authentication and network timeouts

### 4. Data Export

- Identifies all user databases (excludes system databases)
- Uses modern CockroachDB export methods (`SHOW CREATE ALL TABLES`, direct SELECT queries)
- Advanced DDL processing with sophisticated schema conversion
- Creates PostgreSQL-compatible SQL file with proper constraint/index separation
- Includes database creation statements

### 5. PostgreSQL Import (Conditional)

- Automatically downloads PostgreSQL client if missing (configurable version)
- Can be disabled via `postgres_import_enabled: false` for testing

## Migration Strategy & Conversion Details

### Overview of CockroachDB to PostgreSQL Differences

The migration tool addresses fundamental differences between CockroachDB and PostgreSQL through a comprehensive conversion strategy. This section details how each difference is handled to ensure complete and accurate data migration.

### 1. Schema Conversion Strategy

#### Advanced DDL Processing ([`migrate_conversion.py`](migrate_conversion.py))

The migration uses sophisticated DDL processing that separates schema components for optimal PostgreSQL compatibility:

**Component Separation**:

- **Tables**: Core table structures processed first
- **Constraints**: Foreign keys and constraints applied after tables exist
- **Indexes**: Created last to avoid dependency issues during import

**Processing Pipeline**:

```python
def process_ddl_content(content: str, db_name: str = None) -> tuple[str, str, str]:
    # Returns: (tables_sql, constraints_sql, indexes_sql)
```

**Chunked Processing for Large Databases**:

- **Memory Efficient**: Processes tables in configurable chunks instead of loading entire tables into memory
- **Progress Tracking**: Shows "chunk X/Y" progress with row counts for long-running exports
- **Scalable**: Handles tables with millions of rows without memory exhaustion
- **Configurable**: Adjustable chunk size (default: 10,000 rows per chunk)

#### Data Type Conversions

| CockroachDB Type | PostgreSQL Type | Conversion Logic |
|------------------|-----------------|------------------|
| `STRING` | `TEXT` | Direct replacement |
| `STRING(n)` | `VARCHAR(n)` | Length preserved |
| `BYTES` | `BYTEA` | Binary data compatibility |
| `SERIAL8` | `BIGSERIAL` | Auto-increment sequences |
| `SERIAL4` | `SERIAL` | Standard sequences |
| `INT8` | `BIGINT` | 64-bit integers |
| `INT4` | `INTEGER` | 32-bit integers |
| `INT2` | `SMALLINT` | 16-bit integers |
| `JSON` | `JSONB` | Enhanced JSON with indexing |
| `TEXT(n)` | `VARCHAR(n)` | PostgreSQL doesn't support TEXT with length |

#### Index Handling

**Unique Index Naming**: Prevents PostgreSQL identifier conflicts

```python
def create_unique_index_name(original_name: str, db_name: str = None, table_name: str = None) -> str:
    # Creates PostgreSQL-compatible names within 63-character limit
    # Format: db_indexname_tablehash
```

**Index Features**:

- `STORING` clauses converted to `INCLUDE` (PostgreSQL 11+ syntax)
- Automatic index name deduplication
- Hash-based naming for long identifiers
- Removal of CockroachDB-specific index types

#### Constraint Processing

**Primary Key Conflicts**: Resolves duplicate constraint names

```sql
-- CockroachDB (problematic)
CONSTRAINT "primary" PRIMARY KEY

-- PostgreSQL (fixed)
CONSTRAINT "tablename_primary" PRIMARY KEY
```

**Foreign Key Handling**:

- `NOT VALID` constraints removed (PostgreSQL syntax difference)
- Cross-database references adapted
- Constraint validation separated from creation

### 2. Data Conversion Strategy

#### SELECT to INSERT Conversion ([`convert_select_to_inserts()`](migrate_conversion.py:389))

**Tab-Separated Output Handling**: CockroachDB uses tab separation, not pipe separation

```python
if '\t' in line:
    values = [val.strip() for val in line.split('\t')]
else:
    values = [val.strip() for val in line.split('|')]  # Fallback
```

**String Escaping**: Handles CockroachDB's double-quote escaping

```python
# CockroachDB: "" -> PostgreSQL: "
postgresql_content = inner_content.replace('""', '"')
# Single quotes: '' (same in both systems)
```

**JSON Data Handling**: Fixes double-escaped JSON content

```python
if value.startswith('"{') and value.endswith('}"'):
    json_content = value[1:-1]  # Remove outer quotes
    json_content = json_content.replace('""', '"')  # Fix escaping
```

**Length Constraint Validation**: Prevents data truncation

```python
if max_length and len(escaped_value) > max_length:
    logger.error(f"Value exceeds length limit ({len(escaped_value)} > {max_length})")
```

### 3. CockroachDB-Specific Feature Removal

#### Unsupported Features Filtered Out

- `FAMILY` clauses (CockroachDB column families)
- `INTERLEAVE` tables (CockroachDB-specific optimization)
- `STORING` in CREATE TABLE (converted to separate indexes)
- `SPLIT AT` partitioning
- `CONFIGURE ZONE` settings
- `INVERTED INDEX` (CockroachDB JSON indexing)
- `HASH SHARDED INDEX` (CockroachDB distribution)
- `LOCALITY REGIONAL` settings
- `PARTITION BY` clauses
- `WITH (ttl_` TTL settings

#### UUID Generation Differences

```sql
-- CockroachDB
DEFAULT gen_random_uuid()

-- PostgreSQL (requires uuid-ossp extension)
DEFAULT uuid_generate_v4()
```

### 4. Advanced Processing Features

#### Wrapped SQL Statement Cleaning ([`clean_wrapped_sql_statements()`](migrate_conversion.py:288))

Handles CockroachDB's `SHOW CREATE ALL TABLES` output format:

```sql
create_statement
"CREATE TABLE example (
  id INT8 PRIMARY KEY,
  name STRING
)"
```

Converted to standard SQL:

```sql
CREATE TABLE example (
  id BIGINT PRIMARY KEY,
  name TEXT
);
```

#### Fallback Mechanism

If advanced DDL processing fails, the system falls back to basic conversions:

```python
try:
    # Advanced DDL processing
    tables_sql, constraints_sql, indexes_sql = process_ddl_content(cleaned_content, db_name)
except Exception as e:
    logger.warning(f"Advanced DDL processing failed: {e}")
    logger.info("Falling back to basic schema conversion")
    return apply_basic_conversions(schema_content, logger)
```

### 5. Validation & Testing Strategy

#### Pre-Import Validation ([`migrate_validate.py`](migrate_validate.py))

**Schema Validation**:

- Table structure analysis
- Index compatibility checking
- Constraint dependency validation
- PostgreSQL syntax verification

**Data Validation**:

- Row count verification
- Data type compatibility
- Length constraint validation
- Character encoding checks

**Cross-Validation**:

- Schema-data consistency
- Foreign key relationship integrity
- Index coverage analysis

#### Local PostgreSQL Testing ([`migrate_postgresql.py`](migrate_postgresql.py))

**Automated Test Environment**:

- Downloads PostgreSQL binaries automatically
- Creates isolated test database
- Performs complete import test
- Validates data integrity
- Provides detailed error reporting

**Test Results Include**:

- Setup time metrics
- Import performance data
- Table row counts
- Error analysis
- Compatibility warnings

### 6. Binary Management & Platform Support

#### Automatic Binary Downloads

**CockroachDB Binary Management** ([`migrate_cockroach.py`](migrate_cockroach.py:19)):

- Version-specific persistent storage
- Platform detection (Linux, macOS, Windows)
- Architecture support (x64, ARM64)
- Automatic extraction and setup

**PostgreSQL Client Management**:

- Configurable version downloads
- Windows binary support (Linux/macOS require manual install)
- Persistent storage to avoid re-downloads
- Path management and executable detection

### 7. Error Handling & Recovery

#### Comprehensive Error Management

- **Connection failures**: Automatic retry with exponential backoff
- **Schema conflicts**: Detailed conflict resolution logging
- **Data truncation**: Length validation with error reporting
- **Type mismatches**: Automatic type coercion where possible
- **Constraint violations**: Dependency-aware constraint ordering

#### Logging & Debugging

- Detailed conversion logs for each transformation
- SQL statement logging for troubleshooting
- Performance metrics for optimization
- Validation reports for quality assurance

### 8. Production Readiness Features

#### Conditional Execution Controls

- **`postgres_import_enabled`**: Test schema conversion without import
- **`skip_validation`**: Fast migration for trusted data
- **`do_cleanup`**: Preserve temporary files for debugging

#### Performance Optimizations

- Batch processing for large datasets
- Memory-efficient streaming for large tables
- Parallel processing where possible
- Connection pooling for multiple databases

This comprehensive conversion strategy ensures that CockroachDB databases can be migrated to PostgreSQL with high fidelity, maintaining data integrity while adapting to PostgreSQL's specific requirements and optimizations.

## Advanced Features

### 1. Testing Mode

For testing and development, you can configure various validation and execution modes:

**Fast Migration Testing** (skip validation, preserve files):

```json
{
  "skip_validation": true,
  "postgres_import_enabled": false,
  "do_cleanup": false
}
```

**Schema Conversion Testing** (export only, no import):

```json
{
  "postgres_import_enabled": false,
  "do_cleanup": false,
  "skip_validation": false
}
```

These configurations allow you to:

- Test schema conversion without requiring PostgreSQL
- Validate data integrity before actual migration
- Inspect generated SQL files and validation reports
- Debug issues with temporary CockroachDB instance
- Examine exported data before import
- Preserve temporary resources for analysis

### 2. PostgreSQL Import Features

- Uses `psql` command for reliable import
- Handles authentication via environment variables
- Provides detailed error reporting
- Automatic PostgreSQL client download (Windows)

### 3. Cleanup (Conditional)

- Can be disabled via `do_cleanup: false` for debugging
- Gracefully stops temporary CockroachDB instance
- Removes all temporary files and directories
- Ensures no processes are left running
- When disabled, preserves temporary resources for inspection

## Troubleshooting

### Common Issues

#### 1. Certificate Errors

```Text
Error: Required certificate not found: /path/to/cockroachdb/certs/ca.crt
```

**Solution**: Ensure all required certificates are present in the `cockroachdb/certs/` directory.

#### 2. AWS Credentials

```Text
Error: AWS credentials not found in configuration
```

#### 6. PostgreSQL Client Download

```Text
Error: Failed to download PostgreSQL client
```

**Solution**: Check internet connection and firewall settings. The tool downloads from official PostgreSQL sites.

#### 7. Advanced DDL Processing

```Text
Warning: Advanced DDL processing failed, falling back to basic conversion
```

**Solution**: This is normal fallback behavior. Check logs for specific DDL patterns that couldn't be processed.

**Solution**: Verify AWS credentials are correctly configured in the config file or keys file.

#### 3. Port Conflicts

```Text
Error: CockroachDB failed to start
```

**Solution**: Change `cockroach_port` and `cockroach_http_port` in configuration to unused ports.

#### 4. PostgreSQL Connection

```Text
Error: psql command not found
```

**Solution**: Install PostgreSQL client tools or ensure `psql` is in your PATH.

#### 5. S3 Access

```Text
Error: Failed to restore backup
```

**Solution**: Verify S3 path exists and AWS credentials have appropriate permissions.

### Debug Steps

1. **Check Log File**: Review `migration.log` for detailed error messages
2. **Verify Prerequisites**: Ensure all required software is installed
3. **Test Connections**: Verify PostgreSQL and S3 access independently
4. **Certificate Validation**: Confirm certificate files are readable and valid
5. **Port Availability**: Ensure configured ports are not in use

### Manual Verification

After migration, verify the data:

```sql
-- Connect to PostgreSQL
psql -h localhost -p 5432 -U postgres

-- List databases
\l

-- Connect to migrated database
\c your_database_name

-- List tables
\dt

-- Verify data
SELECT COUNT(*) FROM your_table_name;
```

## Security Considerations

- **Certificates**: Keep CockroachDB certificates secure and with appropriate permissions
- **AWS Credentials**: Store AWS credentials securely, avoid hardcoding in scripts
- **PostgreSQL Password**: Use strong passwords and secure connection methods
- **Temporary Files**: Script automatically cleans up temporary files containing sensitive data
- **Network Security**: Temporary CockroachDB instance only binds to localhost

## Performance Notes

- **Large Datasets**: Migration time depends on backup size and network speed
- **Memory Usage**: Temporary CockroachDB instance may require significant memory
- **Disk Space**: Ensure sufficient disk space for temporary files and SQL export
- **Network Bandwidth**: S3 restore speed depends on available bandwidth

## Support

For issues or questions:

1. Check the `migration.log` file for detailed error information
2. Verify all prerequisites are met
3. Test individual components (S3 access, PostgreSQL connection, certificates)
4. Review configuration file for typos or incorrect values

## Example Complete Workflow

```bash
# 1. Install the package
pip install cockroach-migrator

# 2. Create configuration
cockroach-migrate --create-config

# 3. Edit configuration
nano migration_config.json

# 4. Run migration
cockroach-migrate --config migration_config.json

# 5. Verify results
psql -h localhost -p 5432 -U postgres -c "\l"

# 6. Check logs if needed
tail -f migration.log
```

## Migration Challenges & Solutions

### Common CockroachDB to PostgreSQL Migration Issues

#### 1. **Schema Compatibility Issues**

**Challenge**: CockroachDB uses different SQL syntax and features than PostgreSQL.

**Solution**: The migration tool provides comprehensive schema conversion:

- **Type mapping**: All CockroachDB types mapped to PostgreSQL equivalents
- **Syntax conversion**: CockroachDB-specific SQL converted to PostgreSQL standard
- **Feature removal**: Unsupported features safely removed or converted
- **Constraint handling**: Complex constraint dependencies properly ordered

**Example Conversion**:

```sql
-- CockroachDB Original
CREATE TABLE users (
    id SERIAL8 PRIMARY KEY,
    email STRING(255) UNIQUE,
    data JSON,
    created_at TIMESTAMPTZ DEFAULT now():::TIMESTAMPTZ
);

-- PostgreSQL Result
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    data JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);
```

#### 2. **Index Name Conflicts**

**Challenge**: PostgreSQL has stricter index naming requirements and global namespace conflicts.

**Solution**: Intelligent index renaming with collision detection:

```python
# Creates unique names like: dbname_indexname_a1b2
unique_index_name = create_unique_index_name(original_name, db_name, table_name)
```

#### 3. **Data Escaping & Encoding**

**Challenge**: CockroachDB and PostgreSQL handle string escaping differently.

**Solution**: Multi-layer escaping conversion:

- Double-quote escaping: `""` → `"`
- Single-quote preservation: `''` (same in both)
- JSON content fixing: Handles nested quote escaping
- Binary data conversion: `BYTES` → `BYTEA` with proper encoding

#### 4. **Large Dataset Handling**

**Challenge**: Memory limitations with large datasets during conversion.

**Solution**: Streaming and batch processing:

- Row-by-row processing for large tables
- Memory-efficient SELECT to INSERT conversion
- Temporary file management for intermediate results
- Progress tracking and resumable operations

#### 5. **Cross-Database Dependencies**

**Challenge**: CockroachDB allows cross-database references that PostgreSQL handles differently.

**Solution**: Dependency analysis and restructuring:

- Foreign key relationship mapping
- Cross-database reference resolution
- Constraint ordering to prevent dependency violations
- Database-specific namespace handling

### Quality Assurance Features

#### 1. **Pre-Migration Validation**

The tool performs comprehensive validation before any data modification:

```bash
# Test the migration (includes validation)
cockroach-migrate --config migration_config.json

# Skip validation for faster migration
cockroach-migrate --skip-validation --config migration_config.json
```

**Validation Checks**:

- Schema compatibility analysis
- Data type validation
- Constraint dependency verification
- Index compatibility testing
- Character encoding validation
- Length constraint verification

#### 2. **Test Import Capability**

Automated testing with local PostgreSQL instance:

```python
# Automatic test import before production
test_results = migrate_postgresql.test_postgresql_import(config, sql_file)
```

**Test Features**:

- Isolated test environment
- Complete import simulation
- Performance benchmarking
- Error detection and reporting
- Data integrity verification

#### 3. **Rollback & Recovery**

**Safe Migration Practices**:

- Non-destructive source data handling
- Temporary file preservation for debugging
- Detailed logging for troubleshooting
- Conditional cleanup for inspection
- Error state recovery procedures

### Performance Considerations

#### 1. **Migration Speed Optimization**

**Factors Affecting Performance**:

- **Network bandwidth**: S3 restore speed
- **Disk I/O**: Temporary file operations
- **CPU usage**: Schema conversion processing
- **Memory usage**: Large table handling

**Optimization Strategies**:

- Parallel processing where possible
- Efficient memory usage patterns
- Streaming data processing
- Batch operation optimization

#### 2. **Resource Management**

**Temporary Resource Usage**:

- CockroachDB instance: ~500MB-2GB RAM
- PostgreSQL test instance: ~200MB-1GB RAM
- Temporary files: 2-3x source data size
- Binary downloads: ~100-200MB per platform

**Resource Cleanup**:

- Automatic cleanup of temporary instances
- Configurable cleanup behavior
- Manual cleanup options for debugging
- Resource monitoring and reporting

### Enterprise Features

#### 1. **Security Considerations**

**Data Protection**:

- Certificate-based authentication
- Encrypted connections (TLS)
- Secure credential handling
- Temporary file encryption options
- Network isolation for test instances

**Access Control**:

- Role-based database access
- Credential separation
- Audit logging capabilities
- Secure cleanup procedures

#### 2. **Monitoring & Observability**

**Comprehensive Logging**:

- Migration progress tracking
- Performance metrics collection
- Error categorization and reporting
- Validation result documentation
- Debug information preservation

**Reporting Features**:

- Migration summary reports
- Validation result analysis
- Performance benchmarking
- Error analysis and recommendations
- Data quality assessments

The migration script is designed to be robust, secure, and handle various edge cases automatically while providing comprehensive logging for troubleshooting. The multi-layered approach ensures high-fidelity migration with extensive quality assurance and error recovery capabilities.
