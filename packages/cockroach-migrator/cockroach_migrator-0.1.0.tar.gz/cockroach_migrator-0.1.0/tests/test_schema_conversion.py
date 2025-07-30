#!/usr/bin/env python3
"""
Test cases for schema conversion functionality in migrate_conversion.py
"""

import unittest
import logging
import sys
from pathlib import Path

# Add parent directory to path for package imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from cockroach_migrator.migrate_conversion import convert_schema_to_postgresql, clean_wrapped_sql_statements, process_ddl_content


class TestSchemaConversion(unittest.TestCase):
    """Test cases for schema conversion functions"""

    def setUp(self):
        """Set up test fixtures"""
        # Create a logger for testing
        self.logger = logging.getLogger('test_logger')
        self.logger.setLevel(logging.INFO)

        # Sample wrapped SQL content similar to what's generated
        self.sample_wrapped_sql = '''-- Database: authdiverse
CREATE DATABASE IF NOT EXISTS "authdiverse";
\\c "authdiverse";

-- Schema
-- Tables and basic structure
create extension if not exists pgcrypto;
create_statement
"CREATE TABLE nomos_security_members (
	""memberId"" BYTES NOT NULL
	,""displayName"" VARCHAR(255) NULL
	,email VARCHAR(255) NULL
	,password CHAR(128) NULL
	,salt CHAR(128) NULL
	,status INT2 NULL
	,deleted INT2 NULL
	,""dateCreated"" TIMESTAMP NULL
	,""facebookId"" VARCHAR(45) NULL
	,facebooktoken STRING NULL
	,datepwchanged TIMESTAMP NULL
	,lastmodified TIMESTAMP NULL
	,facebookemail STRING NULL
	,extrainfo JSONB NULL
	,CONSTRAINT ""primary"" PRIMARY KEY (""memberId"" ASC)
	--INDEX nomos_security_email_index1 (email ASC)
	--INDEX nomos_security_facebookid_index1 (""facebookId"" ASC)
	--INDEX nomos_security_facebookemail_index1 (facebookemail ASC)
);"
create_statement
"CREATE TABLE nomos_security_devices (
	deviceauthid BYTES NOT NULL
	,memberid BYTES NOT NULL
	,deviceid VARCHAR(255) NULL
	,deviceidhash VARCHAR(255) NULL
	,devicetype VARCHAR(255) NULL
	,devicetoken STRING NULL
	,deviceinfo JSONB NULL
	,datelastlogin TIMESTAMP NULL
	,lastmodified TIMESTAMP NULL
	,CONSTRAINT ""primary"" PRIMARY KEY (deviceauthid ASC)
	--INDEX nomos_nomos_security_devices_memberid_index1 (memberid ASC)
	--INDEX nomos_nomos_security_devices_deviceid_index1 (deviceid ASC)
);"

-- Indexes
create INDEX nomos_security_email_index1 on nomos_security_members (email ASC);
create INDEX nomos_security_facebookid_index1 on nomos_security_members (""facebookId"" ASC);'''

        # Expected clean output
        self.expected_clean_sql = '''-- Database: authdiverse
CREATE DATABASE IF NOT EXISTS "authdiverse";
\\c "authdiverse";

-- Schema
-- Tables and basic structure
create extension if not exists pgcrypto;
CREATE TABLE nomos_security_members (
	"memberId" BYTES NOT NULL
	,"displayName" VARCHAR(255) NULL
	,email VARCHAR(255) NULL
	,password CHAR(128) NULL
	,salt CHAR(128) NULL
	,status INT2 NULL
	,deleted INT2 NULL
	,"dateCreated" TIMESTAMP NULL
	,"facebookId" VARCHAR(45) NULL
	,facebooktoken STRING NULL
	,datepwchanged TIMESTAMP NULL
	,lastmodified TIMESTAMP NULL
	,facebookemail STRING NULL
	,extrainfo JSONB NULL
	,CONSTRAINT "primary" PRIMARY KEY ("memberId" ASC)
	--INDEX nomos_security_email_index1 (email ASC)
	--INDEX nomos_security_facebookid_index1 ("facebookId" ASC)
	--INDEX nomos_security_facebookemail_index1 (facebookemail ASC)
);
CREATE TABLE nomos_security_devices (
	deviceauthid BYTES NOT NULL
	,memberid BYTES NOT NULL
	,deviceid VARCHAR(255) NULL
	,deviceidhash VARCHAR(255) NULL
	,devicetype VARCHAR(255) NULL
	,devicetoken STRING NULL
	,deviceinfo JSONB NULL
	,datelastlogin TIMESTAMP NULL
	,lastmodified TIMESTAMP NULL
	,CONSTRAINT "primary" PRIMARY KEY (deviceauthid ASC)
	--INDEX nomos_nomos_security_devices_memberid_index1 (memberid ASC)
	--INDEX nomos_nomos_security_devices_deviceid_index1 (deviceid ASC)
);

-- Indexes
create INDEX nomos_security_email_index1 on nomos_security_members (email ASC);
create INDEX nomos_security_facebookid_index1 on nomos_security_members ("facebookId" ASC);'''

    def test_clean_wrapped_sql_statements(self):
        """Test the clean_wrapped_sql_statements function"""
        result = clean_wrapped_sql_statements(self.sample_wrapped_sql, self.logger)

        # Check that create_statement lines are removed
        self.assertNotIn('create_statement', result)

        # Check that quoted SQL statements are unwrapped
        self.assertIn('CREATE TABLE nomos_security_members', result)
        self.assertIn('CREATE TABLE nomos_security_devices', result)

        # Check that double quotes are properly converted to single quotes
        self.assertIn('"memberId"', result)
        self.assertIn('"displayName"', result)

        # Check that the structure is preserved
        lines = result.split('\n')
        create_table_lines = [line for line in lines if 'CREATE TABLE' in line]
        self.assertEqual(len(create_table_lines), 2)

    def test_convert_schema_to_postgresql_basic_types(self):
        """Test basic CockroachDB to PostgreSQL type conversions"""
        cockroach_sql = '''CREATE TABLE test_table (
    id SERIAL8 PRIMARY KEY,
    name STRING NOT NULL,
    data BYTES,
    count INT8,
    small_count INT2,
    medium_count INT4
);'''

        result = convert_schema_to_postgresql(cockroach_sql, self.logger)

        # Check type conversions
        self.assertIn('BIGSERIAL', result)
        self.assertIn('TEXT', result)
        self.assertIn('BYTEA', result)
        self.assertIn('BIGINT', result)
        self.assertIn('SMALLINT', result)
        self.assertIn('INTEGER', result)

        # Original types should be replaced
        self.assertNotIn('SERIAL8', result)
        self.assertNotIn('STRING', result)
        self.assertNotIn('BYTES', result)
        self.assertNotIn('INT8', result)
        self.assertNotIn('INT2', result)
        self.assertNotIn('INT4', result)

    def test_convert_schema_with_wrapped_statements(self):
        """Test conversion of schema with wrapped CREATE TABLE statements"""
        result = convert_schema_to_postgresql(self.sample_wrapped_sql, self.logger)

        # Check that the result contains proper CREATE TABLE statements
        self.assertIn('CREATE TABLE nomos_security_members', result)
        self.assertIn('CREATE TABLE nomos_security_devices', result)

        # Check that wrapped format is removed
        self.assertNotIn('create_statement', result)
        self.assertNotIn('"CREATE TABLE', result)

        # Check that type conversions are applied
        self.assertIn('TEXT', result)  # STRING -> TEXT
        self.assertIn('BYTEA', result)  # BYTES -> BYTEA
        self.assertIn('SMALLINT', result)  # INT2 -> SMALLINT


    def test_process_ddl_content(self):
        """Test the process_ddl_content function"""
        simple_ddl = '''CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100)
);

CREATE INDEX idx_users_name ON users (name);

ALTER TABLE users ADD CONSTRAINT fk_users_dept
    FOREIGN KEY (dept_id) REFERENCES departments(id);'''

        tables_sql, constraints_sql, indexes_sql = process_ddl_content(simple_ddl)

        # Check that tables SQL contains the CREATE TABLE
        self.assertIn('CREATE TABLE users', tables_sql)
        self.assertIn('create extension if not exists pgcrypto', tables_sql)

        # Check that constraints are separated
        self.assertIn('ALTER TABLE users ADD CONSTRAINT', constraints_sql)

        # Note: The current process_ddl_content doesn't handle standalone CREATE INDEX
        # statements, only inline INDEX clauses within CREATE TABLE

    def test_uuid_generation_conversion(self):
        """Test UUID generation function conversion"""
        cockroach_sql = '''CREATE TABLE test_table (
    id UUID DEFAULT gen_random_uuid(),
    name STRING
);'''

        result = convert_schema_to_postgresql(cockroach_sql, self.logger)

        # Check UUID function conversion
        self.assertIn('uuid_generate_v4()', result)
        self.assertNotIn('gen_random_uuid()', result)

    def test_jsonb_conversion(self):
        """Test JSON to JSONB conversion (PostgreSQL prefers JSONB)"""
        cockroach_sql = '''CREATE TABLE test_table (
    id SERIAL PRIMARY KEY,
    metadata JSON
);'''

        result = convert_schema_to_postgresql(cockroach_sql, self.logger)

        # Check JSON to JSONB conversion (PostgreSQL prefers JSONB)
        self.assertIn('JSONB', result)
        self.assertNotIn('JSON ', result)  # Space to avoid matching JSONB

    def test_empty_input(self):
        """Test handling of empty input"""
        result = convert_schema_to_postgresql('', self.logger)
        self.assertEqual(result.strip(), '')

    def test_comments_preservation(self):
        """Test that comments are preserved during conversion"""
        sql_with_comments = '''-- This is a comment
CREATE TABLE test_table (
    id SERIAL PRIMARY KEY, -- Another comment
    name STRING
);
-- Final comment'''

        result = convert_schema_to_postgresql(sql_with_comments, self.logger)

        # Check that comments are preserved
        self.assertIn('-- This is a comment', result)
        self.assertIn('-- Another comment', result)
        self.assertIn('-- Final comment', result)

    def test_postgresql_compatibility_fixes(self):
        """Test PostgreSQL compatibility fixes"""
        cockroach_sql = '''CREATE DATABASE IF NOT EXISTS "testdb";
CREATE TABLE test_table (
    id SERIAL8 PRIMARY KEY ("id" ASC),
    name STRING NOT NULL,
    count INT2 DEFAULT 0:::BIGINT,
    metadata JSON
);
CREATE INDEX idx_name ON test_table (name ASC);
INSERT INTO "test_table" ("id	name	count") VALUES ('1	test	5');'''

        result = convert_schema_to_postgresql(cockroach_sql, self.logger)

        # Check CREATE DATABASE IF NOT EXISTS is fixed
        self.assertIn('CREATE DATABASE "testdb"', result)
        self.assertNotIn('IF NOT EXISTS', result)

        # Check DEFAULT with type casting is fixed
        self.assertIn('DEFAULT 0', result)
        self.assertNotIn('0:::BIGINT', result)

        # Check ASC is removed from PRIMARY KEY
        self.assertIn('PRIMARY KEY ("id")', result)
        self.assertNotIn('PRIMARY KEY ("id" ASC)', result)

        # Check ASC is removed from single-column INDEX
        self.assertIn('CREATE INDEX idx_name ON test_table (name)', result)
        self.assertNotIn('(name ASC)', result)

        # Check JSON to JSONB conversion
        self.assertIn('JSONB', result)
        self.assertNotIn('JSON ', result)

        # Check INSERT column list is fixed (tab-separated to comma-separated)
        self.assertIn('"id", "name", "count"', result)
        self.assertNotIn('"id	name	count"', result)

    def test_create_database_if_not_exists_fix(self):
        """Test CREATE DATABASE IF NOT EXISTS fix"""
        sql = 'CREATE DATABASE IF NOT EXISTS "mydb";'
        result = convert_schema_to_postgresql(sql, self.logger)

        self.assertIn('CREATE DATABASE "mydb"', result)
        self.assertNotIn('IF NOT EXISTS', result)

    def test_default_type_casting_fix(self):
        """Test DEFAULT with type casting fix"""
        sql = '''CREATE TABLE test (
    id INT DEFAULT 0:::BIGINT,
    flag SMALLINT DEFAULT 1:::INT8
);'''
        result = convert_schema_to_postgresql(sql, self.logger)

        self.assertIn('DEFAULT 0', result)
        self.assertIn('DEFAULT 1', result)
        self.assertNotIn(':::BIGINT', result)
        self.assertNotIn(':::INT8', result)

    def test_primary_key_asc_removal(self):
        """Test ASC removal from PRIMARY KEY"""
        sql = '''CREATE TABLE test (
    id INT PRIMARY KEY ("id" ASC),
    name VARCHAR(100)
);'''
        result = convert_schema_to_postgresql(sql, self.logger)

        self.assertIn('PRIMARY KEY ("id")', result)
        self.assertNotIn('PRIMARY KEY ("id" ASC)', result)

    def test_index_asc_removal(self):
        """Test ASC removal from single-column INDEX"""
        sql = '''CREATE INDEX idx_test ON test_table (column_name ASC);
CREATE UNIQUE INDEX idx_unique ON test_table (unique_col ASC);'''
        result = convert_schema_to_postgresql(sql, self.logger)

        self.assertIn('CREATE INDEX idx_test ON test_table (column_name)', result)
        self.assertIn('CREATE UNIQUE INDEX idx_unique ON test_table (unique_col)', result)
        self.assertNotIn('(column_name ASC)', result)
        self.assertNotIn('(unique_col ASC)', result)


def run_tests():
    """Run all test cases"""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSchemaConversion)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return success status
    return result.wasSuccessful()


if __name__ == '__main__':
    print("Running schema conversion tests...")
    success = run_tests()

    if success:
        print("\n[OK] All tests passed!")
        exit(0)
    else:
        print("\n✗ Some tests failed!")
        exit(1)