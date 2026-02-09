#!/usr/bin/env python
"""
GoWheels Test Runner
Run all tests with coverage reporting
"""
import sys
import os
import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    os.environ['DJANGO_SETTINGS_MODULE'] = 'gowheels_project.settings'
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2, interactive=True, keepdb=False)
    
    # Run all tests
    failures = test_runner.run_tests(["tests"])
    
    if failures:
        sys.exit(1)
    
    print("\n✅ All tests passed!")
    sys.exit(0)
