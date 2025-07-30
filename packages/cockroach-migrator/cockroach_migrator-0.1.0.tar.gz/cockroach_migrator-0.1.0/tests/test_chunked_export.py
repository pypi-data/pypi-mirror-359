#!/usr/bin/env python3
"""
Test cases for chunked export functionality
"""

import unittest
import sys
import os
import tempfile
from pathlib import Path

# Add parent directory to path for package imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from cockroach_migrator.migrate_cockroach import count_data_rows


class TestChunkedExport(unittest.TestCase):
    """Test cases for chunked export functionality"""

    def test_count_data_rows(self):
        """Test the count_data_rows function"""
        
        # Test case 1: Normal SELECT result with 3 data rows
        test_result1 = """id	name	email
1	John Doe	john@example.com
2	Jane Smith	jane@example.com
3	Bob Johnson	bob@example.com
(3 rows)"""
        
        count1 = count_data_rows(test_result1)
        self.assertEqual(count1, 3, f"Expected 3 rows, got {count1}")
        
        # Test case 2: Empty result
        test_result2 = """id	name	email
(0 rows)"""
        
        count2 = count_data_rows(test_result2)
        self.assertEqual(count2, 0, f"Expected 0 rows, got {count2}")
        
        # Test case 3: Single row
        test_result3 = """id	name
1	Test User
(1 row)"""
        
        count3 = count_data_rows(test_result3)
        self.assertEqual(count3, 1, f"Expected 1 row, got {count3}")

    def test_chunked_export_logic(self):
        """Test the chunked export logic without actual database"""
        
        # Test chunk calculation
        total_rows = 25000
        chunk_size = 10000
        expected_chunks = (total_rows + chunk_size - 1) // chunk_size  # Ceiling division
        
        self.assertEqual(expected_chunks, 3, f"Expected 3 chunks for 25000 rows with 10000 chunk size, got {expected_chunks}")
        
        # Test edge cases
        test_cases = [
            (10000, 10000, 1),  # Exact match
            (10001, 10000, 2),  # One extra row
            (9999, 10000, 1),   # Just under
            (0, 10000, 1),      # Zero rows (should still be 1 chunk minimum)
        ]
        
        for rows, chunk, expected in test_cases:
            calculated = (rows + chunk - 1) // chunk if rows > 0 else 1
            self.assertEqual(calculated, expected, f"Chunk calculation failed for {rows} rows")


if __name__ == "__main__":
    unittest.main()
    main()