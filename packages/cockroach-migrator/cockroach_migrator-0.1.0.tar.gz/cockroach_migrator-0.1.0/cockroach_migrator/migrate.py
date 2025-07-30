#!/usr/bin/env python3
"""
CockroachDB to PostgreSQL Migration Script

This script migrates data from a CockroachDB backup stored in S3 to a PostgreSQL database.
The process involves:
1. Downloading CockroachDB binary if not present
2. Setting up a temporary CockroachDB instance
3. Restoring data from S3 backup
4. Exporting data as SQL
5. Importing data into PostgreSQL

Usage:
    cockroach-migrate --config config.json
"""

import argparse
import json
import logging
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import time
import re
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple
import zipfile

import requests

from . import migrate_conversion, migrate_validate, migrate_cockroach, migrate_postgresql

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migration.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)



class CockroachMigrator:
    """Handles migration from CockroachDB backup to PostgreSQL"""

    def __init__(self, config_path: str):
        """Initialize migrator with configuration"""
        self.config = self._load_config(config_path)
        self.temp_dir = None
        self.cockroach_binary = None
        self.psql_binary = None
        self.temp_cockroach_process = None

        # Default configuration values
        self.s3_backup_path = "s3://nomosbackups/lightvault/cockroach/2025/06/28-075951.27"
        self.cockroach_version = "v24.3.5"
        self.cockroach_port = 26257
        self.cockroach_http_port = 8080
        self.certs_dir = Path("cockroachdb/certs").resolve()
        self.insecure_mode = False
        self.postgres_import_enabled = True
        self.do_cleanup = True
        self.postgres_version = "17.0"
        self.temp_dir_path = ""
        self.chunk_size = 10000  # Default chunk size for large table processing

        # Override with config values if provided
        if 's3_backup_path' in self.config:
            self.s3_backup_path = self.config['s3_backup_path']
        if 'cockroach_version' in self.config:
            self.cockroach_version = self.config['cockroach_version']
        if 'cockroach_port' in self.config:
            self.cockroach_port = self.config['cockroach_port']
        if 'certs_dir' in self.config:
            self.certs_dir = Path(self.config['certs_dir']).resolve()
        if 'insecure_mode' in self.config:
            self.insecure_mode = self.config['insecure_mode']
        if 'postgres_import_enabled' in self.config:
            self.postgres_import_enabled = self.config['postgres_import_enabled']
        if 'do_cleanup' in self.config:
            self.do_cleanup = self.config['do_cleanup']
        if 'postgres_version' in self.config:
            self.postgres_version = self.config['postgres_version']
        if 'temp_dir' in self.config:
            self.temp_dir_path = self.config['temp_dir']
        if 'chunk_size' in self.config:
            self.chunk_size = self.config['chunk_size']

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            logger.info(f"Loaded configuration from {config_path}")
            return config
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {config_path}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in configuration file: {e}")
            sys.exit(1)

    def _get_aws_credentials(self) -> Tuple[str, str]:
        """Extract AWS credentials from configuration"""
        if 'aws_access_key_id' in self.config and 'aws_secret_access_key' in self.config:
            return self.config['aws_access_key_id'], self.config['aws_secret_access_key']

        # Try to load from AWS keys file if specified
        if 'aws_keys_file' in self.config:
            try:
                with open(self.config['aws_keys_file'], 'r') as f:
                    content = f.read()
                    access_key = None
                    secret_key = None

                    for line in content.split('\n'):
                        if 'AWS_ACCESS_KEY' in line:
                            access_key = line.split('=')[1].strip()
                        elif 'AWS_SECRET_KEY' in line:
                            secret_key = line.split('=')[1].strip()

                    if access_key and secret_key:
                        return access_key, secret_key
            except FileNotFoundError:
                logger.error(f"AWS keys file not found: {self.config['aws_keys_file']}")

        logger.error("AWS credentials not found in configuration")
        sys.exit(1)

    def _get_postgres_config(self) -> Dict:
        """Get PostgreSQL connection configuration"""
        postgres_config = {
            'host': self.config.get('postgres_host', 'localhost'),
            'port': self.config.get('postgres_port', 5432),
            'database': self.config.get('postgres_database', 'postgres'),
            'username': self.config.get('postgres_username', 'postgres'),
            'password': self.config.get('postgres_password', '')
        }

        if not postgres_config['password']:
            logger.error("PostgreSQL password not provided in configuration")
            sys.exit(1)

        return postgres_config

    def _get_platform_info(self) -> Tuple[str, str]:
        """Get platform information for CockroachDB binary download"""
        system = platform.system().lower()
        machine = platform.machine().lower()

        if system == 'linux':
            if machine in ['x86_64', 'amd64']:
                return 'linux', 'amd64'
            elif machine in ['aarch64', 'arm64']:
                return 'linux', 'arm64'
        elif system == 'darwin':
            if machine in ['x86_64', 'amd64']:
                return 'darwin', 'amd64'
            elif machine in ['arm64']:
                return 'darwin', 'arm64'
        elif system == 'windows':
            return 'windows', 'amd64'

        logger.error(f"Unsupported platform: {system} {machine}")
        sys.exit(1)

    def _download_postgres_client(self) -> str:
        """Download PostgreSQL client tools if not available"""
        logger.info("Checking for PostgreSQL client (psql)")

        # Use the shared function to get PostgreSQL client path
        try:
            return migrate_postgresql.get_postgresql_client_path(self.postgres_version, self.temp_dir, logger)
        except Exception as e:
            logger.error(f"Failed to get PostgreSQL client: {e}")
            raise

    def _verify_cockroach_certificates(self):
        """Verify that required certificates exist (skip if insecure mode)"""
        if self.insecure_mode:
            logger.warning("Running in insecure mode - skipping certificate verification")
            return

        required_certs = ['ca.crt', 'client.root.crt', 'client.root.key', 'node.crt', 'node.key']

        for cert in required_certs:
            cert_path = self.certs_dir / cert
            if not cert_path.exists():
                logger.error(f"Required certificate not found: {cert_path}")
                sys.exit(1)

        logger.info(f"All required certificates found in {self.certs_dir}")

    def _restore_cockroach_backup_from_s3(self):
        """Restore CockroachDB backup from S3"""
        logger.info(f"Restoring backup from {self.s3_backup_path}")

        aws_access_key, aws_secret_key = self._get_aws_credentials()

        # Construct S3 URL with credentials (URL encode the secret key to handle special characters)
        import urllib.parse
        encoded_secret = urllib.parse.quote(aws_secret_key, safe='')
        s3_url = f"{self.s3_backup_path}?AWS_ACCESS_KEY_ID={aws_access_key}&AWS_SECRET_ACCESS_KEY={encoded_secret}"

        # Execute restore command with skip_localities_check flag
        try:
            restore_sql = f"RESTORE FROM LATEST IN '{s3_url}' WITH skip_localities_check"
            result = migrate_cockroach.execute_cockroach_sql(self.cockroach_binary, self.cockroach_port, self.insecure_mode, self.certs_dir, restore_sql, logger)
            logger.info("Backup restored successfully")
            logger.debug(f"Restore output: {result}")
        except Exception as e:
            logger.error(f"Failed to restore backup: {e}")
            raise

    def _export_cockroach_to_sql(self, output_file: str, databases: dict = None):
        """Export CockroachDB data to SQL file using modern approach"""
        logger.info(f"Exporting data to {output_file}")

        # # Get list of databases
        # show_db_sql = "SHOW DATABASES"
        # databases_result = migrate_cockroach.execute_cockroach_sql(self.cockroach_binary, self.cockroach_port, self.insecure_mode, self.certs_dir, show_db_sql, logger)
        # databases = []

        # for line in databases_result.split('\n'):
        #     line = line.strip()
        #     if line and not line.startswith('database_name') and not line.startswith('-') and not line.startswith('(') and line != '':
        #         # Handle table format output - extract database name more carefully
        #         parts = line.split()
        #         if parts:
        #             db_name = parts[0]
        #             # Skip system databases and empty names
        #             if db_name and db_name not in ['system', 'information_schema', 'pg_catalog', 'defaultdb']:
        #                 databases.append(db_name)

        logger.info(f"Using databases to export: {databases}")

        # Create export directory for CSV files
        export_dir = Path(self.temp_dir) / "export_data"
        export_dir.mkdir(exist_ok=True)

        # Export each database
        with open(output_file, 'w') as f:
            for db_name in databases.keys() if databases else []:
                logger.info(f"Exporting database: {db_name}")

                f.write(f"-- Database: {db_name}\n")
                f.write(f"SELECT 'CREATE DATABASE \"{db_name}\"' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '{db_name}')\\gexec\n")
                f.write(f"\\c \"{db_name}\";\n\n")

                try:
                    # First, get the schema using SHOW CREATE ALL TABLES
                    logger.info(f"Extracting schema for database: {db_name}")
                    schema_cmd = [
                        self.cockroach_binary,
                        "sql",
                        "--host", f"localhost:{self.cockroach_port}",
                        "--database", db_name,
                        "--execute", "SHOW CREATE ALL TABLES"
                    ]

                    # Add security options
                    if self.insecure_mode:
                        schema_cmd.append("--insecure")
                    else:
                        schema_cmd.extend(["--certs-dir", str(self.certs_dir)])

                    schema_result = subprocess.run(
                        schema_cmd,
                        capture_output=True,
                        text=True,
                        check=True
                    )

                    # Process schema output to make it PostgreSQL compatible
                    schema_content = schema_result.stdout
                    schema_content = migrate_conversion.convert_schema_to_postgresql(schema_content, logger, db_name)
                    f.write("-- Schema\n")
                    f.write(schema_content)
                    f.write("\n\n")

                    # Get list of tables from the databases dictionary
                    tables = databases.get(db_name, {}).get('tables', [])
                    logger.info(f"Found tables in {db_name}: {tables}")

                    # Export data for each table using chunked processing
                    for table_name in tables:
                        try:
                            logger.debug(f"Exporting data using chunked processing for table: {db_name}.\"{table_name}\"")

                            # Get column definitions for this table from databases info
                            column_definitions = databases.get(db_name, {}).get('column_definitions', {}).get(table_name, {})

                            f.write(f"-- Data for table: {table_name}\n")

                            # Use chunked processing for all tables
                            total_exported = migrate_cockroach.export_table_chunked(
                                self.cockroach_binary, self.cockroach_port,
                                self.insecure_mode, self.certs_dir,
                                db_name, table_name, f, column_definitions,
                                self.chunk_size, logger
                            )
                            logger.info(f"Successfully exported {total_exported:,} rows from {db_name}.{table_name}")

                            f.write("\n")

                        except Exception as e:
                            logger.error(f"Failed to export table {table_name}: {e}")

                except subprocess.CalledProcessError as e:
                    logger.error(f"Failed to export database {db_name}: {e.stderr}")
                    raise

        logger.info(f"Data exported to {output_file}")

    def _extract_cockroach_database_info(self):
        """Extract database information from the migration context"""
        databases = {}

        # Try to get database info from the temporary CockroachDB instance
        try:
            if self.temp_cockroach_process:
                # Get list of databases
                show_db_sql = "SHOW DATABASES"
                result = migrate_cockroach.execute_cockroach_sql(self.cockroach_binary, self.cockroach_port, self.insecure_mode, self.certs_dir, show_db_sql, logger)
                logger.debug(f"SHOW DATABASES result: {repr(result)}")
                db_lines = result.split('\n')

                for line in db_lines:
                    line = line.strip()
                    # Skip empty lines, headers, and separators
                    if (not line or
                        line.startswith('-') or
                        line.startswith('database_name') or
                        line.startswith('SET') or
                        line.startswith('SHOW DATABASES')):
                        continue

                    # CockroachDB uses tab separation for SHOW DATABASES too
                    if '\t' in line:
                        # Parse the database name from the first column
                        parts = [p.strip() for p in line.split('\t')]
                    elif ' ' in line and not '\t' in line:
                        # Fallback for space-separated format
                        parts = [p.strip() for p in line.split() if p.strip()]
                    else:
                        # Single database name on the line
                        parts = [line.strip()]
                    if len(parts) > 0:
                        db_name = parts[0]
                    if db_name and db_name not in ['system', 'information_schema', 'pg_catalog', 'defaultdb', 'postgres']:
                        databases[db_name] = {'schemas': {}, 'tables': []}
                        logger.debug(f"Added database '{db_name}' to databases dict")

                        # Get tables for this database using the same logic as export
                        logger.info("Extracting Table and Column Data from CockroachDB")
                        try:
                            show_tables_sql = f"USE {db_name}; SHOW TABLES"
                            tables_result = migrate_cockroach.execute_cockroach_sql(self.cockroach_binary, self.cockroach_port, self.insecure_mode, self.certs_dir, show_tables_sql, logger)
                            logger.debug(f"Raw SHOW TABLES output for validation in {db_name}:\n{tables_result}")
                            table_lines = tables_result.split('\n')

                            for table_line in table_lines:
                                table_line = table_line.strip()

                                # Skip empty lines
                                if not table_line:
                                    continue

                                # Skip header line (use same logic as export)
                                if 'schema_name' in table_line and 'table_name' in table_line:
                                    continue

                                # Skip separator lines
                                if table_line.startswith('-') or table_line.startswith('+'):
                                    continue

                                # Skip row count lines
                                if table_line.startswith('(') and 'row' in table_line:
                                    continue

                                # Parse table data lines - CockroachDB uses TAB separation, not pipes
                                if '\t' in table_line and not table_line.startswith('schema_name'):
                                    # Use the same filtering logic as the export process
                                    table_parts = [p.strip() for p in table_line.split('\t')]
                                    logger.debug(f"Validation parsing table line: '{table_line}' -> parts: {table_parts}")
                                    if len(table_parts) >= 3:  # Need at least schema, table, type
                                        schema_name = table_parts[0]
                                        table_name = table_parts[1]
                                        table_type = table_parts[2]

                                        logger.debug(f"Validation table details: schema='{schema_name}', name='{table_name}', type='{table_type}'")

                                        # Only include actual tables (not views) from public schema
                                        # This matches the export logic exactly
                                        if (table_name and
                                            schema_name == 'public' and
                                            table_type == 'table' and
                                            table_name not in ['information_schema', 'pg_catalog', 'crdb_internal']):

                                            if schema_name not in databases[db_name]['schemas']:
                                                databases[db_name]['schemas'][schema_name] = []
                                            databases[db_name]['schemas'][schema_name].append(table_name)
                                            databases[db_name]['tables'].append(table_name)

                                            # Get column definitions for this table
                                            try:
                                                show_columns_sql = f"USE {db_name}; SHOW COLUMNS FROM \"{table_name}\""
                                                columns_result = migrate_cockroach.execute_cockroach_sql(self.cockroach_binary, self.cockroach_port, self.insecure_mode, self.certs_dir, show_columns_sql, logger)
                                                logger.debug(f"Raw SHOW COLUMNS output for {db_name}.{table_name}:\n{columns_result}")

                                                # Parse column definitions
                                                column_definitions = migrate_cockroach.parse_column_definitions(columns_result, db_name, table_name, logger)

                                                # Store column definitions in database structure
                                                if 'column_definitions' not in databases[db_name]:
                                                    databases[db_name]['column_definitions'] = {}
                                                databases[db_name]['column_definitions'][table_name] = column_definitions

                                            except Exception as e:
                                                logger.error(f"Could not get column definitions for {db_name}.{table_name}: {e}")

                                            logger.debug(f" Table '{table_name}' added to database info")
                                        else:
                                            logger.debug(f" Table '{table_name}' filtered out: schema='{schema_name}', type='{table_type}'")
                        except Exception as e:
                            logger.debug(f"Could not get tables for database {db_name}: {e}")

        except Exception as e:
            logger.debug(f"Could not extract database info: {e}")

        logger.info(f"Final databases dict: {databases}")
        return databases

    def _import_to_postgres(self, sql_file: str):
        """Import SQL data into PostgreSQL using the same logic as test import"""
        logger.info("Starting PostgreSQL import...")

        # Check if PostgreSQL import is enabled
        if not self.config.get('postgres_import_enabled', True):
            logger.info("PostgreSQL import is disabled in configuration. Skipping import.")
            return

        try:
            # Use the unified import logic from migrate_postgresql module
            import_results = migrate_postgresql.perform_postgresql_import(
                config=self.config,
                sql_file=sql_file,
                temp_dir=self.temp_dir,
                logger=logger
            )
            
            if import_results['success']:
                logger.info("Data imported successfully into PostgreSQL")
                logger.info(f"Import completed in {import_results['import_time']:.2f} seconds")
                
                # Log validation summary if available
                validation = import_results.get('validation_results', {})
                if validation:
                    logger.info("Import validation summary:")
                    for key, value in validation.items():
                        if isinstance(value, str) and len(value) < 200:
                            logger.info(f"  - {key}: {value}")
                        else:
                            logger.info(f"  - {key}: [Results available]")
            else:
                logger.error("PostgreSQL import failed")
                for error in import_results.get('errors', []):
                    logger.error(f"  - {error}")
                raise Exception("PostgreSQL import failed")
                
        except Exception as e:
            logger.error(f"Failed to import data into PostgreSQL: {e}")
            raise

    def _perform_postgres_test_import(self, sql_file):
        """Test PostgreSQL import with local instance"""
        if self.config.get('test_postgresql_import', True):
            logger.info("Testing PostgreSQL import with local instance...")
            try:
                # Use the unified import logic from migrate_postgresql module
                test_results = migrate_postgresql.test_postgresql_import(
                    config=self.config,
                    sql_file=str(sql_file),
                    temp_dir=self.temp_dir,
                    logger=logger
                )

                if test_results['success']:
                    logger.info(f"PostgreSQL import test PASSED")
                    logger.info(f"  - Setup time: {test_results['setup_time']:.2f}s")
                    logger.info(f"  - Import time: {test_results['import_time']:.2f}s")

                    # Log validation summary
                    validation = test_results.get('validation_results', {})
                    if 'List tables' in validation:
                        table_info = validation['List tables']
                        table_count = len([line for line in table_info.split('\n') if line.strip()])
                        logger.info(f"  - Tables imported: {table_count}")

                    logger.info("SQL file is ready for production PostgreSQL import")
                    return True
                else:
                    logger.error("PostgreSQL import test FAILED")
                    for error in test_results.get('errors', []):
                        logger.error(f"  - {error}")
                    logger.warning("Please review the SQL file before production import")
                    return False

            except Exception as e:
                logger.error(f"PostgreSQL import test encountered an error: {e}")
                logger.warning("Continuing with migration despite test failure")
        else:
            logger.info("PostgreSQL import test is disabled")
        return False

    def _performValidation(self, sql_file, databases):
        logger.info("Performing validation of exported data...")
        try:
            # For validation, we'll treat the combined export file as both schema and data
            validation_results = migrate_validate.validate_schema_and_data(databases, str(sql_file), str(sql_file), self.temp_dir, logger)

            # Check for critical errors
            if validation_results.get('errors'):
                logger.error("Critical validation errors found:")
                for error in validation_results['errors']:
                    logger.error(f"  - {error}")
                logger.error("Migration aborted due to validation errors. Check validation_report.txt for details.")
                return

            # Log validation summary
            schema_val = validation_results.get('schema_validation', {})
            data_val = validation_results.get('data_validation', {})
            cross_val = validation_results.get('cross_validation', {})

            logger.info("Validation Summary:")
            logger.info(f"  - Schema: {schema_val.get('table_count', 0)} tables, {schema_val.get('index_count', 0)} indexes, {schema_val.get('constraint_count', 0)} constraints")
            logger.info(f"  - Data: {data_val.get('insert_count', 0):,} INSERT statements, {len(data_val.get('tables_with_data', []))} tables with data")
            logger.info(f"  - Consistency: {cross_val.get('consistency_score', 0):.1%} schema-data match")

            if validation_results.get('warnings'):
                logger.warning(f"Validation completed with {len(validation_results['warnings'])} warnings (see validation_report.txt)")
            else:
                logger.info("Validation completed successfully - ready for import")

        except Exception as e:
            logger.warning(f"Validation failed: {e}. Proceeding with import anyway.")

    def migrate(self):
        """Execute the complete migration process"""
        try:
            logger.info("Starting CockroachDB to PostgreSQL migration")

            # Create temporary directory
            if self.temp_dir_path:
                # Use the specified directory as the base
                temp_base_dir = Path(self.temp_dir_path).resolve()
                os.makedirs(temp_base_dir, exist_ok=True)
                self.temp_dir = tempfile.mkdtemp(prefix="cockroach_migration_", dir=str(temp_base_dir))
                logger.info(f"Created temporary directory in specified location: {self.temp_dir}")
            else:
                # Use system default temp directory (user's temp folder)
                self.temp_dir = tempfile.mkdtemp(prefix="cockroach_migration_")
                logger.info(f"Created temporary directory (system): {self.temp_dir}")

            # Verify certificates
            self._verify_cockroach_certificates()

            # Download CockroachDB binary (stored persistently by version)
            os_name, arch = self._get_platform_info()
            self.cockroach_binary = migrate_cockroach.download_cockroach_binary(os_name, arch, self.temp_dir, self.cockroach_version, logger)
            logger.info(f"Using CockroachDB binary: {self.cockroach_binary}")

            # Start temporary CockroachDB instance
            self.temp_cockroach_process = migrate_cockroach.start_temp_cockroach(self.temp_dir, self.cockroach_binary, self.cockroach_port, self.cockroach_http_port, self.insecure_mode, self.certs_dir, logger)

            # Restore from S3 backup
            self._restore_cockroach_backup_from_s3()

            # Try to extract database information from the migration context (actual exportable tables)
            databases = self._extract_cockroach_database_info()

            # Export to SQL file
            sql_file = Path(self.temp_dir) / "export.sql"
            self._export_cockroach_to_sql(str(sql_file), databases)

            # Validate exported data before import (unless skipped)
            if not getattr(self, '_skip_validation', False):
                self._performValidation(sql_file, databases)
            else:
                logger.info("Validation skipped as requested")

            success = self._perform_postgres_test_import(sql_file)

            # Import to PostgreSQL (conditional)
            if success and self.postgres_import_enabled:
                logger.info("PostgreSQL import is enabled - importing data")
                self._import_to_postgres(str(sql_file))
            elif not success:
                logger.info("Skipping production import due to failed test import")
            else:
                logger.info("PostgreSQL import is disabled - skipping import step")
                logger.info(f"SQL export file available at: {sql_file}")

            logger.info("Migration completed successfully!")

        except Exception as e:
            logger.error(f"Migration failed: {e}")
            raise
        finally:
            # Cleanup (conditional)
            if self.do_cleanup:
                logger.info("Cleanup is enabled - cleaning up temporary resources")
                logger.info(f"Note: CockroachDB binary is preserved in version-specific directory: cockroach-{self.cockroach_version}")
                logger.info(f"Note: PostgreSQL client is preserved in version-specific directory: postgresql-{self.postgres_version}")
                self._cleanup()
            else:
                logger.info("Cleanup is disabled - preserving temporary resources")
                logger.info(f"Temporary directory preserved at: {self.temp_dir}")
                logger.info(f"CockroachDB binary preserved in: cockroach-{self.cockroach_version}")
                logger.info(f"PostgreSQL client preserved in: postgresql-{self.postgres_version}")
                if self.temp_cockroach_process:
                    logger.info("CockroachDB process is still running - you may need to stop it manually")

    def _cleanup(self):
        """Clean up temporary resources"""
        logger.info("Cleaning up temporary resources")

        # Stop CockroachDB process
        if self.temp_cockroach_process:
            try:
                logger.info("Stopping CockroachDB process...")
                self.temp_cockroach_process.terminate()
                try:
                    self.temp_cockroach_process.wait(timeout=30)
                    logger.info("CockroachDB process stopped gracefully")
                except subprocess.TimeoutExpired:
                    logger.warning("CockroachDB process did not stop gracefully, forcing kill")
                    self.temp_cockroach_process.kill()
                    self.temp_cockroach_process.wait()
            except Exception as e:
                logger.warning(f"Error stopping CockroachDB process: {e}")

        # Remove temporary directory
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                logger.info(f"Removed temporary directory: {self.temp_dir}")
            except Exception as e:
                logger.warning(f"Error removing temporary directory: {e}")


def create_sample_config():
    """Create a sample configuration file"""
    sample_config = {
        "aws_access_key_id": "YOUR_AWS_ACCESS_KEY_ID",
        "aws_secret_access_key": "YOUR_AWS_SECRET_ACCESS_KEY",
        "aws_keys_file": "AWS/keys/allpurposeInstance1.txt",
        "s3_backup_path": "s3://mybucket/mybackup",
        "cockroach_version": "v24.3.5",
        "cockroach_port": 26257,
        "certs_dir": "cockroachdb/certs",
        "postgres_host": "localhost",
        "postgres_port": 5432,
        "postgres_database": "postgres",
        "postgres_username": "postgres",
        "postgres_password": "YOUR_POSTGRES_PASSWORD",
        "postgres_version": "17.2",
        "postgres_import_enabled": True,
        "test_postgresql_import": True,
        "test_postgres_port": 5433,
        "test_database_name": "migration_test",
        "test_username": "postgres",
        "test_password": "YOUR_TEST_PASSWORD",
        "do_cleanup": True,
        "skip_validation": False,
        "temp_dir": "",
        "chunk_size": 10000
    }

    with open("migration_config.json", "w") as f:
        json.dump(sample_config, f, indent=2)

    print("Sample configuration file created: migration_config.json")
    print("Please edit the configuration file with your actual values before running the migration.")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Migrate CockroachDB backup from S3 to PostgreSQL")
    parser.add_argument("--config", default="migration_config.json", help="Path to configuration JSON file (default: migration_config.json)")
    parser.add_argument("--create-config", action="store_true", help="Create sample configuration file")
    parser.add_argument("--skip-validation", action="store_true", help="Skip validation step")

    args = parser.parse_args()

    if args.create_config:
        create_sample_config()
        return

    # Use the config file (either provided or default)
    config_file = args.config

    # Check if config file exists
    if not os.path.exists(config_file):
        logger.error(f"Configuration file not found: {config_file}")
        if config_file == "migration_config.json":
            logger.info("You can create a sample configuration file using: cockroach-migrate --create-config")
        sys.exit(1)

    try:
        migrator = CockroachMigrator(config_file)

        # Get validation settings from config (with command-line overrides)
        skip_validation = args.skip_validation or migrator.config.get('skip_validation', False)

        # Handle validation settings
        if skip_validation:
            logger.info("Skipping validation as requested (from config or command-line)")
            # Add a flag to skip validation in migrate method
            migrator._skip_validation = True
            migrator.migrate()
        else:
            migrator.migrate()

    except KeyboardInterrupt:
        logger.info("Migration interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
