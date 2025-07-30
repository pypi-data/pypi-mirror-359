
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

from . import migrate_conversion

def download_cockroach_binary(os_name, arch, temp_dir, cockroach_version, logger) -> str:
    """Download CockroachDB binary if not present"""

    # Create persistent directory for CockroachDB binaries based on version
    # Use the current working directory (script location) instead of temp directory
    script_dir = Path.cwd()
    cockroach_dir = script_dir / f"cockroach-{cockroach_version}"
    cockroach_dir.mkdir(exist_ok=True)

    # Check if binary already exists in the persistent directory
    binary_name = 'cockroach.exe' if os_name == 'windows' else 'cockroach'
    local_binary = cockroach_dir / binary_name

    if local_binary.exists():
        logger.info(f"CockroachDB binary already exists: {local_binary}")
        return str(local_binary)

    logger.info(f"CockroachDB binary not found, downloading to: {cockroach_dir}")

    # Construct download URL
    if os_name == 'windows':
        archive_name = f"cockroach-{cockroach_version}.windows-6.2-amd64.zip"
    else:
        archive_name = f"cockroach-{cockroach_version}.{os_name}-{arch}.tgz"

    download_url = f"https://binaries.cockroachdb.com/{archive_name}"

    logger.info(f"Downloading CockroachDB binary from {download_url}")

    try:
        # Download archive to temporary location for extraction
        archive_path = Path(temp_dir) / archive_name
        urllib.request.urlretrieve(download_url, archive_path)

        # Extract binary
        if os_name == 'windows':
            import zipfile
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
                # Find the binary in extracted folder
                extracted_dir = Path(temp_dir) / f"cockroach-{cockroach_version}.windows-6.2-amd64"
                binary_source = extracted_dir / "cockroach.exe"
        else:
            import tarfile
            with tarfile.open(archive_path, 'r:gz') as tar_ref:
                tar_ref.extractall(temp_dir)
                # Find the binary in extracted folder
                extracted_dir = Path(temp_dir) / f"cockroach-{cockroach_version}.{os_name}-{arch}"
                binary_source = extracted_dir / "cockroach"

        # Move binary to persistent directory
        shutil.move(str(binary_source), str(local_binary))

        # Make executable on Unix systems
        if os_name != 'windows':
            os.chmod(local_binary, 0o755)

        # Clean up temporary extraction files (but keep the binary in persistent location)
        os.remove(archive_path)
        shutil.rmtree(extracted_dir)

        logger.info(f"CockroachDB binary downloaded and extracted: {local_binary}")
        return str(local_binary)

    except Exception as e:
        logger.error(f"Failed to download CockroachDB binary: {e}")
        sys.exit(1)

def start_temp_cockroach(temp_dir, cockroach_binary, cockroach_port, cockroach_http_port, insecure_mode, certs_dir, logger) -> subprocess.Popen:
    """Start a temporary CockroachDB instance"""
    logger.info("Starting temporary CockroachDB instance")

    # Create temporary data directory
    data_dir = Path(temp_dir) / "cockroach-data"
    data_dir.mkdir(exist_ok=True)

    # Start CockroachDB in single-node mode
    cmd = [
        cockroach_binary,
        "start-single-node",
        "--store", str(data_dir),
        "--listen-addr", f"localhost:{cockroach_port}",
        "--http-addr", f"localhost:{cockroach_http_port}"
    ]

    # Add security options based on mode
    if insecure_mode:
        logger.warning("Starting CockroachDB in INSECURE mode")
        cmd.append("--insecure")
    else:
        cmd.extend(["--certs-dir", str(certs_dir)])

    try:
        # Start process without --background to maintain control
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Wait for startup and check if it's ready
        logger.info("Waiting for CockroachDB to start...")
        max_retries = 30
        for i in range(max_retries):
            time.sleep(2)

            # Check if process died
            if process.poll() is not None:
                stdout, stderr = process.communicate()
                logger.error(f"CockroachDB failed to start: {stderr}")
                raise Exception(f"CockroachDB process died: {stderr}")

            # Try to connect to check if it's ready
            try:
                test_cmd = [
                    cockroach_binary,
                    "sql",
                    "--host", f"localhost:{cockroach_port}",
                    "--execute", "SELECT 1;"
                ]

                # Add security options
                if insecure_mode:
                    test_cmd.append("--insecure")
                else:
                    test_cmd.extend(["--certs-dir", str(certs_dir)])

                test_result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=5)

                if test_result.returncode == 0:
                    logger.info(f"CockroachDB started successfully on port {cockroach_port}")

                    # Initialize the cluster if needed (for single-node mode)
                    try:
                        init_cmd = [
                            cockroach_binary,
                            "init",
                            "--host", f"localhost:{cockroach_port}"
                        ]

                        # Add security options for init
                        if insecure_mode:
                            init_cmd.append("--insecure")
                        else:
                            init_cmd.extend(["--certs-dir", str(certs_dir)])

                        init_result = subprocess.run(init_cmd, capture_output=True, text=True, timeout=10)
                        if init_result.returncode == 0:
                            logger.info("CockroachDB cluster initialized successfully")
                        else:
                            # Cluster might already be initialized, which is fine
                            logger.debug(f"Cluster init result: {init_result.stderr}")

                    except Exception as e:
                        logger.warning(f"Cluster initialization warning (may already be initialized): {e}")

                    return process

            except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
                # Still starting up, continue waiting
                pass

        # If we get here, startup failed
        process.terminate()
        raise Exception("CockroachDB failed to start within timeout period")

    except Exception as e:
        logger.error(f"Failed to start CockroachDB: {e}")
        raise

def execute_cockroach_sql(cockroach_binary, cockroach_port, insecure_mode, certs_dir, sql_command: str, logger) -> str:
    """Execute SQL command in CockroachDB"""
    cmd = [
        cockroach_binary,
        "sql",
        "--host", f"localhost:{cockroach_port}",
        "--execute", sql_command
    ]

    # Add security options
    if insecure_mode:
        cmd.append("--insecure")
    else:
        cmd.extend(["--certs-dir", str(certs_dir)])

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"SQL command failed: {e.stderr}")
        raise

def get_table_row_count(cockroach_binary, cockroach_port, insecure_mode, certs_dir, db_name: str, table_name: str, logger) -> int:
    """Get approximate row count for table to determine processing strategy"""
    try:
        count_sql = f"SELECT COUNT(*) FROM {db_name}.\"{table_name}\""
        result = execute_cockroach_sql(
            cockroach_binary, cockroach_port,
            insecure_mode, certs_dir, count_sql, logger
        )
        # Parse the result to get the count
        lines = result.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line and line.isdigit():
                return int(line)
        # Fallback: try to find a number in the result
        numbers = re.findall(r'\d+', result)
        if numbers:
            return int(numbers[0])
        return 0
    except Exception as e:
        logger.warning(f"Could not get row count for {db_name}.{table_name}: {e}")
        return 0

def export_table_chunked(cockroach_binary, cockroach_port, insecure_mode, certs_dir, db_name: str, table_name: str, output_file, column_definitions: dict, chunk_size: int, logger):
    """Export table data in chunks to handle large tables efficiently"""

    # First, get the total row count to calculate expected chunks
    total_rows = get_table_row_count(cockroach_binary, cockroach_port, insecure_mode, certs_dir, db_name, table_name, logger)
    expected_chunks = (total_rows + chunk_size - 1) // chunk_size if total_rows > 0 else 1  # Ceiling division

    logger.info(f"Using chunked processing for table: {db_name}.{table_name} ({total_rows:,} rows, {expected_chunks} chunks of {chunk_size:,})")

    offset = 0
    total_rows_processed = 0
    chunk_num = 1

    while True:
        try:
            # Query with LIMIT and OFFSET for pagination
            select_sql = f"SELECT * FROM {db_name}.\"{table_name}\" LIMIT {chunk_size} OFFSET {offset}"
            logger.debug(f"Chunk {chunk_num}: {select_sql}")

            select_result = execute_cockroach_sql(
                cockroach_binary, cockroach_port,
                insecure_mode, certs_dir, select_sql, logger
            )

            # Count rows in this chunk by counting data lines
            chunk_rows = count_data_rows(select_result)

            if chunk_rows == 0:
                # No more data
                break

            # Convert chunk to INSERT statements
            migrate_conversion.convert_select_to_inserts(
                select_result, table_name, output_file, logger, column_definitions
            )

            total_rows_processed += chunk_rows
            logger.info(f"Processed chunk {chunk_num}/{expected_chunks} for {db_name}.{table_name}: {chunk_rows:,} rows (total: {total_rows_processed:,})")

            # If we got fewer rows than chunk_size, we're done
            if chunk_rows < chunk_size:
                break

            offset += chunk_size
            chunk_num += 1

        except Exception as e:
            logger.error(f"Failed to process chunk {chunk_num} for table {table_name}: {e}")
            raise

    logger.info(f"Completed chunked export for {db_name}.{table_name}: {total_rows_processed:,} total rows in {chunk_num} chunks")
    return total_rows_processed

def count_data_rows(select_result: str) -> int:
    """Count the number of data rows in a SELECT result"""
    lines = select_result.split('\n')
    data_row_count = 0
    headers_found = False

    for line in lines:
        line = line.strip()
        # Skip empty lines, separators, and row count lines
        if not line or line.startswith('-') or line.startswith('(') and 'row' in line:
            continue

        if not headers_found:
            # First non-empty line should be headers
            headers_found = True
            continue

        # This is a data row
        data_row_count += 1

    return data_row_count

def export_table_full(cockroach_binary, cockroach_port, insecure_mode, certs_dir, db_name: str, table_name: str, output_file, column_definitions: dict, logger):
    """Export entire table at once (for smaller tables)"""
    logger.debug(f"Using full export for table: {db_name}.{table_name}")

    select_sql = f"SELECT * FROM {db_name}.\"{table_name}\""
    select_result = execute_cockroach_sql(
        cockroach_binary, cockroach_port,
        insecure_mode, certs_dir, select_sql, logger
    )

    migrate_conversion.convert_select_to_inserts(
        select_result, table_name, output_file, logger, column_definitions
    )

    return count_data_rows(select_result)


def parse_column_definitions(columns_result: str, db_name: str, table_name: str, logger) -> dict:
    """Parse SHOW COLUMNS output to extract column definitions with length constraints"""
    column_definitions = {}
    lines = columns_result.split('\n')

    for line in lines:
        line = line.strip()

        # Skip empty lines, headers, and separators
        if (not line or
            line.startswith('-') or
            line.startswith('column_name') or
            line.startswith('(') and 'row' in line):
            continue

        # Parse column data - CockroachDB uses TAB separation
        if '\t' in line:
            parts = [p.strip() for p in line.split('\t')]
            if len(parts) >= 2:  # Need at least column_name and data_type
                column_name = parts[0]
                data_type = parts[1]

                # Extract length constraints from data types
                length_constraint = extract_length_constraint(data_type)

                column_definitions[column_name] = {
                    'data_type': data_type,
                    'length_constraint': length_constraint
                }

                logger.debug(f"Column {db_name}.{table_name}.{column_name}: {data_type} (max_length: {length_constraint})")

    return column_definitions

def extract_length_constraint(data_type: str) -> int:
    """Extract length constraint from data type definition"""

    # Handle CHAR(n), VARCHAR(n), TEXT(n) patterns
    length_match = re.search(r'\b(?:CHAR|VARCHAR|TEXT)\s*\(\s*(\d+)\s*\)', data_type, re.IGNORECASE)
    if length_match:
        return int(length_match.group(1))

    # Handle STRING(n) - CockroachDB specific
    string_match = re.search(r'\bSTRING\s*\(\s*(\d+)\s*\)', data_type, re.IGNORECASE)
    if string_match:
        return int(string_match.group(1))

    # No length constraint found
    return None