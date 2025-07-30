"""
CockroachDB to PostgreSQL Migration Tool

A comprehensive tool for migrating data from CockroachDB backups to PostgreSQL databases.
"""

__version__ = "0.1.0"
__author__ = "Nomos"
__email__ = "oss@ordicio.com"

from .migrate import CockroachMigrator

__all__ = ["CockroachMigrator"]