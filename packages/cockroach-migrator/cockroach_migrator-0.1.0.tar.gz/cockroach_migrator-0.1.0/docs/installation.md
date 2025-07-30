# Installation Guide

## Prerequisites

- Python 3.7 or higher
- pip package manager

## Installation Methods

### Method 1: Install from PyPI (Recommended)

Once published to PyPI, you can install the package directly:

```bash
pip install cockroach-migrator
```

### Method 2: Install from Source

Clone the repository and install in development mode:

```bash
git clone https://github.com/nomos-oss/cockroach-migrator.git
cd cockroach-migrator
pip install -e .
```

### Method 3: Install from Wheel

If you have a built wheel file:

```bash
pip install cockroach_migrator-0.1.0-py3-none-any.whl
```

## Development Installation

For development work, install with development dependencies:

```bash
git clone https://github.com/nomos-oss/cockroach-migrator.git
cd cockroach-migrator
pip install -e ".[dev]"
```

This installs additional tools for development:
- pytest (testing framework)
- pytest-cov (coverage reporting)
- black (code formatting)
- flake8 (linting)
- mypy (type checking)

## Verification

After installation, verify the package is working:

```bash
# Check if the command-line tool is available
cockroach-migrate --version

# Or use the alternative command
crdb-migrate --version

# Create a sample configuration file
cockroach-migrate --create-config
```

## System Requirements

### Required Software
- Python 3.7 or higher
- Internet connection (for downloading CockroachDB and PostgreSQL binaries)

### Optional Software
- PostgreSQL client tools (`psql` command) - automatically downloaded if missing
- AWS CLI (if using AWS credentials from environment)

### Required Files (when using secure mode)
- **Certificates**: CockroachDB certificates in `cockroachdb/certs/`
  - `ca.crt`
  - `client.root.crt`
  - `client.root.key`
  - `node.crt`
  - `node.key`

## Troubleshooting

### Common Issues

1. **Permission Errors**: Use `--user` flag for user-level installation:
   ```bash
   pip install --user cockroach-migrator
   ```

2. **Python Version**: Ensure you're using Python 3.7+:
   ```bash
   python --version
   ```

3. **Command Not Found**: Add Python scripts directory to PATH or use full path:
   ```bash
   python -m cockroach_migrator.cli --version
   ```

### Platform-Specific Notes

- **Windows**: The tool automatically downloads Windows binaries
- **macOS**: Supports both Intel and Apple Silicon
- **Linux**: Supports x86_64 and ARM64 architectures

## Uninstallation

To remove the package:

```bash
pip uninstall cockroach-migrator