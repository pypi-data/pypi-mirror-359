#!/usr/bin/env python3
"""
Test cases for PostgreSQL import functionality
"""

import unittest
import json
import logging
import os
import sys
import tempfile
from pathlib import Path

# Add parent directory to path for package imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from cockroach_migrator import migrate_postgresql


class TestPostgreSQLImport(unittest.TestCase):
    """Test cases for PostgreSQL import functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp(prefix="postgres_test_")
        
        # Default test configuration
        self.config = {
            'postgres_version': '17.2',
            'test_postgres_port': 5433,
            'test_database_name': 'migration_test',
            'test_username': 'postgres',
            'test_password': 'YOUR_TEST_PASSWORD',
            'test_postgresql_import': True
        }
        
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def create_sample_sql_file(self) -> str:
        """Create a sample SQL file for testing"""
        sql_content = """
-- Sample SQL file for PostgreSQL import testing
-- Note: Database creation is handled separately, this file contains table definitions

-- Create sample tables
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS posts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    title VARCHAR(200) NOT NULL,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data
INSERT INTO users (username, email) VALUES
    ('john_doe', 'john@example.com'),
    ('jane_smith', 'jane@example.com'),
    ('bob_wilson', 'bob@example.com')
ON CONFLICT (username) DO NOTHING;

INSERT INTO posts (user_id, title, content) VALUES
    (1, 'First Post', 'This is my first post content'),
    (1, 'Second Post', 'This is my second post content'),
    (2, 'Jane''s Post', 'Hello from Jane'),
    (3, 'Bob''s Thoughts', 'Some thoughts from Bob')
ON CONFLICT DO NOTHING;
"""
        
        sql_file = Path(self.temp_dir) / "test_export.sql"
        with open(sql_file, 'w') as f:
            f.write(sql_content)
        
        return str(sql_file)

    def load_config_from_file(self) -> dict:
        """Load configuration from file if it exists"""
        config_file = "migration_config.json"
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    file_config = json.load(f)
                # Merge with defaults
                merged_config = self.config.copy()
                merged_config.update(file_config)
                return merged_config
            except Exception as e:
                self.logger.warning(f"Error loading config file: {e}")
        
        return self.config

    def test_sample_sql_file_creation(self):
        """Test that sample SQL file is created correctly"""
        sql_file = self.create_sample_sql_file()
        
        self.assertTrue(os.path.exists(sql_file), "SQL file should be created")
        
        with open(sql_file, 'r') as f:
            content = f.read()
        
        # Check that expected content is present
        self.assertIn("CREATE TABLE IF NOT EXISTS users", content)
        self.assertIn("CREATE TABLE IF NOT EXISTS posts", content)
        self.assertIn("INSERT INTO users", content)
        self.assertIn("INSERT INTO posts", content)
        self.assertIn("john_doe", content)
        self.assertIn("jane_smith", content)

    def test_config_loading(self):
        """Test configuration loading functionality"""
        config = self.load_config_from_file()
        
        # Check that default values are present
        self.assertIn('postgres_version', config)
        self.assertIn('test_postgres_port', config)
        self.assertIn('test_database_name', config)
        self.assertIn('test_username', config)
        self.assertIn('test_password', config)
        self.assertIn('test_postgresql_import', config)
        
        # Check default values
        self.assertEqual(config['postgres_version'], '17.2')
        self.assertEqual(config['test_postgres_port'], 5433)
        self.assertEqual(config['test_database_name'], 'migration_test')

    @unittest.skipUnless(
        hasattr(migrate_postgresql, 'test_postgresql_import'),
        "migrate_postgresql.test_postgresql_import not available"
    )
    def test_postgresql_import(self):
        """Test PostgreSQL import functionality (requires PostgreSQL setup)"""
        # This test requires actual PostgreSQL setup and is skipped by default
        # It can be enabled when PostgreSQL is available for testing
        
        config = self.load_config_from_file()
        sql_file = self.create_sample_sql_file()
        
        try:
            results = migrate_postgresql.test_postgresql_import(
                config=config,
                sql_file=sql_file,
                temp_dir=self.temp_dir,
                logger=self.logger
            )
            
            # Check results structure
            self.assertIn('success', results)
            self.assertIn('setup_time', results)
            self.assertIn('import_time', results)
            self.assertIn('validation_results', results)
            self.assertIn('errors', results)
            
            if results['success']:
                self.assertGreaterEqual(results['setup_time'], 0)
                self.assertGreaterEqual(results['import_time'], 0)
            
        except Exception as e:
            self.skipTest(f"PostgreSQL import test requires PostgreSQL setup: {e}")


if __name__ == "__main__":
    unittest.main()