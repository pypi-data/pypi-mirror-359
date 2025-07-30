#!/usr/bin/env python3
"""
Main test runner for the CockroachDB migrator test suite.

This script follows Python testing best practices by:
1. Using unittest's test discovery mechanism
2. Proper module imports using relative imports
3. Structured test organization
4. Standard test runner patterns
"""

import sys
import os
import unittest
import logging
from pathlib import Path

# Add the parent directory to Python path for package imports
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

def setup_logging():
    """Set up logging for the test runner"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('test_results.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def run_unittest_discovery():
    """
    Use unittest's built-in test discovery to find and run all tests.
    This is the recommended approach for Python testing.
    """
    logger = logging.getLogger(__name__)
    
    # Change to tests directory for proper test discovery
    original_cwd = os.getcwd()
    tests_dir = Path(__file__).parent
    os.chdir(tests_dir)
    
    try:
        # Discover tests using unittest's discovery mechanism
        loader = unittest.TestLoader()
        start_dir = '.'
        pattern = 'test_*.py'
        
        logger.info(f"Discovering tests in {tests_dir} with pattern '{pattern}'")
        
        # Load tests
        suite = loader.discover(start_dir, pattern=pattern)
        
        # Count tests
        test_count = suite.countTestCases()
        logger.info(f"Discovered {test_count} test cases")
        
        if test_count == 0:
            logger.warning("No tests discovered. This might indicate import issues.")
            return None
        
        # Run tests with detailed output
        runner = unittest.TextTestRunner(
            verbosity=2,
            stream=sys.stdout,
            buffer=True,  # Capture stdout/stderr during tests
            failfast=False  # Continue running tests even if some fail
        )
        
        result = runner.run(suite)
        return result
        
    except Exception as e:
        logger.error(f"Error during test discovery: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None
    finally:
        # Restore original working directory
        os.chdir(original_cwd)

def run_manual_tests():
    """
    Fallback method to run tests manually if discovery fails.
    This handles tests that might not follow standard unittest patterns.
    """
    logger = logging.getLogger(__name__)
    logger.info("Running manual test execution as fallback...")
    
    results = []
    
    # List of test modules that can be run manually
    manual_test_modules = [
        'test_schema_conversion',
        'test_cockroach_download', 
        'test_chunked_export',
        'test_postgres_download',
        'test_postgresql_import',
        'test_chunked_integration'
    ]
    
    for module_name in manual_test_modules:
        try:
            logger.info(f"Attempting to run {module_name}")
            
            # Try to import and run the module
            if module_name == 'test_schema_conversion':
                # This uses unittest framework
                try:
                    from test_schema_conversion import TestSchemaConversion
                    suite = unittest.TestLoader().loadTestsFromTestCase(TestSchemaConversion)
                    runner = unittest.TextTestRunner(verbosity=2)
                    result = runner.run(suite)
                    results.append((module_name, result.wasSuccessful(), None))
                except Exception as e:
                    results.append((module_name, False, str(e)))
            
            else:
                # For standalone test modules, try to run their main functions
                try:
                    module = __import__(module_name)
                    
                    # Look for common test function patterns
                    test_functions = [attr for attr in dir(module) 
                                    if attr.startswith('test_') and callable(getattr(module, attr))]
                    
                    if test_functions:
                        for func_name in test_functions:
                            try:
                                func = getattr(module, func_name)
                                func()
                                logger.info(f"✓ {module_name}.{func_name} PASSED")
                                results.append((f"{module_name}.{func_name}", True, None))
                            except Exception as e:
                                logger.error(f"✗ {module_name}.{func_name} FAILED: {e}")
                                results.append((f"{module_name}.{func_name}", False, str(e)))
                    
                    elif hasattr(module, 'main'):
                        module.main()
                        logger.info(f"✓ {module_name} PASSED")
                        results.append((module_name, True, None))
                    
                    else:
                        logger.warning(f"No runnable tests found in {module_name}")
                        results.append((module_name, False, "No runnable tests found"))
                        
                except Exception as e:
                    logger.error(f"Failed to run {module_name}: {e}")
                    results.append((module_name, False, str(e)))
                    
        except Exception as e:
            logger.error(f"Failed to import {module_name}: {e}")
            results.append((module_name, False, f"Import error: {e}"))
    
    return results

def print_manual_test_summary(results):
    """Print summary for manual test results"""
    logger = logging.getLogger(__name__)
    
    logger.info("\n" + "="*60)
    logger.info("MANUAL TEST SUMMARY")
    logger.info("="*60)
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    logger.info(f"Total Tests: {total}")
    logger.info(f"Passed: {passed}")
    logger.info(f"Failed: {total - passed}")
    logger.info(f"Success Rate: {(passed/total*100):.1f}%" if total > 0 else "Success Rate: N/A")
    
    if total > passed:
        logger.info("\nFailed Tests:")
        for name, success, error in results:
            if not success:
                logger.info(f"  - {name}: {error}")
    
    return passed == total

def print_unittest_summary(result):
    """Print summary for unittest results"""
    logger = logging.getLogger(__name__)
    
    logger.info("\n" + "="*60)
    logger.info("UNITTEST SUMMARY")
    logger.info("="*60)
    
    logger.info(f"Tests Run: {result.testsRun}")
    logger.info(f"Failures: {len(result.failures)}")
    logger.info(f"Errors: {len(result.errors)}")
    logger.info(f"Skipped: {len(result.skipped)}")
    
    success_count = result.testsRun - len(result.failures) - len(result.errors)
    logger.info(f"Successful: {success_count}")
    
    if result.testsRun > 0:
        success_rate = (success_count / result.testsRun) * 100
        logger.info(f"Success Rate: {success_rate:.1f}%")
    
    # Print details of failures and errors
    if result.failures:
        logger.info("\nFailures:")
        for test, traceback in result.failures:
            logger.info(f"  - {test}")
            logger.debug(f"    Traceback: {traceback}")
    
    if result.errors:
        logger.info("\nErrors:")
        for test, traceback in result.errors:
            logger.info(f"  - {test}")
            logger.debug(f"    Traceback: {traceback}")
    
    return result.wasSuccessful()

def main():
    """
    Main test runner function following Python testing best practices.
    
    This function:
    1. First tries unittest discovery (recommended approach)
    2. Falls back to manual test execution if discovery fails
    3. Provides comprehensive reporting
    4. Returns appropriate exit codes
    """
    logger = setup_logging()
    logger.info("CockroachDB Migrator Test Suite")
    logger.info("="*60)
    
    # Try unittest discovery first (best practice)
    logger.info("Attempting unittest test discovery...")
    unittest_result = run_unittest_discovery()
    
    if unittest_result is not None and unittest_result.testsRun > 0:
        # Unittest discovery was successful
        success = print_unittest_summary(unittest_result)
        logger.info(f"\nTest execution completed using unittest discovery")
        logger.info(f"Results saved to: test_results.log")
        sys.exit(0 if success else 1)
    
    else:
        # Fall back to manual test execution
        logger.warning("Unittest discovery failed or found no tests. Trying manual execution...")
        manual_results = run_manual_tests()
        
        if manual_results:
            success = print_manual_test_summary(manual_results)
            logger.info(f"\nTest execution completed using manual method")
            logger.info(f"Results saved to: test_results.log")
            sys.exit(0 if success else 1)
        else:
            logger.error("No tests could be executed")
            sys.exit(1)

if __name__ == "__main__":
    main()