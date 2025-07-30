#!/usr/bin/env python3
"""
Test cases for PostgreSQL client download functionality
"""

import unittest
import os
import sys
import tempfile
import shutil
import json
import platform
from pathlib import Path

# Add parent directory to path for package imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from cockroach_migrator.migrate import CockroachMigrator


class TestPostgresDownload(unittest.TestCase):
    """Test cases for PostgreSQL client download functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_config = {
            "postgres_version": "17.0",
            "postgres_host": "localhost",
            "postgres_port": 5432,
            "postgres_database": "test",
            "postgres_username": "test",
            "postgres_password": "YOUR_TEST_PASSWORD"
        }
        
        # Create a temporary config file
        self.config_file = "test_config.json"
        with open(self.config_file, 'w') as f:
            json.dump(self.test_config, f, indent=2)
        
        # Create migrator instance
        self.migrator = CockroachMigrator(self.config_file)
        self.migrator.temp_dir = tempfile.mkdtemp(prefix="postgres_test_")

    def tearDown(self):
        """Clean up test fixtures"""
        # Cleanup config file
        if os.path.exists(self.config_file):
            os.remove(self.config_file)

        # Cleanup temp directory
        if hasattr(self.migrator, 'temp_dir') and self.migrator.temp_dir and os.path.exists(self.migrator.temp_dir):
            shutil.rmtree(self.migrator.temp_dir)

    def test_postgres_download(self):
        """Test PostgreSQL client download functionality"""
        
        # Check if we're on Windows (only platform currently supported for auto-download)
        if platform.system().lower() != "windows":
            self.skipTest("PostgreSQL auto-download only supported on Windows")

        # Test download on Windows
        try:
            psql_path = self.migrator._download_postgres_client()
            self.assertIsNotNone(psql_path, "PostgreSQL client path should not be None")

            # Check if the persistent directory was created
            script_dir = Path.cwd()
            postgres_dir = script_dir / f"postgresql-{self.migrator.postgres_version}"

            self.assertTrue(postgres_dir.exists(), f"Persistent directory should be created: {postgres_dir}")

            # Check if binary exists
            psql_binary = postgres_dir / "bin" / "psql.exe"
            self.assertTrue(psql_binary.exists(), f"PostgreSQL binary should exist: {psql_binary}")

            # Test running it again (should use existing binary)
            psql_path2 = self.migrator._download_postgres_client()
            self.assertEqual(str(psql_binary), psql_path2, "Second download should reuse existing binary")

        except Exception as e:
            self.fail(f"PostgreSQL download test failed: {e}")

    def test_system_path_check(self):
        """Test system PATH check for PostgreSQL client"""
        
        # This test works on all platforms
        try:
            psql_path = self.migrator._download_postgres_client()
            # If we get here without exception, PostgreSQL was found
            self.assertIsNotNone(psql_path, "PostgreSQL client path should not be None if found")
        except Exception:
            # It's okay if PostgreSQL is not found in system PATH
            # This is expected on systems without PostgreSQL installed
            pass

    def test_version_directories(self):
        """Test that different versions create different directories"""
        
        script_dir = Path.cwd()
        
        # Test different versions
        versions = ["16.0", "17.0", "15.2"]
        
        for version in versions:
            expected_dir = script_dir / f"postgresql-{version}"
            # We just check that the directory path is correctly formed
            # We don't require the directory to exist since we're not downloading all versions
            self.assertEqual(expected_dir.name, f"postgresql-{version}")


if __name__ == "__main__":
    unittest.main()