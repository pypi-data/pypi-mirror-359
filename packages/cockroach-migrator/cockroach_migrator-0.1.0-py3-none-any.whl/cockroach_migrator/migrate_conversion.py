import re
import hashlib

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

def create_unique_index_name(original_name: str, db_name: str = None, table_name: str = None) -> str:
    """Create a unique, PostgreSQL-compatible index name within 63 character limit"""
    # Clean the original name
    clean_name = original_name.strip().strip('"').strip()

    # Remove common redundant suffixes to save space
    clean_name = re.sub(r'_?index\d*$', '', clean_name, flags=re.IGNORECASE)
    clean_name = re.sub(r'_?idx\d*$', '', clean_name, flags=re.IGNORECASE)

    # Create a 4-character hash of the table name for uniqueness
    table_hash = ""
    if table_name:
        clean_table = table_name.strip().strip('"').strip()
        table_hash = hashlib.md5(clean_table.encode()).hexdigest()[:4]

    # Build the index name: db_indexname_tablehash
    parts = []
    if db_name:
        parts.append(db_name.lower())
    if clean_name:
        parts.append(clean_name.lower())
    if table_hash:
        parts.append(table_hash)

    base_name = "_".join(parts)

    # PostgreSQL identifier limit is 63 characters
    max_length = 63
    if len(base_name) > max_length:
        # If still too long, create a hash from the full context and truncate
        hash_input = f"{original_name}_{db_name or ''}_{table_name or ''}"
        short_hash = hashlib.md5(hash_input.encode()).hexdigest()[:4]

        # Truncate base name to leave room for hash and underscore
        truncated_length = max_length - len(short_hash) - 1  # -1 for underscore
        base_name = base_name[:truncated_length] + "_" + short_hash

    return base_name

# transform cockroach ddl to postgresql compatible
def process_ddl_content(content: str, db_name: str = None) -> tuple[str, str, str]:
    """
    Process DDL content and return (tables_sql, constraints_sql, indexes_sql)
    """
    lines = content.split('\n')

    tab_out = []
    ref_out = []
    ind_out = []

    # Trackers
    nextline = ""
    indexes = ""
    table = ""

    # Add extension as first line
    tab_out.append("create extension if not exists pgcrypto;")

    for idx, line in enumerate(lines):
        original_line = line.rstrip()

        # Remove schema 'public.' from TABLE or REFERENCES statements
        if re.search(r'TABLE public[.]', original_line):
            line = re.sub(r'(REFERENCES |TABLE )public[.]', r'\1', original_line)
        else:
            line = original_line

        # Move commas at end of line to the beginning of the next line
        if nextline:
            match = re.match(r"(^\t*)(.*)$", line)
            if match:
                indent, content_part = match.groups()
                line = f"{indent}{nextline}{content_part}"
            nextline = ""

        if line.rstrip().endswith(","):
            line = line.rstrip().rstrip(",")
            nextline = ","

        # Extract table name after CREATE TABLE
        m_create_table = re.match(r'^CREATE TABLE (.*) \(', line)
        if m_create_table:
            table = m_create_table.group(1)

        # Handle INDEX clause within CREATE TABLE
        m_index = re.match(r"^\t*,(UNIQUE )?INDEX", line)
        if m_index:
            # Gensub for STORING -> INCLUDE
            line_mod = re.sub(r" STORING ", " INCLUDE ", line)
            # Compose index SQL statement with database prefix for uniqueness
            def create_index_statement(m):
                unique_part = m.group(1) or ''
                index_keyword = m.group(2)
                original_index_name = m.group(3).strip()

                # Create a unique, length-appropriate index name
                unique_index_name = create_unique_index_name(original_index_name, db_name, table)

                table_part = m.group(4)
                storing_part = m.group(5) or ''
                rest_part = m.group(6)

                return f"create {unique_part}{index_keyword} {unique_index_name} on {table}{table_part}{storing_part}{rest_part};"

            line_mod = re.sub(r"^\t*,(UNIQUE )?(INDEX)([^(]+)(.*)( STORING)?(.*)$", create_index_statement, line_mod)
            indexes += "\n" + line_mod
            # Comment out original index line in tab_out
            line = re.sub(r"(^\t*),(.*)$", r"\1--\2", line)

        # Handle constraint creation (ALTER TABLE ... ADD CONSTRAINT)
        if re.match(r"^ALTER TABLE.*ADD CONSTRAINT.*", line):
            # Remove NOT VALID
            line2 = re.sub(r'(.*)(NOT VALID)?(;)$', r'\1\3', line)
            ref_out.append(line2)
            # Comment out in tab file
            line = "--" + line

        # Handle inline PRIMARY KEY constraints with duplicate names
        if 'CONSTRAINT "primary" PRIMARY KEY' in line:
            # Replace generic "primary" constraint name with table-specific name
            clean_table = table.strip('"').replace('"', '') if table else 'table'
            line = line.replace('CONSTRAINT "primary"', f'CONSTRAINT "{clean_table}_primary"')

        # Handle other common constraint name conflicts
        if 'CONSTRAINT "unique"' in line:
            clean_table = table.strip('"').replace('"', '') if table else 'table'
            line = line.replace('CONSTRAINT "unique"', f'CONSTRAINT "{clean_table}_unique"')

        # Comment out VALIDATE CONSTRAINT
        if re.match(r"^ALTER TABLE.*VALIDATE CONSTRAINT.*;$", line):
            line = "--" + line

        # Output to tab file
        tab_out.append(line)

    # Apply final conversions to the processed content
    tables_sql = '\n'.join(tab_out)
    constraints_sql = '\n'.join(ref_out) if ref_out else ""
    indexes_sql = indexes.lstrip("\n") if indexes.strip() else ""

    # Apply JSON to JSONB conversion after processing
    tables_sql = re.sub(r'\bJSON\b', 'JSONB', tables_sql)
    constraints_sql = re.sub(r'\bJSON\b', 'JSONB', constraints_sql)
    indexes_sql = re.sub(r'\bJSON\b', 'JSONB', indexes_sql)

    return tables_sql, constraints_sql, indexes_sql

def convert_schema_to_postgresql(schema_content: str, logger, db_name: str = None) -> str:
    """Convert CockroachDB schema to PostgreSQL compatible format using advanced DDL processing"""
    logger.info("Converting schema from CockroachDB to PostgreSQL format using advanced DDL processing")

    # Handle empty input
    if not schema_content or not schema_content.strip():
        return ""

    try:
        # First, clean up any wrapped SQL statements before processing
        cleaned_content = clean_wrapped_sql_statements(schema_content, logger)

        # Apply basic type conversions
        cleaned_content = apply_basic_conversions(cleaned_content, logger)

        # Use the advanced DDL processing function
        tables_sql, constraints_sql, indexes_sql = process_ddl_content(cleaned_content, db_name)

        # Combine all parts in the proper order
        converted_parts = []

        if tables_sql:
            converted_parts.append("-- Tables and basic structure")
            converted_parts.append(tables_sql)

        if constraints_sql:
            converted_parts.append("\n-- Constraints and foreign keys")
            converted_parts.append(constraints_sql)

        if indexes_sql:
            converted_parts.append("\n-- Indexes")
            converted_parts.append(indexes_sql)

        converted_schema = '\n'.join(converted_parts)

        logger.info("Advanced DDL processing completed successfully")
        return converted_schema

    except Exception as e:
        logger.warning(f"Advanced DDL processing failed: {e}")
        logger.info("Falling back to basic schema conversion")

        # Fallback to basic conversions
        return apply_basic_conversions(schema_content, logger)

def apply_basic_conversions(schema_content: str, logger) -> str:
    """Apply basic CockroachDB to PostgreSQL conversions"""
    # Replace CockroachDB-specific syntax with PostgreSQL equivalents
    schema_content = schema_content.replace('STRING', 'TEXT')
    schema_content = schema_content.replace('BYTES', 'BYTEA')
    schema_content = schema_content.replace('SERIAL8', 'BIGSERIAL')
    schema_content = schema_content.replace('SERIAL4', 'SERIAL')
    schema_content = schema_content.replace('INT8', 'BIGINT')
    schema_content = schema_content.replace('INT4', 'INTEGER')
    schema_content = schema_content.replace('INT2', 'SMALLINT')

    # Fix TEXT with length modifiers - PostgreSQL doesn't support TEXT(n)
    # Convert TEXT(n) to VARCHAR(n)
    schema_content = re.sub(r'\bTEXT\s*\(\s*(\d+)\s*\)', r'VARCHAR(\1)', schema_content)

    # Fix CREATE DATABASE IF NOT EXISTS (not supported in PostgreSQL)
    schema_content = re.sub(r'CREATE DATABASE IF NOT EXISTS\s+', 'CREATE DATABASE ', schema_content, flags=re.IGNORECASE)

    # Fix DEFAULT with type casting (e.g., DEFAULT 0:::BIGINT -> DEFAULT 0)
    schema_content = re.sub(r'DEFAULT\s+(\w+):::\w+', r'DEFAULT \1', schema_content)

    # Remove ASC from PRIMARY KEY declarations
    schema_content = re.sub(r'PRIMARY KEY\s*\([^)]+\s+ASC\s*\)', lambda m: m.group(0).replace(' ASC', ''), schema_content, flags=re.IGNORECASE)

    # Remove ASC from single-column INDEX declarations (keep for multi-column)
    schema_content = re.sub(r'CREATE\s+(?:UNIQUE\s+)?INDEX\s+\w+\s+ON\s+\w+\s*\(\s*\w+\s+ASC\s*\)',
                           lambda m: m.group(0).replace(' ASC', ''), schema_content, flags=re.IGNORECASE)

    # Handle JSON to JSONB conversion (PostgreSQL prefers JSONB)
    # Use word boundaries to avoid replacing parts of other words
    schema_content = re.sub(r'\bJSON\b', 'JSONB', schema_content)

    # Remove CockroachDB-specific constraints and settings
    lines = schema_content.split('\n')
    filtered_lines = []
    for line in lines:
        line_upper = line.upper()
        # Skip CockroachDB-specific statements
        if not any(skip_pattern in line_upper for skip_pattern in [
            'FAMILY ', 'INTERLEAVE', 'STORING', 'SPLIT AT', 'CONFIGURE ZONE',
            'INVERTED INDEX', 'HASH SHARDED INDEX', 'LOCALITY REGIONAL',
            'PARTITION BY', 'WITH (ttl_'
        ]):
            # Handle UUID generation differences
            if 'gen_random_uuid()' in line:
                line = line.replace('gen_random_uuid()', 'uuid_generate_v4()')

            # Fix INSERT statements with invalid column lists (tab-separated instead of comma-separated)
            if line.strip().upper().startswith('INSERT INTO'):
                # Fix column list: replace tabs with commas in the column specification
                # Pattern to match: INSERT INTO "table" ("col1	col2	col3") VALUES (...)
                insert_match = re.search(r'INSERT INTO\s+"([^"]+)"\s*\(\s*"([^"]+)"\s*\)', line, re.IGNORECASE)
                if insert_match and '\t' in insert_match.group(2):
                    table_name = insert_match.group(1)
                    column_list = insert_match.group(2)
                    # Split by tabs and create proper comma-separated list
                    columns = [f'"{col.strip()}"' for col in column_list.split('\t')]
                    new_column_list = ', '.join(columns)
                    # Replace the column list in the line
                    line = line.replace(f'"{column_list}"', new_column_list)

                # Also fix VALUES part if it contains tab-separated values
                values_match = re.search(r"VALUES\s*\(\s*'([^']+)'\s*\)", line)
                if values_match and '\t' in values_match.group(1):
                    values_list = values_match.group(1)
                    # Split by tabs and create proper comma-separated list
                    values = [f"'{val.strip()}'" for val in values_list.split('\t')]
                    new_values_list = ', '.join(values)
                    # Replace the values list in the line
                    line = line.replace(f"'{values_list}'", new_values_list)

            filtered_lines.append(line)

    return '\n'.join(filtered_lines)

def clean_wrapped_sql_statements(sql_content: str, logger) -> str:
    """Clean up wrapped SQL statements and convert them to standard format"""
    logger.info("Cleaning wrapped SQL statements")

    lines = sql_content.split('\n')
    cleaned_lines = []

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Skip empty lines and comments
        if not line or line.startswith('--'):
            cleaned_lines.append(lines[i])
            i += 1
            continue

        # Check for create_statement line - skip it and process following quoted statements
        if line == 'create_statement':
            i += 1  # Skip the create_statement line itself

            # Process all following quoted SQL statements
            while i < len(lines):
                current_line = lines[i].strip()

                # Check if this line starts a quoted SQL statement
                if current_line.startswith('"'):
                    # Process this quoted multiline statement
                    j = i
                    sql_lines = []

                    while j < len(lines):
                        stmt_line = lines[j]

                        if j == i:
                            # First line - remove opening quote
                            content = stmt_line.strip()[1:]
                            if content:
                                sql_lines.append(content)
                        elif stmt_line.strip().endswith('"'):
                            # Last line - remove closing quote
                            line_content = stmt_line.rstrip()[:-1]
                            if line_content:
                                sql_lines.append(line_content)
                            break
                        else:
                            # Middle line of the quoted statement
                            sql_lines.append(stmt_line)
                        j += 1

                    if sql_lines:
                        # Join the SQL lines and clean up
                        sql_statement = '\n'.join(sql_lines)

                        # Replace double quotes with single quotes for identifiers
                        sql_statement = sql_statement.replace('""', '"')

                        # Add the cleaned statement
                        cleaned_lines.append(sql_statement)

                    i = j + 1  # Move past this quoted statement
                else:
                    # No more quoted statements following create_statement
                    break
            continue

        # For regular lines, just add them as-is
        cleaned_lines.append(lines[i])
        i += 1

    return '\n'.join(cleaned_lines)

def convert_csv_to_inserts(csv_file: Path, table_name: str, output_file, logger):
    """Convert CSV file to INSERT statements"""
    import csv

    try:
        with open(csv_file, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            headers = next(reader)  # Get column names from header

            for row in reader:
                # Escape and quote values
                escaped_values = []
                for value in row:
                    if value == '':
                        escaped_values.append('NULL')
                    else:
                        # Escape single quotes and wrap in quotes
                        escaped_value = value.replace("'", "''")
                        escaped_values.append(f"'{escaped_value}'")

                # Create INSERT statement
                columns = ', '.join(f'"{col}"' for col in headers)
                values = ', '.join(escaped_values)
                insert_sql = f"INSERT INTO \"{table_name}\" ({columns}) VALUES ({values});\n"
                output_file.write(insert_sql)

    except Exception as e:
        logger.warning(f"Failed to convert CSV {csv_file} to INSERT statements: {e}")

def convert_select_to_inserts(select_result: str, table_name: str, output_file, logger, column_definitions: dict = None):
    """Convert SELECT result to INSERT statements with column length validation"""
    lines = select_result.split('\n')
    headers = None
    logger.debug(f"tanslating raw select statement: {select_result}")

    for line in lines:
        line = line.strip()
        if not line or line.startswith('-') or line.startswith('('):
            continue

        if headers is None:
            # First non-empty line should be headers
            # CockroachDB uses tab-separated output, not pipe-separated
            if '\t' in line:
                headers = [col.strip() for col in line.split('\t')]
            else:
                # Fallback to pipe-separated for other formats
                headers = [col.strip() for col in line.split('|')]
            continue

        # Data row - handle tab-separated CockroachDB output
        if '\t' in line:
            values = [val.strip() for val in line.split('\t')]
        else:
            # Fallback to pipe-separated for other formats
            values = [val.strip() for val in line.split('|')]

        if len(values) == len(headers):
            # Escape and quote values
            escaped_values = []
            for i, value in enumerate(values):
                # Get column name and definition for length validation
                column_name = headers[i] if i < len(headers) else None
                column_def = column_definitions.get(column_name, {}) if column_definitions and column_name else {}
                max_length = column_def.get('length_constraint')

                if value == '' or value.lower() == 'null':
                    escaped_values.append('NULL')
                else:
                    # Handle JSON data specially - fix double-escaped quotes
                    if value.startswith('"{') and value.endswith('}"'):
                        # This looks like JSON data with double-escaped quotes
                        # Remove outer quotes and fix double-escaped quotes
                        json_content = value[1:-1]  # Remove outer quotes
                        json_content = json_content.replace('""', '"')  # Fix double-escaped quotes
                        # Escape single quotes for SQL and wrap in quotes
                        escaped_value = json_content.replace("'", "''")
                        escaped_values.append(f"'{escaped_value}'")
                    elif (value.startswith('"') and value.endswith('"') and len(value) > 2 and
                          ("''" in value or '""' in value)):
                        # This is a CockroachDB escaped string
                        # Remove outer double quotes
                        inner_content = value[1:-1]
                        # Convert CockroachDB escaping to PostgreSQL escaping
                        # CockroachDB: '' -> PostgreSQL: ''  (single quotes stay the same)
                        # CockroachDB: "" -> PostgreSQL: "   (double quotes become single)
                        postgresql_content = inner_content.replace('""', '"')
                        # Single quotes are already properly escaped as '' for PostgreSQL
                        postgresql_content = postgresql_content.replace("\'", "''")
                        escaped_values.append(f"'{postgresql_content}'")
                    # Validate length constraint if defined
                    elif max_length and len(value) > max_length and value.startswith('"') and value.endswith('"'):
                        logger.debug(f"Value in column '{column_name}' exceeds length limit ({len(escaped_value)} > {max_length}): Removing quote escapes")
                        value = value[1:len(value)-1]
                        if len(value) > max_length:
                            logger.error(f"Value in column '{column_name}' still exceeds length limit after truncating quotes ({len(escaped_value)} > {max_length}): something is very wrong!")
                        escaped_value = value.replace("'", "''")
                        escaped_values.append(f"'{escaped_value}'")
                    else:
                        # Regular value - escape single quotes and wrap in quotes
                        escaped_value = value.replace("'", "''")
                        # Validate length constraint if defined
                        if max_length and len(escaped_value) > max_length:
                            logger.error(f"Value in column '{column_name}' exceeds length limit ({len(escaped_value)} > {max_length}): truncating")
                            logger.debug(f"Original value: {escaped_value[:100]}...")
                            #escaped_value = escaped_value[:max_length]
                        escaped_values.append(f"'{escaped_value}'")

            # Create INSERT statement
            columns = ', '.join(f'"{col}"' for col in headers)
            values_str = ', '.join(escaped_values)
            insert_sql = f"INSERT INTO \"{table_name}\" ({columns}) VALUES ({values_str});\n"
            output_file.write(insert_sql)