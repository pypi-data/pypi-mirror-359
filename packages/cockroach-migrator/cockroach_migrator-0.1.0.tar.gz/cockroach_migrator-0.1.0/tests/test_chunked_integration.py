#!/usr/bin/env python3
"""
Integration test cases for chunked export functionality with actual CockroachDB
"""

import unittest
import sys
import os
import tempfile
import shutil
import subprocess
import platform
import logging
from pathlib import Path

# Add parent directory to path for package imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from cockroach_migrator import migrate_cockroach


class TestChunkedExportIntegration(unittest.TestCase):
    """Integration test cases for chunked export with real CockroachDB"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = None
        self.cockroach_binary = None
        self.cockroach_process = None
        self.cockroach_port = 26258  # Use different port to avoid conflicts
        self.cockroach_http_port = 8081
        self.test_db = "chunked_test_db"
        self.test_table = "large_test_table"
        
        # Set up logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        # Set up test environment
        self._setup_environment()
        
    def tearDown(self):
        """Clean up test environment"""
        self._cleanup()
        
    def _setup_environment(self):
        """Set up test environment"""
        self.logger.info("Setting up integration test environment...")
        
        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp(prefix="chunked_test_")
        self.logger.info(f"Created temp directory: {self.temp_dir}")
        
        # Download CockroachDB binary if needed
        try:
            system = platform.system().lower()
            machine = platform.machine().lower()
            
            if system == 'linux':
                if machine in ['x86_64', 'amd64']:
                    os_name, arch = 'linux', 'amd64'
                elif machine in ['aarch64', 'arm64']:
                    os_name, arch = 'linux', 'arm64'
                else:
                    raise Exception(f"Unsupported Linux architecture: {machine}")
            elif system == 'darwin':
                if machine in ['x86_64', 'amd64']:
                    os_name, arch = 'darwin', 'amd64'
                elif machine in ['arm64']:
                    os_name, arch = 'darwin', 'arm64'
                else:
                    raise Exception(f"Unsupported macOS architecture: {machine}")
            elif system == 'windows':
                os_name, arch = 'windows', 'amd64'
            else:
                raise Exception(f"Unsupported platform: {system}")
            
            self.cockroach_binary = migrate_cockroach.download_cockroach_binary(
                os_name, arch, self.temp_dir, "v24.3.5", self.logger
            )
            self.logger.info(f"CockroachDB binary ready: {self.cockroach_binary}")
            
        except Exception as e:
            self.logger.error(f"Failed to setup CockroachDB binary: {e}")
            self.skipTest(f"CockroachDB setup failed: {e}")
    
    def _start_cockroach(self):
        """Start temporary CockroachDB instance"""
        self.logger.info("Starting temporary CockroachDB instance...")
        
        try:
            self.cockroach_process = migrate_cockroach.start_temp_cockroach(
                self.temp_dir, self.cockroach_binary, self.cockroach_port, 
                self.cockroach_http_port, True, None, self.logger  # insecure mode
            )
            self.logger.info("CockroachDB started successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to start CockroachDB: {e}")
            raise
    
    def _create_test_data(self):
        """Create test database and populate with test data"""
        self.logger.info("Creating test database and data...")
        
        try:
            # Create database
            create_db_sql = f"CREATE DATABASE {self.test_db}"
            migrate_cockroach.execute_cockroach_sql(
                self.cockroach_binary, self.cockroach_port, True, None, create_db_sql, self.logger
            )
            self.logger.info(f"Created database: {self.test_db}")
            
            # Create table
            create_table_sql = f"""
            USE {self.test_db};
            CREATE TABLE {self.test_table} (
                id SERIAL PRIMARY KEY,
                name STRING(100),
                email STRING(255),
                data TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            )
            """
            migrate_cockroach.execute_cockroach_sql(
                self.cockroach_binary, self.cockroach_port, True, None, create_table_sql, self.logger
            )
            self.logger.info(f"Created table: {self.test_table}")
            
            # Insert test data in batches (simulate large dataset)
            # Use smaller batch size to avoid Windows command line length limits
            batch_size = 100  # Reduced from 1000 to avoid long SQL commands
            total_rows = 5500  # This will create 6 chunks with chunk_size=1000
            
            self.logger.info(f"Inserting {total_rows} test rows in batches of {batch_size}...")
            
            for batch_start in range(0, total_rows, batch_size):
                batch_end = min(batch_start + batch_size, total_rows)
                values = []
                
                for i in range(batch_start, batch_end):
                    name = f"User_{i:05d}"
                    email = f"user{i:05d}@example.com"
                    data = f"Data_{i}"  # Reduced data size to avoid long SQL commands
                    values.append(f"('{name}', '{email}', '{data}')")
                
                insert_sql = f"""
                USE {self.test_db};
                INSERT INTO {self.test_table} (name, email, data) VALUES {', '.join(values)}
                """
                
                migrate_cockroach.execute_cockroach_sql(
                    self.cockroach_binary, self.cockroach_port, True, None, insert_sql, self.logger
                )
                
                self.logger.info(f"Inserted batch {batch_start+1}-{batch_end} ({batch_end-batch_start} rows)")
            
            self.logger.info(f"Successfully created {total_rows} test rows")
            
        except Exception as e:
            self.logger.error(f"Failed to create test data: {e}")
            raise
    
    def _cleanup(self):
        """Clean up test environment"""
        self.logger.info("Cleaning up test environment...")
        
        # Stop CockroachDB process
        if self.cockroach_process:
            try:
                self.logger.info("Stopping CockroachDB process...")
                self.cockroach_process.terminate()
                try:
                    self.cockroach_process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    self.logger.warning("CockroachDB didn't stop gracefully, forcing kill")
                    self.cockroach_process.kill()
                    self.cockroach_process.wait()
                self.logger.info("CockroachDB process stopped")
            except Exception as e:
                self.logger.warning(f"Error stopping CockroachDB: {e}")
        
        # Remove temporary directory
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                self.logger.info(f"Removed temp directory: {self.temp_dir}")
            except Exception as e:
                self.logger.warning(f"Error removing temp directory: {e}")

    @unittest.skipUnless(
        hasattr(migrate_cockroach, 'download_cockroach_binary'),
        "migrate_cockroach module not available"
    )
    def test_chunked_export_integration(self):
        """Test the chunked export functionality with real CockroachDB"""
        try:
            self._start_cockroach()
            self._create_test_data()
            
            # Test row count function
            row_count = migrate_cockroach.get_table_row_count(
                self.cockroach_binary, self.cockroach_port, True, None,
                self.test_db, self.test_table, self.logger
            )
            self.logger.info(f"Table row count: {row_count}")
            self.assertEqual(row_count, 5500, f"Expected 5500 rows, got {row_count}")
            
            # Test chunked export with small chunk size to verify chunking
            chunk_size = 1000
            output_file_path = Path(self.temp_dir) / "chunked_export_test.sql"
            
            with open(output_file_path, 'w') as output_file:
                output_file.write(f"-- Test chunked export for {self.test_table}\n")
                
                total_exported = migrate_cockroach.export_table_chunked(
                    self.cockroach_binary, self.cockroach_port, True, None,
                    self.test_db, self.test_table, output_file, {}, chunk_size, self.logger
                )
            
            self.logger.info(f"Chunked export completed: {total_exported} rows exported")
            self.assertEqual(total_exported, 5500, f"Expected to export 5500 rows, got {total_exported}")
            
            # Verify the output file contains INSERT statements
            with open(output_file_path, 'r') as f:
                content = f.read()
                insert_count = content.count('INSERT INTO')
                self.logger.info(f"Generated {insert_count} INSERT statements")
                self.assertEqual(insert_count, 5500, f"Expected 5500 INSERT statements, got {insert_count}")
                
                # Check that we have the expected data
                self.assertIn('User_00000', content, "First user not found in export")
                self.assertIn('User_05499', content, "Last user not found in export")
                self.assertIn('user00000@example.com', content, "First email not found in export")
                self.assertIn('user05499@example.com', content, "Last email not found in export")
                self.assertIn('Data_0', content, "First data not found in export")
                self.assertIn('Data_5499', content, "Last data not found in export")
            
            self.logger.info("✓ Chunked export test passed!")
            
        except Exception as e:
            self.fail(f"Chunked export test failed: {e}")

    @unittest.skipUnless(
        hasattr(migrate_cockroach, 'download_cockroach_binary'),
        "migrate_cockroach module not available"
    )
    def test_small_table_export(self):
        """Test export of a small table (single chunk)"""
        try:
            self._start_cockroach()
            self._create_test_data()
            
            # Create a small table
            small_table = "small_test_table"
            create_small_table_sql = f"""
            USE {self.test_db};
            CREATE TABLE {small_table} (
                id SERIAL PRIMARY KEY,
                value STRING(50)
            );
            INSERT INTO {small_table} (value) VALUES 
                ('test1'), ('test2'), ('test3'), ('test4'), ('test5');
            """
            
            migrate_cockroach.execute_cockroach_sql(
                self.cockroach_binary, self.cockroach_port, True, None, create_small_table_sql, self.logger
            )
            
            # Export with large chunk size
            chunk_size = 1000
            output_file_path = Path(self.temp_dir) / "small_export_test.sql"
            
            with open(output_file_path, 'w') as output_file:
                total_exported = migrate_cockroach.export_table_chunked(
                    self.cockroach_binary, self.cockroach_port, True, None,
                    self.test_db, small_table, output_file, {}, chunk_size, self.logger
                )
            
            self.logger.info(f"Small table export completed: {total_exported} rows")
            self.assertEqual(total_exported, 5, f"Expected 5 rows, got {total_exported}")
            
            self.logger.info("✓ Small table export test passed!")
            
        except Exception as e:
            self.fail(f"Small table export test failed: {e}")


if __name__ == "__main__":
    unittest.main()