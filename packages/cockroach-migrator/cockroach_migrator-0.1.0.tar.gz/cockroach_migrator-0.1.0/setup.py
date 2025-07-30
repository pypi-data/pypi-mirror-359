#!/usr/bin/env python3
"""
Setup script for cockroach-migrator package
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements
requirements = []
requirements_file = this_directory / "requirements.txt"
if requirements_file.exists():
    requirements = requirements_file.read_text().strip().split('\n')
    requirements = [req.strip() for req in requirements if req.strip() and not req.startswith('#')]

setup(
    name="cockroach-migrator",
    version="0.1.0",
    author="Nomos",
    author_email="oss@ordicio.com",
    description="A comprehensive tool for migrating data from CockroachDB to PostgreSQL",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nomos-oss/cockroach-migrator",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Database",
        "Topic :: Database :: Database Engines/Servers",
        "Topic :: System :: Archiving :: Backup",
        "Topic :: Utilities",
    ],
    license="MIT",
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "cockroach-migrate=cockroach_migrator.cli:main",
            "crdb-migrate=cockroach_migrator.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "cockroach_migrator": [
            "config/*.json",
            "templates/*.json",
        ],
    },
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "test": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
        ],
    },
    keywords="cockroachdb postgresql migration database backup restore",
    project_urls={
        "Bug Reports": "https://github.com/nomos-oss/cockroach-migrator/issues",
        "Source": "https://github.com/nomos-oss/cockroach-migrator",
        "Documentation": "https://github.com/nomos-oss/cockroach-migrator#readme",
    },
)