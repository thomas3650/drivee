#!/usr/bin/env python3
"""Standalone test runner for basic validation tests.

This script runs tests without requiring pytest or Home Assistant.
Useful for local development on Windows where HA installation is problematic.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add tests directory to path
sys.path.insert(0, str(Path(__file__).parent / "tests"))

#Import test functions
from test_basic import (
    test_const_values,
    test_manifest_valid,
    test_required_files_exist,
    test_strings_valid,
    test_version_format,
)


def run_test(test_func, test_name: str) -> bool:
    """Run a single test function and return True if it passes."""
    try:
        test_func()
        print(f"[PASS] {test_name}")
        return True
    except AssertionError as e:
        print(f"[FAIL] {test_name}: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] {test_name}: {e}")
        return False


def main() -> int:
    """Run all basic tests and return exit code."""
    print("Running basic validation tests...")
    print("=" * 60)

    tests = [
        (test_manifest_valid, "test_manifest_valid"),
        (test_strings_valid, "test_strings_valid"),
        (test_required_files_exist, "test_required_files_exist"),
        (test_const_values, "test_const_values"),
        (test_version_format, "test_version_format"),
    ]

    results = []
    for test_func, test_name in tests:
        results.append(run_test(test_func, test_name))

    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        print("\nSUCCESS: All tests passed!")
        return 0
    else:
        print(f"\nFAILURE: {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
