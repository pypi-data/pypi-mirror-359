#!/usr/bin/env python3
"""
Test cases for CockroachDB binary download functionality
"""

import unittest
import logging
import tempfile
from pathlib import Path
import sys
import os
import platform

# Add parent directory to path for package imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from cockroach_migrator.migrate_cockroach import download_cockroach_binary


class TestCockroachDownload(unittest.TestCase):
    """Test cases for CockroachDB binary download functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.logger = logging.getLogger('test_cockroach_download')
        self.logger.setLevel(logging.INFO)

        # Test parameters
        self.cockroach_version = "v24.3.5"

        # Determine platform for testing
        system = platform.system().lower()
        machine = platform.machine().lower()

        if system == 'linux':
            if machine in ['x86_64', 'amd64']:
                self.os_name, self.arch = 'linux', 'amd64'
            elif machine in ['aarch64', 'arm64']:
                self.os_name, self.arch = 'linux', 'arm64'
        elif system == 'darwin':
            if machine in ['x86_64', 'amd64']:
                self.os_name, self.arch = 'darwin', 'amd64'
            elif machine in ['arm64']:
                self.os_name, self.arch = 'darwin', 'arm64'
        elif system == 'windows':
            self.os_name, self.arch = 'windows', 'amd64'
        else:
            self.skipTest(f"Unsupported platform: {system} {machine}")

    def test_cockroach_download(self):
        """Test the CockroachDB binary download functionality"""

        # Create a temporary directory for the test
        with tempfile.TemporaryDirectory() as temp_dir:
            self.logger.info("Testing CockroachDB binary download functionality...")

            # Test first download
            self.logger.info("First download attempt...")
            binary_path1 = download_cockroach_binary(
                self.os_name, self.arch, temp_dir, self.cockroach_version, self.logger
            )

            # Verify the binary exists in the persistent directory
            expected_dir = Path.cwd() / f"cockroach-{self.cockroach_version}"
            expected_binary = expected_dir / ("cockroach.exe" if self.os_name == "windows" else "cockroach")

            self.assertTrue(expected_binary.exists(), f"Binary not found at expected location: {expected_binary}")
            self.assertEqual(str(expected_binary), binary_path1, f"Returned path doesn't match expected: {binary_path1} vs {expected_binary}")

            self.logger.info(f"[OK] Binary successfully downloaded to: {binary_path1}")

            # Test second download (should skip download)
            self.logger.info("Second download attempt (should skip)...")
            binary_path2 = download_cockroach_binary(
                self.os_name, self.arch, temp_dir, self.cockroach_version, self.logger
            )

            self.assertEqual(binary_path1, binary_path2, "Second download should return same path")
            self.logger.info("[OK] Second download correctly skipped existing binary")

            self.logger.info("All tests passed!")
            self.logger.info(f"CockroachDB binary is preserved at: {expected_dir}")


if __name__ == "__main__":
    unittest.main()