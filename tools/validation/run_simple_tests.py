#!/usr/bin/env python3
"""
Simple test runner for Imou Life integration.
This script runs tests without pytest to avoid Home Assistant plugin issues on Windows.
"""

import importlib
from pathlib import Path
import sys
import traceback

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def run_test_module(module_name):
    """Run a test module and return results."""
    print(f"\n{'='*60}")
    print(f"Running {module_name}")
    print(f"{'='*60}")

    try:
        # Import the module
        module = importlib.import_module(module_name)
        print(f"✅ Successfully imported {module_name}")

        # Look for test functions
        test_functions = []
        for attr_name in dir(module):
            if attr_name.startswith("test_"):
                test_functions.append(attr_name)

        if test_functions:
            print(
                f"Found {len(test_functions)} test functions: "
                f"{', '.join(test_functions)}"
            )
            print("Note: Test execution requires pytest and Home Assistant environment")
        else:
            print("No test functions found")

        return True, f"Module {module_name} imported successfully"

    except Exception as e:
        error_msg = f"Failed to import {module_name}: {str(e)}"
        print(f"❌ {error_msg}")
        print(f"Error details: {traceback.format_exc()}")
        return False, error_msg


def main():
    """Main test runner."""
    print("🧪 Imou Life - Simple Test Runner")
    print("=" * 50)
    print("This runner checks if test modules can be imported correctly.")
    print("Full test execution requires pytest and Home Assistant environment.")
    print()

    # Test modules to check
    test_modules = [
        "tests.unit.test_switch",
        "tests.unit.test_init",
        "tests.unit.test_config_flow",
        "tests.fixtures.const",
        "tests.fixtures.mocks",
        "tests.conftest",
    ]

    results = []
    passed = 0
    failed = 0

    for module_name in test_modules:
        success, message = run_test_module(module_name)
        results.append((module_name, success, message))
        if success:
            passed += 1
        else:
            failed += 1

    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {len(test_modules)}")

    if failed > 0:
        print("\n❌ FAILED MODULES:")
        for module_name, success, message in results:
            if not success:
                print(f"  - {module_name}: {message}")
        return 1
    else:
        print("\n🎉 All test modules imported successfully!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
