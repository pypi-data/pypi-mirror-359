#!/usr/bin/env python3
"""
Command-line interface for CockroachDB to PostgreSQL migration tool.
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path

from .migrate import CockroachMigrator


def create_sample_config():
    """Create a sample configuration file"""
    config_template = {
        "aws_access_key_id": "your_aws_access_key_here",
        "aws_secret_access_key": "your_aws_secret_key_here",
        "s3_backup_path": "s3://your-bucket/your-backup-path",
        "cockroach_version": "v24.3.5",
        "cockroach_port": 26257,
        "cockroach_http_port": 8080,
        "certs_dir": "cockroachdb/certs",
        "insecure_mode": True,
        "postgres_host": "localhost",
        "postgres_port": 5432,
        "postgres_database": "postgres",
        "postgres_username": "postgres",
        "postgres_password": "your_postgres_password_here",
        "postgres_version": "17.0",
        "skip_validation": False,
        "postgres_import_enabled": True,
        "test_postgresql_import": True,
        "test_postgres_port": 5433,
        "test_database_name": "migration_test",
        "test_username": "postgres",
        "test_password": "YOUR_TEST_PASSWORD",
        "do_cleanup": True,
        "temp_dir": "",
        "chunk_size": 10000
    }

    config_file = "migration_config.json"
    with open(config_file, 'w') as f:
        json.dump(config_template, f, indent=2)

    print(f"Sample configuration file created: {config_file}")
    print("Please edit this file with your specific values before running the migration.")


def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('migration.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)


def main():
    """Main entry point for the CLI"""
    parser = argparse.ArgumentParser(
        description="Migrate CockroachDB backup from S3 to PostgreSQL",
        prog="cockroach-migrate"
    )
    parser.add_argument(
        "--config",
        default="migration_config.json",
        help="Path to configuration JSON file (default: migration_config.json)"
    )
    parser.add_argument(
        "--create-config",
        action="store_true",
        help="Create sample configuration file"
    )
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip validation step"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0"
    )

    args = parser.parse_args()

    # Setup logging
    logger = setup_logging()

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