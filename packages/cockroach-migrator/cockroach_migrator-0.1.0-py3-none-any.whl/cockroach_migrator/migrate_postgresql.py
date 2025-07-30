#!/usr/bin/env python3
"""
PostgreSQL Module

Contains functions related to postgresql functionality.

There is also a test module that provides functionality to:
1. Download and set up a local PostgreSQL instance
2. Import SQL files exported from the migration process
3. Validate the imported data
4. Clean up temporary PostgreSQL resources
"""

import logging
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile
from pathlib import Path
from typing import Dict, Optional, Tuple
import requests


# Shared utility functions for PostgreSQL operations
def get_platform_info() -> Tuple[str, str]:
    """Get platform information for PostgreSQL binary download"""
    system = platform.system().lower()
    machine = platform.machine().lower()

    if system == 'linux':
        if machine in ['x86_64', 'amd64']:
            return 'linux', 'x64'
        elif machine in ['aarch64', 'arm64']:
            return 'linux', 'arm64'
    elif system == 'darwin':
        if machine in ['x86_64', 'amd64']:
            return 'darwin', 'x64'
        elif machine in ['arm64']:
            return 'darwin', 'arm64'
    elif system == 'windows':
        return 'windows', 'x64'

    raise Exception(f"Unsupported platform: {system} {machine}")


def download_postgresql_binary(postgres_version: str, temp_dir: str, logger: logging.Logger) -> str:
    """Download PostgreSQL binary if not available - shared implementation"""
    logger.info("Setting up PostgreSQL binary")

    # Create persistent directory for PostgreSQL binaries based on version
    script_dir = Path.cwd()
    postgres_dir = script_dir / f"postgresql-{postgres_version}"

    # Check if binary already exists
    system = platform.system().lower()
    postgres_executable = 'postgres.exe' if system == 'windows' else 'postgres'
    local_postgres_binary = postgres_dir / "bin" / postgres_executable

    if local_postgres_binary.exists():
        logger.info(f"PostgreSQL binary already exists: {local_postgres_binary}")
        return str(local_postgres_binary)

    logger.info(f"PostgreSQL binary not found, downloading to: {postgres_dir}")
    postgres_dir.mkdir(exist_ok=True)

    # Get platform info
    os_name, arch = get_platform_info()
    version = postgres_version

    # Construct download URL based on platform
    if os_name == "windows":
        postgres_url = f"https://get.enterprisedb.com/postgresql/postgresql-{version}-1-windows-x64-binaries.zip"
        postgres_filename = f"postgresql-{version}-windows-x64-binaries.zip"
    else:
        # For Linux/macOS, we'll provide instructions instead of downloading
        logger.error("Automatic PostgreSQL binary download is only supported on Windows")
        logger.error("Please install PostgreSQL manually:")
        if os_name == "linux":
            logger.error("  Ubuntu/Debian: sudo apt-get install postgresql postgresql-contrib")
            logger.error("  CentOS/RHEL: sudo yum install postgresql-server postgresql-contrib")
        elif os_name == "darwin":
            logger.error("  macOS: brew install postgresql")
        raise Exception("PostgreSQL binary download not supported on this platform")

    try:
        # Download archive
        postgres_zip_path = Path(temp_dir) / postgres_filename

        logger.info(f"Downloading PostgreSQL from {postgres_url}")
        response = requests.get(postgres_url, stream=True)
        response.raise_for_status()

        with open(postgres_zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        # Extract the archive
        postgres_extract_dir = Path(temp_dir) / "postgresql_temp"
        postgres_extract_dir.mkdir(exist_ok=True)

        with zipfile.ZipFile(postgres_zip_path, 'r') as zip_ref:
            zip_ref.extractall(postgres_extract_dir)

        # Find the extracted PostgreSQL directory
        extracted_postgres_dir = None
        for item in postgres_extract_dir.iterdir():
            if item.is_dir() and "postgresql" in item.name.lower():
                extracted_postgres_dir = item
                break

        if not extracted_postgres_dir:
            # Look for any directory that contains bin/postgres.exe
            for root, dirs, files in os.walk(postgres_extract_dir):
                if postgres_executable in files:
                    extracted_postgres_dir = Path(root).parent
                    break

        if not extracted_postgres_dir:
            raise Exception("Could not find PostgreSQL directory structure in downloaded package")

        # Move to persistent location
        if postgres_dir.exists():
            shutil.rmtree(postgres_dir)

        shutil.move(str(extracted_postgres_dir), str(postgres_dir))

        # Verify binary exists
        if not local_postgres_binary.exists():
            # Try to find postgres in the moved directory structure
            postgres_path = None
            for root, dirs, files in os.walk(postgres_dir):
                if postgres_executable in files:
                    postgres_path = Path(root) / postgres_executable
                    break

            if not postgres_path:
                raise Exception(f"Could not find {postgres_executable} in downloaded PostgreSQL package")

            local_postgres_binary = postgres_path

        # Clean up temporary files
        os.remove(postgres_zip_path)
        if postgres_extract_dir.exists():
            shutil.rmtree(postgres_extract_dir)

        logger.info(f"PostgreSQL binary downloaded: {local_postgres_binary}")
        return str(local_postgres_binary)

    except Exception as e:
        logger.error(f"Failed to download PostgreSQL binary: {e}")
        raise


def get_postgresql_client_path(postgres_version: str, temp_dir: str, logger: logging.Logger) -> str:
    """Get path to PostgreSQL client (psql), downloading if necessary"""
    # First check if psql is already available in system PATH
    psql_cmd = shutil.which('psql')
    if psql_cmd:
        logger.info("PostgreSQL client (psql) is already available in system PATH")
        return psql_cmd

    # Download PostgreSQL binaries and get psql path
    postgres_binary = download_postgresql_binary(postgres_version, temp_dir, logger)
    
    # Get psql from the same directory
    system = platform.system().lower()
    psql_executable = 'psql.exe' if system == 'windows' else 'psql'
    psql_cmd = str(Path(postgres_binary).parent / psql_executable)
    
    if not Path(psql_cmd).exists():
        raise Exception(f"psql binary not found at expected location: {psql_cmd}")
    
    logger.info(f"Using PostgreSQL client: {psql_cmd}")
    return psql_cmd


def execute_postgresql_command(psql_cmd: str, host: str, port: int, username: str, password: str,
                             database: str, command: str = None, sql_file: str = None,
                             additional_args: list = None, logger: logging.Logger = None) -> subprocess.CompletedProcess:
    """Execute a PostgreSQL command using psql - shared implementation"""
    if not logger:
        logger = logging.getLogger(__name__)
    
    # Set environment for password
    env = os.environ.copy()
    env['PGPASSWORD'] = password

    # Build base command
    cmd = [
        psql_cmd,
        "-h", host,
        "-p", str(port),
        "-U", username,
        "-d", database
    ]
    
    # Add command or file
    if command:
        cmd.extend(["-c", command])
    elif sql_file:
        cmd.extend(["-f", sql_file])
    else:
        raise ValueError("Either command or sql_file must be provided")
    
    # Add additional arguments
    if additional_args:
        cmd.extend(additional_args)

    try:
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            check=True
        )
        return result
    except subprocess.CalledProcessError as e:
        logger.error(f"PostgreSQL command failed: {e.stderr}")
        raise


class PostgreSQLTester:
    """Handles local PostgreSQL instance setup and SQL import testing"""

    def __init__(self, config: Dict, temp_dir: str = None, logger: logging.Logger = None):
        """Initialize PostgreSQL tester with configuration"""
        self.config = config
        self.temp_dir = temp_dir
        self.logger = logger or logging.getLogger(__name__)

        # PostgreSQL configuration
        self.postgres_version = config.get('postgres_version', '17.2')
        self.postgres_port = config.get('test_postgres_port', 5433)  # Use different port for testing
        self.postgres_data_dir = None
        self.postgres_binary_dir = None
        self.postgres_process = None
        self.postgres_initialized = False

        # Test database configuration
        self.test_db_name = config.get('test_database_name', 'migration_test')
        self.test_username = config.get('test_username', 'postgres')
        self.test_password = config.get('test_password', 'YOUR_TEST_PASSWORD')

    def _download_postgresql_binary(self) -> str:
        """Download PostgreSQL binary if not available"""
        postgres_binary = download_postgresql_binary(self.postgres_version, self.temp_dir, self.logger)
        
        # Set binary directory for other methods
        self.postgres_binary_dir = Path(postgres_binary).parent
        
        return postgres_binary

    def _initialize_postgres_data_directory(self):
        """Initialize PostgreSQL data directory"""
        if self.postgres_initialized:
            return

        self.postgres_data_dir = Path(self.temp_dir) / "postgres_data"
        self.postgres_data_dir.mkdir(exist_ok=True)

        # Get initdb binary path
        system = platform.system().lower()
        initdb_executable = 'initdb.exe' if system == 'windows' else 'initdb'
        if not self.postgres_binary_dir:
            raise Exception("PostgreSQL binary directory not set. Please run _download_postgresql_binary() first.")

        initdb_binary = self.postgres_binary_dir / initdb_executable

        if not initdb_binary.exists():
            # Try to find initdb in system PATH
            initdb_binary = shutil.which('initdb')
            if not initdb_binary:
                raise Exception(f"initdb binary not found in {self.postgres_binary_dir} or system PATH")

        self.logger.info(f"Initializing PostgreSQL data directory: {self.postgres_data_dir}")

        # Create password file for initdb
        password_file = Path(self.temp_dir) / "postgres_password.txt"

        try:
            with open(password_file, 'w') as f:
                f.write(self.test_password)

            # Initialize database cluster
            cmd = [
                str(initdb_binary),
                "-D", str(self.postgres_data_dir),
                "-U", self.test_username,
                "--pwfile", str(password_file),
                "--auth-local=trust",
                "--auth-host=md5"
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )

            self.logger.info("PostgreSQL data directory initialized successfully")
            self.logger.debug(f"initdb output: {result.stdout}")
            self.postgres_initialized = True

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to initialize PostgreSQL data directory: {e.stderr}")
            raise Exception(f"initdb failed: {e.stderr}")
        except Exception as e:
            self.logger.error(f"Error initializing PostgreSQL: {e}")
            raise
        finally:
            # Clean up password file
            if password_file.exists():
                password_file.unlink()

    def _start_postgres_server(self):
        """Start local PostgreSQL server"""
        if self.postgres_process and self.postgres_process.poll() is None:
            self.logger.info("PostgreSQL server is already running")
            return

        # Get postgres binary path
        system = platform.system().lower()
        postgres_executable = 'postgres.exe' if system == 'windows' else 'postgres'

        if not self.postgres_binary_dir:
            raise Exception("PostgreSQL binary directory not set. Please run _download_postgresql_binary() first.")

        postgres_binary = self.postgres_binary_dir / postgres_executable

        if not postgres_binary.exists():
            # Try to find postgres in system PATH
            postgres_binary = shutil.which('postgres')
            if not postgres_binary:
                raise Exception(f"postgres binary not found in {self.postgres_binary_dir} or system PATH")

        self.logger.info(f"Starting PostgreSQL server on port {self.postgres_port}")

        # Create log file
        log_file = Path(self.temp_dir) / "postgres.log"

        # Start PostgreSQL server
        cmd = [
            str(postgres_binary),
            "-D", str(self.postgres_data_dir),
            "-p", str(self.postgres_port),
            "-F"  # Don't run in background
        ]

        # Add Unix socket directory only on non-Windows systems
        system = platform.system().lower()
        if system != 'windows':
            cmd.extend(["-k", str(self.temp_dir)])

        try:
            with open(log_file, 'w') as log:
                self.postgres_process = subprocess.Popen(
                    cmd,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    cwd=self.temp_dir
                )

            # Wait for server to start
            self._wait_for_postgres_ready()
            self.logger.info("PostgreSQL server started successfully")

        except Exception as e:
            self.logger.error(f"Failed to start PostgreSQL server: {e}")
            raise

    def _wait_for_postgres_ready(self, timeout: int = 30):
        """Wait for PostgreSQL server to be ready"""
        self.logger.info("Waiting for PostgreSQL server to be ready...")

        # Get pg_isready binary path
        system = platform.system().lower()
        pg_isready_executable = 'pg_isready.exe' if system == 'windows' else 'pg_isready'
        pg_isready_binary = self.postgres_binary_dir / pg_isready_executable

        if not pg_isready_binary.exists():
            # Try to find pg_isready in system PATH
            pg_isready_binary = shutil.which('pg_isready')
            if not pg_isready_binary:
                # Fallback to simple connection test
                self._wait_for_postgres_connection(timeout)
                return

        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                result = subprocess.run(
                    [str(pg_isready_binary), "-h", "localhost", "-p", str(self.postgres_port)],
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                if result.returncode == 0:
                    self.logger.info("PostgreSQL server is ready")
                    return

            except subprocess.TimeoutExpired:
                pass
            except Exception as e:
                self.logger.debug(f"pg_isready check failed: {e}")

            time.sleep(1)

        raise Exception(f"PostgreSQL server did not become ready within {timeout} seconds")

    def _wait_for_postgres_connection(self, timeout: int = 30):
        """Fallback method to wait for PostgreSQL connection"""
        import socket

        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                with socket.create_connection(('localhost', self.postgres_port), timeout=1):
                    self.logger.info("PostgreSQL server is accepting connections")
                    return
            except (socket.error, ConnectionRefusedError):
                pass

            time.sleep(1)

        raise Exception(f"PostgreSQL server did not accept connections within {timeout} seconds")

    def _create_test_database(self):
        """Create test database for import"""
        self.logger.info(f"Creating test database: {self.test_db_name}")

        # Get createdb binary path
        system = platform.system().lower()
        createdb_executable = 'createdb.exe' if system == 'windows' else 'createdb'
        createdb_binary = self.postgres_binary_dir / createdb_executable

        if not createdb_binary.exists():
            # Try to find createdb in system PATH
            createdb_binary = shutil.which('createdb')
            if not createdb_binary:
                raise Exception("createdb binary not found")

        # Set environment for password
        env = os.environ.copy()
        env['PGPASSWORD'] = self.test_password

        cmd = [
            str(createdb_binary),
            "-h", "localhost",
            "-p", str(self.postgres_port),
            "-U", self.test_username,
            self.test_db_name
        ]

        try:
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                check=True
            )

            self.logger.info(f"Test database '{self.test_db_name}' created successfully")

        except subprocess.CalledProcessError as e:
            if "already exists" in e.stderr:
                self.logger.info(f"Test database '{self.test_db_name}' already exists")
            else:
                self.logger.error(f"Failed to create test database: {e.stderr}")
                raise

    def _import_sql_file(self, sql_file: str):
        """Import SQL file into test database"""
        self.logger.info(f"Importing SQL file: {sql_file}")

        # Get psql binary path
        system = platform.system().lower()
        psql_executable = 'psql.exe' if system == 'windows' else 'psql'
        psql_binary = self.postgres_binary_dir / psql_executable

        if not psql_binary.exists():
            # Try to find psql in system PATH
            psql_binary = shutil.which('psql')
            if not psql_binary:
                raise Exception("psql binary not found")

        try:
            result = execute_postgresql_command(
                psql_cmd=str(psql_binary),
                host="localhost",
                port=self.postgres_port,
                username=self.test_username,
                password=self.test_password,
                database=self.test_db_name,
                sql_file=sql_file,
                additional_args=["--set", "ON_ERROR_STOP=on", "-v", "ON_ERROR_STOP=1"],
                logger=self.logger
            )

            self.logger.info("SQL file imported successfully")
            self.logger.debug(f"Import output: {result.stdout}")

            return result.stdout

        except Exception as e:
            self.logger.error(f"Failed to import SQL file: {e}")
            raise

    def _validate_import(self):
        """Validate the imported data"""
        self.logger.info("Validating imported data...")

        # Get psql binary path
        system = platform.system().lower()
        psql_executable = 'psql.exe' if system == 'windows' else 'psql'
        psql_binary = self.postgres_binary_dir / psql_executable

        if not psql_binary.exists():
            psql_binary = shutil.which('psql')
            if not psql_binary:
                raise Exception("psql binary not found")

        # Set environment for password
        env = os.environ.copy()
        env['PGPASSWORD'] = self.test_password

        validation_queries = [
            ("Database connection", "SELECT version();"),
            ("List databases", "SELECT datname FROM pg_database WHERE datistemplate = false;"),
            ("List tables", "SELECT schemaname, tablename FROM pg_tables WHERE schemaname = 'public';"),
            ("Table row counts", """
                SELECT
                    schemaname || '.' || tablename as table_name,
                    'Row count query would be executed here' as note
                FROM pg_tables
                WHERE schemaname = 'public'
                ORDER BY tablename;
            """)
        ]

        validation_results = {}

        for query_name, query in validation_queries:
            try:
                cmd = [
                    str(psql_binary),
                    "-h", "localhost",
                    "-p", str(self.postgres_port),
                    "-U", self.test_username,
                    "-d", self.test_db_name,
                    "-c", query,
                    "-t"  # Tuples only (no headers)
                ]

                result = subprocess.run(
                    cmd,
                    env=env,
                    capture_output=True,
                    text=True,
                    check=True
                )

                validation_results[query_name] = result.stdout.strip()
                self.logger.info(f"{query_name}: OK")

            except subprocess.CalledProcessError as e:
                self.logger.warning(f"{query_name}: FAILED - {e.stderr}")
                validation_results[query_name] = f"ERROR: {e.stderr}"

        # Get actual row counts for each table
        try:
            table_counts = self._get_table_row_counts()
            if table_counts:
                validation_results["Actual table row counts"] = table_counts
        except Exception as e:
            self.logger.warning(f"Could not get table row counts: {e}")
            validation_results["Actual table row counts"] = f"ERROR: {e}"

        return validation_results

    def _get_table_row_counts(self):
        """Get row counts for all tables in the public schema"""
        # Get psql binary path
        system = platform.system().lower()
        psql_executable = 'psql.exe' if system == 'windows' else 'psql'
        psql_binary = self.postgres_binary_dir / psql_executable

        if not psql_binary.exists():
            psql_binary = shutil.which('psql')
            if not psql_binary:
                raise Exception("psql binary not found")

        # Set environment for password
        env = os.environ.copy()
        env['PGPASSWORD'] = self.test_password

        # First get list of tables
        tables_query = "SELECT tablename FROM pg_tables WHERE schemaname = 'public';"

        cmd = [
            str(psql_binary),
            "-h", "localhost",
            "-p", str(self.postgres_port),
            "-U", self.test_username,
            "-d", self.test_db_name,
            "-c", tables_query,
            "-t"  # Tuples only (no headers)
        ]

        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            check=True
        )

        tables = [line.strip() for line in result.stdout.split('\n') if line.strip()]

        if not tables:
            return "No tables found in public schema"

        # Get row count for each table
        row_counts = []
        for table in tables:
            try:
                count_query = f"SELECT COUNT(*) FROM \"{table}\";"
                cmd = [
                    str(psql_binary),
                    "-h", "localhost",
                    "-p", str(self.postgres_port),
                    "-U", self.test_username,
                    "-d", self.test_db_name,
                    "-c", count_query,
                    "-t"
                ]

                count_result = subprocess.run(
                    cmd,
                    env=env,
                    capture_output=True,
                    text=True,
                    check=True
                )

                count = count_result.stdout.strip()
                row_counts.append(f"{table}: {count} rows")

            except Exception as e:
                row_counts.append(f"{table}: ERROR - {e}")

        return "\n".join(row_counts)

    def _stop_postgres_server(self):
        """Stop PostgreSQL server"""
        if not self.postgres_process:
            return

        self.logger.info("Stopping PostgreSQL server...")

        try:
            # Try graceful shutdown first
            self.postgres_process.terminate()
            try:
                self.postgres_process.wait(timeout=10)
                self.logger.info("PostgreSQL server stopped gracefully")
            except subprocess.TimeoutExpired:
                self.logger.warning("PostgreSQL server did not stop gracefully, forcing kill")
                self.postgres_process.kill()
                self.postgres_process.wait()

        except Exception as e:
            self.logger.warning(f"Error stopping PostgreSQL server: {e}")

        self.postgres_process = None

    def test_import(self, sql_file: str) -> Dict:
        """Test import of SQL file into local PostgreSQL instance"""
        self.logger.info("Starting PostgreSQL import test...")

        results = {
            'success': False,
            'setup_time': 0,
            'import_time': 0,
            'validation_results': {},
            'errors': []
        }

        try:
            start_time = time.time()

            # Download PostgreSQL binary if needed
            self._download_postgresql_binary()

            # Initialize data directory
            self._initialize_postgres_data_directory()

            # Start PostgreSQL server
            self._start_postgres_server()

            # Create test database
            self._create_test_database()

            setup_time = time.time() - start_time
            results['setup_time'] = setup_time
            self.logger.info(f"PostgreSQL setup completed in {setup_time:.2f} seconds")

            # Import SQL file
            import_start = time.time()
            self._import_sql_file(sql_file)
            import_time = time.time() - import_start
            results['import_time'] = import_time
            self.logger.info(f"SQL import completed in {import_time:.2f} seconds")

            # Validate import
            validation_results = self._validate_import()
            results['validation_results'] = validation_results

            results['success'] = True
            self.logger.info("PostgreSQL import test completed successfully")

        except Exception as e:
            error_msg = f"PostgreSQL import test failed: {e}"
            self.logger.error(error_msg)
            results['errors'].append(error_msg)

        finally:
            # Always try to stop the server
            self._stop_postgres_server()

        return results

    def cleanup(self):
        """Clean up PostgreSQL test resources"""
        self.logger.info("Cleaning up PostgreSQL test resources...")

        # Stop server
        self._stop_postgres_server()

        # Remove data directory
        if self.postgres_data_dir and self.postgres_data_dir.exists():
            try:
                shutil.rmtree(self.postgres_data_dir)
                self.logger.info(f"Removed PostgreSQL data directory: {self.postgres_data_dir}")
            except Exception as e:
                self.logger.warning(f"Error removing PostgreSQL data directory: {e}")


def test_postgresql_import(config: Dict, sql_file: str, temp_dir: str = None, logger: logging.Logger = None) -> Dict:
    """
    Convenience function to test PostgreSQL import

    Args:
        config: Configuration dictionary
        sql_file: Path to SQL file to import
        temp_dir: Temporary directory for PostgreSQL files
        logger: Logger instance

    Returns:
        Dictionary with test results
    """
    if not temp_dir:
        temp_dir = tempfile.mkdtemp(prefix="postgres_test_")

    if not logger:
        logger = logging.getLogger(__name__)

    tester = PostgreSQLTester(config, temp_dir, logger)

    try:
        return tester.test_import(sql_file)
    finally:
        tester.cleanup()

def perform_postgresql_import(config: Dict, sql_file: str, temp_dir: str = None, logger: logging.Logger = None):
    """
    Unified PostgreSQL import logic for both test and production imports

    Args:
        config: Configuration dictionary
        sql_file: Path to SQL file to import
        is_test: If True, use local test instance; if False, use production config
        temp_dir: Temporary directory for test files
        logger: Logger instance

    Returns:
        Dictionary with import results
    """
    if not logger:
        logger = logging.getLogger(__name__)


    # Production import using similar logic to test import
    results = {
        'success': False,
        'setup_time': 0,
        'import_time': 0,
        'validation_results': {},
        'errors': []
    }

    try:
        import time
        start_time = time.time()

        # Get PostgreSQL configuration
        postgres_config = {
            'host': config.get('postgres_host', 'localhost'),
            'port': config.get('postgres_port', 5432),
            'database': config.get('postgres_database', 'postgres'),
            'username': config.get('postgres_username', 'postgres'),
            'password': config.get('postgres_password', '')
        }

        if not postgres_config['password']:
            error_msg = "PostgreSQL password not provided in configuration"
            logger.error(error_msg)
            results['errors'].append(error_msg)
            return results

        # Check if psql is available, download if needed
        try:
            postgres_version = config.get('postgres_version', '17.2')
            psql_cmd = get_postgresql_client_path(postgres_version, temp_dir, logger)
        except Exception as e:
            error_msg = f"Failed to get PostgreSQL client: {e}"
            logger.error(error_msg)
            logger.info("You can manually install PostgreSQL client tools:")
            logger.info("  - Ubuntu/Debian: sudo apt-get install postgresql-client")
            logger.info("  - CentOS/RHEL: sudo yum install postgresql")
            logger.info("  - macOS: brew install postgresql")
            logger.info("  - Windows: Download from https://www.postgresql.org/download/windows/")
            results['errors'].append(error_msg)
            return results

        setup_time = time.time() - start_time
        results['setup_time'] = setup_time

        # Import SQL file
        import_start = time.time()

        # Import using shared command execution function
        result = execute_postgresql_command(
            psql_cmd=psql_cmd,
            host=postgres_config['host'],
            port=postgres_config['port'],
            username=postgres_config['username'],
            password=postgres_config['password'],
            database=postgres_config['database'],
            sql_file=sql_file,
            additional_args=["--set", "ON_ERROR_STOP=on", "-v", "ON_ERROR_STOP=1"],
            logger=logger
        )

        import_time = time.time() - import_start
        results['import_time'] = import_time

        logger.debug(f"Import output: {result.stdout}")

        # Basic validation for production import
        validation_results = _validate_production_import(postgres_config, psql_cmd, logger)
        results['validation_results'] = validation_results

        results['success'] = True

    except subprocess.CalledProcessError as e:
        error_msg = f"Failed to import data into PostgreSQL: {e.stderr}"
        logger.error(error_msg)
        results['errors'].append(error_msg)
    except FileNotFoundError:
        error_msg = f"PostgreSQL client not found at: {psql_cmd}"
        logger.error(error_msg)
        results['errors'].append(error_msg)
    except Exception as e:
        error_msg = f"Unexpected error during PostgreSQL import: {e}"
        logger.error(error_msg)
        results['errors'].append(error_msg)

    return results

def _validate_production_import(postgres_config: Dict, psql_cmd: str, logger: logging.Logger):
    """Basic validation for production PostgreSQL import"""
    validation_results = {}

    try:
        # Simple validation queries
        validation_queries = [
            ("Database connection", "SELECT version();"),
            ("List tables", "SELECT schemaname, tablename FROM pg_tables WHERE schemaname = 'public';"),
        ]

        for query_name, query in validation_queries:
            try:
                result = execute_postgresql_command(
                    psql_cmd=psql_cmd,
                    host=postgres_config['host'],
                    port=postgres_config['port'],
                    username=postgres_config['username'],
                    password=postgres_config['password'],
                    database=postgres_config['database'],
                    command=query,
                    additional_args=["-t"],  # Tuples only (no headers)
                    logger=logger
                )

                validation_results[query_name] = result.stdout.strip()
                logger.debug(f"{query_name}: OK")

            except Exception as e:
                logger.warning(f"{query_name}: FAILED - {e}")
                validation_results[query_name] = f"ERROR: {e}"

    except Exception as e:
        logger.warning(f"Validation failed: {e}")
        validation_results["Validation"] = f"ERROR: {e}"

    return validation_results

