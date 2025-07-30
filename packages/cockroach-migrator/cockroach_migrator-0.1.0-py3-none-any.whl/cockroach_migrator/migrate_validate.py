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

def validate_schema_and_data(databases:dict, schema_file: str, data_file: str, temp_dir, logger):
    """Validate the exported schema and data before import"""
    logger.info("Starting schema and data validation...")

    validation_results = {
        'schema_validation': {},
        'data_validation': {},
        'warnings': [],
        'errors': []
    }

    # Validate schema file
    try:
        validation_results['schema_validation'] = validate_schema_file(schema_file, logger)
    except Exception as e:
        validation_results['errors'].append(f"Schema validation failed: {e}")
        logger.error(f"Schema validation failed: {e}")

    # Validate data file
    try:
        validation_results['data_validation'] = validate_data_file(data_file, logger)
    except Exception as e:
        validation_results['errors'].append(f"Data validation failed: {e}")
        logger.error(f"Data validation failed: {e}")

    # Cross-validation between schema and data
    try:
        cross_validation = cross_validate_schema_data(schema_file, data_file, logger)
        validation_results['cross_validation'] = cross_validation
    except Exception as e:
        validation_results['warnings'].append(f"Cross-validation warning: {e}")
        logger.warning(f"Cross-validation warning: {e}")

    # Generate validation report
    generate_validation_report(databases, validation_results, temp_dir, logger)

    return validation_results

def validate_schema_file(schema_file: str, logger) -> dict:
    """Validate the schema file for PostgreSQL compatibility"""
    logger.info("Validating schema file...")

    validation = {
        'file_size': 0,
        'total_lines': 0,
        'table_count': 0,
        'index_count': 0,
        'constraint_count': 0,
        'tables': [],
        'indexes': [],
        'constraints': [],
        'potential_issues': [],
        'postgresql_compatibility': []
    }

    if not os.path.exists(schema_file):
        raise FileNotFoundError(f"Schema file not found: {schema_file}")

    validation['file_size'] = os.path.getsize(schema_file)

    with open(schema_file, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')
        validation['total_lines'] = len(lines)

        # Parse SQL statements
        current_statement = ""
        statements_found = 0
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('--'):
                continue

            current_statement += " " + line

            if line.endswith(';'):
                stmt = current_statement.strip()
                statements_found += 1
                if statements_found <= 5:  # Debug first 5 statements
                    print(f"Processing statement {statements_found}: {stmt[:100]}...")
                analyze_sql_statement(stmt, validation, logger)
                current_statement = ""

        # Handle case where last statement doesn't end with semicolon
        if current_statement.strip():
            stmt = current_statement.strip()
            statements_found += 1
            print(f"Processing final statement: {stmt[:100]}...")
            analyze_sql_statement(stmt, validation, logger)

        print(f"Total SQL statements processed: {statements_found}")

    print(f"Schema validation complete: {validation['table_count']} tables, "
                f"{validation['index_count']} indexes, {validation['constraint_count']} constraints")

    return validation

def analyze_sql_statement(statement: str, validation: dict, logger):
    """Analyze individual SQL statement for validation"""
    stmt_upper = statement.upper()

    # Table creation
    if stmt_upper.startswith('CREATE TABLE'):
        validation['table_count'] += 1
        table_match = re.search(r'CREATE TABLE\s+(?:IF NOT EXISTS\s+)?["`]?(\w+)["`]?', statement, re.IGNORECASE)
        if table_match:
            table_name = table_match.group(1)
            validation['tables'].append(table_name)

            # Check for potential issues
            if 'SERIAL8' in stmt_upper:
                validation['potential_issues'].append(f"Table {table_name}: SERIAL8 should be BIGSERIAL in PostgreSQL")
            if 'STRING' in stmt_upper:
                validation['potential_issues'].append(f"Table {table_name}: STRING should be TEXT in PostgreSQL")
            if 'BYTES' in stmt_upper:
                validation['potential_issues'].append(f"Table {table_name}: BYTES should be BYTEA in PostgreSQL")

    # Index creation
    elif stmt_upper.startswith('CREATE INDEX') or stmt_upper.startswith('CREATE UNIQUE INDEX'):
        validation['index_count'] += 1
        index_match = re.search(r'CREATE\s+(?:UNIQUE\s+)?INDEX\s+(?:IF NOT EXISTS\s+)?["`]?(\w+)["`]?', statement, re.IGNORECASE)
        if index_match:
            index_name = index_match.group(1)
            validation['indexes'].append(index_name)

            # Check for CockroachDB-specific index features
            if 'STORING' in stmt_upper:
                validation['potential_issues'].append(f"Index {index_name}: STORING clause not supported in PostgreSQL")
            if 'HASH SHARDED' in stmt_upper:
                validation['potential_issues'].append(f"Index {index_name}: HASH SHARDED not supported in PostgreSQL")

    # Constraint creation
    elif 'CONSTRAINT' in stmt_upper and ('FOREIGN KEY' in stmt_upper or 'PRIMARY KEY' in stmt_upper or 'CHECK' in stmt_upper):
        validation['constraint_count'] += 1
        constraint_match = re.search(r'CONSTRAINT\s+["`]?(\w+)["`]?', statement, re.IGNORECASE)
        if constraint_match:
            constraint_name = constraint_match.group(1)
            validation['constraints'].append(constraint_name)

def validate_data_file(data_file: str, logger) -> dict:
    """Validate the data file for consistency and PostgreSQL compatibility"""
    logger.info("Validating data file...")

    validation = {
        'file_size': 0,
        'total_lines': 0,
        'insert_count': 0,
        'tables_with_data': [],
        'estimated_rows': 0,
        'potential_issues': [],
        'data_types_found': set()
    }

    if not os.path.exists(data_file):
        raise FileNotFoundError(f"Data file not found: {data_file}")

    validation['file_size'] = os.path.getsize(data_file)

    with open(data_file, 'r', encoding='utf-8') as f:
        current_table = None
        for line_num, line in enumerate(f, 1):
            validation['total_lines'] = line_num
            line = line.strip()

            if not line or line.startswith('--'):
                if line.startswith('-- Data for table:'):
                    table_match = re.search(r'-- Data for table:\s+(\w+)', line)
                    if table_match:
                        current_table = table_match.group(1)
                        if current_table not in validation['tables_with_data']:
                            validation['tables_with_data'].append(current_table)
                continue

            if line.upper().startswith('INSERT INTO'):
                validation['insert_count'] += 1
                validation['estimated_rows'] += 1

                # Check for potential data issues
                if "''" in line:  # Escaped quotes
                    validation['data_types_found'].add('text_with_quotes')
                if 'NULL' in line:
                    validation['data_types_found'].add('null_values')
                if re.search(r"'[0-9]{4}-[0-9]{2}-[0-9]{2}", line):  # Date patterns
                    validation['data_types_found'].add('dates')
                if re.search(r"'[0-9]+\.[0-9]+'", line):  # Decimal patterns
                    validation['data_types_found'].add('decimals')

    validation['data_types_found'] = list(validation['data_types_found'])

    logger.info(f"Data validation complete: {validation['insert_count']} INSERT statements, "
                f"{len(validation['tables_with_data'])} tables with data")

    return validation

def cross_validate_schema_data(schema_file: str, data_file: str, logger) -> dict:
    """Cross-validate schema and data consistency"""
    logger.info("Performing cross-validation between schema and data...")

    cross_validation = {
        'schema_tables': set(),
        'data_tables': set(),
        'tables_with_schema_only': [],
        'tables_with_data_only': [],
        'matching_tables': [],
        'consistency_score': 0.0
    }

    # Get tables from schema
    with open(schema_file, 'r', encoding='utf-8') as f:
        content = f.read()
        table_matches = re.findall(r'CREATE TABLE\s+(?:IF NOT EXISTS\s+)?["`]?(\w+)["`]?', content, re.IGNORECASE)
        cross_validation['schema_tables'] = set(table_matches)

    # Get tables from data
    with open(data_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('-- Data for table:'):
                table_match = re.search(r'-- Data for table:\s+(\w+)', line)
                if table_match:
                    cross_validation['data_tables'].add(table_match.group(1))

    # Compare tables
    cross_validation['tables_with_schema_only'] = list(
        cross_validation['schema_tables'] - cross_validation['data_tables']
    )
    cross_validation['tables_with_data_only'] = list(
        cross_validation['data_tables'] - cross_validation['schema_tables']
    )
    cross_validation['matching_tables'] = list(
        cross_validation['schema_tables'] & cross_validation['data_tables']
    )

    # Calculate consistency score
    total_tables = len(cross_validation['schema_tables'] | cross_validation['data_tables'])
    if total_tables > 0:
        cross_validation['consistency_score'] = len(cross_validation['matching_tables']) / total_tables

    return cross_validation

def write_database_tree_structure(f, validation_results: dict, databases:dict, logger):
    """Write database structure in tree format"""
    f.write("DATABASE STRUCTURE OVERVIEW\n")
    f.write("-" * 40 + "\n")

    # Extract database and table information from validation results consistently
    schema_tables = set()
    data_tables = set()

    # Get schema tables from schema validation
    if 'schema_validation' in validation_results:
        schema_val = validation_results['schema_validation']
        if schema_val.get('file_exists', False):
            schema_tables = set(schema_val.get('tables', []))

    # Get data tables from data validation
    if 'data_validation' in validation_results:
        data_val = validation_results['data_validation']
        if data_val.get('file_exists', False):
            data_tables = set(data_val.get('tables_with_data', []))

    # Use cross-validation results if available (they should be consistent)
    if 'cross_validation' in validation_results:
        cross_val = validation_results['cross_validation']
        # Only override if cross-validation has data
        if cross_val.get('schema_tables'):
            schema_tables = set(cross_val.get('schema_tables', set()))
        if cross_val.get('data_tables'):
            data_tables = set(cross_val.get('data_tables', set()))

    # Combine validation tables with actual database tables
    all_tables = schema_tables | data_tables

    # If we have actual database info, prioritize that over validation results
    if databases:
        actual_tables = set()
        for db_info in databases.values():
            actual_tables.update(db_info.get('tables', []))

        if actual_tables:
            # Use actual database tables as the source of truth
            all_tables = actual_tables
            # Update schema/data tables to only include tables that actually exist
            schema_tables = schema_tables & actual_tables
            data_tables = data_tables & actual_tables

    if not all_tables:
        f.write("No exportable tables found.\n")
        f.write("This indicates:\n")
        f.write("  - Databases exist but contain no tables in the 'public' schema\n")
        f.write("  - All tables are views, system tables, or in non-public schemas\n")
        f.write("  - Tables exist but don't meet export criteria (public schema, table type)\n")

        # Show what databases were found even if they have no exportable tables
        if databases:
            f.write(f"\nDatabases found: {list(databases.keys())}\n")
            f.write("Note: These databases exist but contain no exportable tables.\n")
        f.write("\n")
        return

    if databases and any(db_info.get('tables') for db_info in databases.values()):
        # Multi-database structure with actual table data
        for db_name, db_info in databases.items():
            db_tables = db_info.get('tables', [])
            if db_tables:  # Only show databases that have exportable tables
                f.write(f"{db_name}\n")

                # Group tables by schema if available
                schemas = db_info.get('schemas', {})
                if schemas:
                    for schema_name, schema_tables_list in schemas.items():
                        if schema_tables_list:  # Only show schemas with tables
                            f.write(f"-- {schema_name}\n")
                            for table in sorted(schema_tables_list):
                                status = get_table_status(table, schema_tables, data_tables, logger)
                                f.write(f"---- {table}{status}\n")
                else:
                    # No schema information, list tables directly under database
                    for table in sorted(db_tables):
                        status = get_table_status(table, schema_tables, data_tables, logger)
                        f.write(f"-- {table}{status}\n")
                f.write("\n")
    else:
        # Single database or no database info - use validation results
        f.write("lightvault (default database)\n")
        f.write("-- public (default schema)\n")
        for table in sorted(all_tables):
            status = get_table_status(table, schema_tables, data_tables, logger)
            f.write(f"---- {table}{status}\n")
        f.write("\n")

    # Summary - calculate statistics properly for multi-database scenarios
    if databases and any(db_info.get('tables') for db_info in databases.values()):
        # Multi-database: count total tables across all databases (including duplicates)
        total_tables = sum(len(db_info.get('tables', [])) for db_info in databases.values())

        # For schema/data statistics, we need to count per-database occurrences
        total_with_schema = 0
        total_with_data = 0
        total_with_both = 0
        total_schema_only = 0
        total_data_only = 0

        for db_info in databases.values():
            db_tables = set(db_info.get('tables', []))
            db_schema_tables = schema_tables & db_tables
            db_data_tables = data_tables & db_tables

            total_with_schema += len(db_schema_tables)
            total_with_data += len(db_data_tables)
            total_with_both += len(db_schema_tables & db_data_tables)
            total_schema_only += len(db_schema_tables - db_data_tables)
            total_data_only += len(db_data_tables - db_schema_tables)

        f.write(f"Total exportable tables: {total_tables}\n")
        f.write(f"  - With schema definitions: {total_with_schema}\n")
        f.write(f"  - With data: {total_with_data}\n")
        f.write(f"  - Schema + Data: {total_with_both}\n")
        f.write(f"  - Schema only: {total_schema_only}\n")
        f.write(f"  - Data only: {total_data_only}\n\n")
    else:
        # Single database: use original logic
        f.write(f"Total exportable tables: {len(all_tables)}\n")
        f.write(f"  - With schema definitions: {len(schema_tables)}\n")
        f.write(f"  - With data: {len(data_tables)}\n")
        f.write(f"  - Schema + Data: {len(schema_tables & data_tables)}\n")
        f.write(f"  - Schema only: {len(schema_tables - data_tables)}\n")
        f.write(f"  - Data only: {len(data_tables - schema_tables)}\n\n")

    # Legend
    f.write("Legend:\n")
    f.write("  (S) = Schema only (no data)\n")
    f.write("  (D) = Data only (no schema)\n")
    f.write("  (S+D) = Schema and data present\n")
    f.write("\n")

def get_table_status(table_name: str, schema_tables: set, data_tables: set, logger) -> str:
    """Get status indicator for a table"""
    has_schema = table_name in schema_tables
    has_data = table_name in data_tables

    if has_schema and has_data:
        return " (S+D)"
    elif has_schema:
        return " (S)"
    elif has_data:
        return " (D)"
    else:
        return ""

def generate_validation_report(databases:dict, validation_results: dict, temp_dir, logger):
    """Generate a comprehensive validation report"""
    report_file = os.path.join(temp_dir or ".", "validation_report.txt")

    logger.info(f"Generating validation report: {report_file}")

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("MIGRATION VALIDATION REPORT\n")
        f.write("=" * 80 + "\n\n")

        # Database Structure Overview
        write_database_tree_structure(f, validation_results, databases, logger)

        # Schema Validation Results
        if 'schema_validation' in validation_results:
            schema_val = validation_results['schema_validation']
            f.write("SCHEMA VALIDATION RESULTS\n")
            f.write("-" * 40 + "\n")
            f.write(f"Schema file exists: {'[OK]' if schema_val.get('file_exists') else '✗'}\n")
            f.write(f"Schema file size: {schema_val.get('file_size', 0):,} bytes\n")
            f.write(f"Tables found: {len(schema_val.get('tables', []))}\n")
            f.write(f"DDL statements: {schema_val.get('ddl_statements', 0)}\n")

            if schema_val.get('issues'):
                f.write(f"Issues found: {len(schema_val['issues'])}\n")
                for issue in schema_val['issues'][:5]:  # Show first 5 issues
                    f.write(f"  - {issue}\n")
                if len(schema_val['issues']) > 5:
                    f.write(f"  ... and {len(schema_val['issues']) - 5} more issues\n")
            else:
                f.write("Issues found: 0\n")
            f.write("\n")

        # Data Validation Results
        if 'data_validation' in validation_results:
            data_val = validation_results['data_validation']
            f.write("DATA VALIDATION RESULTS\n")
            f.write("-" * 40 + "\n")
            f.write(f"Data file exists: {'[OK]' if data_val.get('file_exists') else '✗'}\n")
            f.write(f"Data file size: {data_val.get('file_size', 0):,} bytes\n")
            f.write(f"Tables with data: {len(data_val.get('tables_with_data', []))}\n")
            f.write(f"Total records: {data_val.get('total_records', 0):,}\n")

            if data_val.get('issues'):
                f.write(f"Issues found: {len(data_val['issues'])}\n")
                for issue in data_val['issues'][:5]:  # Show first 5 issues
                    f.write(f"  - {issue}\n")
                if len(data_val['issues']) > 5:
                    f.write(f"  ... and {len(data_val['issues']) - 5} more issues\n")
            else:
                f.write("Issues found: 0\n")
            f.write("\n")

        # Cross Validation Results
        if 'cross_validation' in validation_results:
            cross_val = validation_results['cross_validation']
            f.write("CROSS VALIDATION RESULTS\n")
            f.write("-" * 40 + "\n")
            f.write(f"Schema tables: {len(cross_val.get('schema_tables', set()))}\n")
            f.write(f"Data tables: {len(cross_val.get('data_tables', set()))}\n")
            f.write(f"Matching tables: {len(cross_val.get('matching_tables', set()))}\n")
            f.write(f"Schema-only tables: {len(cross_val.get('schema_only_tables', set()))}\n")
            f.write(f"Data-only tables: {len(cross_val.get('data_only_tables', set()))}\n")
            f.write(f"Consistency score: {cross_val.get('consistency_score', 0):.2%}\n")

            if cross_val.get('schema_only_tables'):
                f.write(f"\nTables with schema but no data:\n")
                for table in sorted(cross_val['schema_only_tables']):
                    f.write(f"  - {table}\n")

            if cross_val.get('data_only_tables'):
                f.write(f"\nTables with data but no schema:\n")
                for table in sorted(cross_val['data_only_tables']):
                    f.write(f"  - {table}\n")
            f.write("\n")

        # Overall Assessment
        f.write("OVERALL ASSESSMENT\n")
        f.write("-" * 40 + "\n")

        total_issues = 0
        if 'schema_validation' in validation_results:
            total_issues += len(validation_results['schema_validation'].get('issues', []))
        if 'data_validation' in validation_results:
            total_issues += len(validation_results['data_validation'].get('issues', []))

        consistency_score = 0
        if 'cross_validation' in validation_results:
            consistency_score = validation_results['cross_validation'].get('consistency_score', 0)

        if total_issues == 0 and consistency_score > 0.9:
            f.write("Status: [OK] READY FOR MIGRATION\n")
            f.write("The validation passed with no critical issues.\n")
        elif total_issues < 5 and consistency_score > 0.7:
            f.write("Status: ⚠ MIGRATION WITH CAUTION\n")
            f.write("Some issues were found but migration may proceed.\n")
        else:
            f.write("Status: ✗ MIGRATION NOT RECOMMENDED\n")
            f.write("Significant issues found. Review and fix before migration.\n")

        f.write(f"\nTotal issues: {total_issues}\n")
        f.write(f"Data consistency: {consistency_score:.2%}\n")

        # Recommendations
        f.write("\nRECOMMENDations:\n")
        f.write("-" * 40 + "\n")

        if total_issues > 0:
            f.write("1. Review and fix validation issues before migration\n")
        if consistency_score < 0.9:
            f.write("2. Investigate schema/data mismatches\n")
        if 'cross_validation' in validation_results:
            cross_val = validation_results['cross_validation']
            if cross_val.get('schema_only_tables'):
                f.write("3. Consider if schema-only tables need data\n")
            if cross_val.get('data_only_tables'):
                f.write("4. Ensure data-only tables have proper schema definitions\n")

        f.write("5. Test migration on a subset of data first\n")
        f.write("6. Have a rollback plan ready\n")

        f.write(f"\nReport generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    logger.info(f"Validation report saved to: {report_file}")
    return report_file