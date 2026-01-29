Test Guide for ScrapLogGit2Net
📋 Overview

This guide explains how to run tests and write new tests for the ScrapLogGit2Net project.
🚀 Quick Start
Prerequisites
bash

# Install pytest and related tools
pip install pytest pytest-mock pytest-cov

# Optional: For rich output in tests
pip install rich loguru

Running Tests
bash

# Run all tests from project root
cd /path/to/ScrapLogGit2Net
python -m pytest tests/ -v

# Run with console output (to see rich tables)
python -m pytest tests/ -v -s

# Run specific test file
python -m pytest tests/test_parsing.py -v

# Run single test function
python -m pytest tests/test_parsing.py::test_email_parsing -v

# Run tests with coverage
python -m pytest tests/ --cov=. --cov-report=term-missing

📁 Project Structure
text

ScrapLogGit2Net/
├── tests/                      # All test

you are giving me several files. give me all in one file. Ready to copy&past into my text editor.
Test Guide for ScrapLogGit2Net
📋 Overview

This guide explains how to run tests and write new tests for the ScrapLogGit2Net project.
🚀 Quick Start
Prerequisites
bash

# Install pytest and related tools
pip install pytest pytest-mock pytest-cov

# Optional: For rich output in tests
pip install rich loguru

Running Tests
bash

# Run all tests from project root
cd /path/to/ScrapLogGit2Net
python -m pytest tests/ -v

# Run with console output (to see rich tables)
python -m pytest tests/ -v -s

# Run specific test file
python -m pytest tests/test_parsing.py -v

# Run single test function
python -m pytest tests/test_parsing.py::test_email_parsing -v

# Run tests with coverage
python -m pytest tests/ --cov=. --cov-report=term-missing

📁 Project Structure
text

ScrapLogGit2Net/
├── tests/                      # All test files
│   ├── conftest.py            # Pytest configuration (critical!)
│   ├── test_parsing.py        # Tests for parsing functions
│   ├── test_email_affiliation.py
│   ├── test_filters.py
│   ├── test_datamodels.py
│   ├── test_network.py
│   └── test_utils_validators.py
├── scrapLog.py                 # Main module
├── transform-nofi-2-nofo-GraphML.py
├── utils/
│   └── validators.py
└── uutils/
    └── unifiedOutputAndLogger.py

🔧 Critical: The conftest.py File

Create this file in your tests/ directory:
python

# tests/conftest.py
import sys
import os

# Add the project root to Python path so tests can import modules
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Optional: Print debug info
print(f"Python path: {sys.path}")
print(f"Project root: {project_root}")

🧪 Writing New Tests
Basic Test Template
python

# tests/test_your_feature.py
import pytest
from unittest.mock import patch

# Test function (no classes needed!)
def test_function_name():
    """Test description goes here."""
    # Arrange: Setup test data
    input_data = "test@example.com"
    expected = "example"
    
    # Act: Call the function
    result = getAffiliationFromEmail(input_data)
    
    # Assert: Verify the result
    assert result == expected

Full Example Test File
python

# tests/test_example.py
"""
Example test file showing best practices.
"""

import pytest
from unittest.mock import patch
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import functions to test
from scrapLog import getAffiliationFromEmail, getDateEmailAffiliation


# FIXTURES: Reusable test data
@pytest.fixture
def sample_emails():
    """Fixture providing sample email data."""
    return [
        "user@company.com",
        "dev@organization.org",
        "test@university.edu",
    ]


# BASIC TESTS
def test_email_processing():
    """Test basic email processing."""
    email = "user@google.com"
    expected = "google"
    
    result = getAffiliationFromEmail(email)
    assert result == expected


def test_invalid_email():
    """Test handling of invalid emails."""
    with pytest.raises(ValueError):
        getAffiliationFromEmail("not-an-email")


# PARAMETERIZED TESTS (multiple inputs)
@pytest.mark.parametrize("email,expected", [
    ("user@google.com", "google"),
    ("dev@microsoft.com", "microsoft"),
    ("eng@ibm.com", "ibm"),
    ("test@amazon.com", "amazon"),
])
def test_affiliation_extraction(email, expected):
    """Test multiple email cases."""
    result = getAffiliationFromEmail(email)
    assert result == expected


# TESTS WITH MOCKING
def test_with_mocked_globals():
    """Test function that uses global variables."""
    # Mock global variables from scrapLog module
    with patch('scrapLog.DEBUG_MODE', 1):
        with patch('scrapLog.EMAIL_FILTERING_MODE', 0):
            # Now test your function
            result = some_function_using_globals("test@example.com")
            assert result == "example"


# TESTS USING FIXTURES
def test_multiple_emails(sample_emails):
    """Test using the fixture."""
    for email in sample_emails:
        result = getAffiliationFromEmail(email)
        # Extract domain part (after @, before .)
        expected = email.split('@')[1].split('.')[0]
        assert result == expected

🎯 Best Practices
1. Test Naming Convention
python

# Good - descriptive names
def test_get_affiliation_from_email():
def test_parse_commit_block_valid():
def test_aggregate_by_file_empty_input():

# Bad - unclear names
def test1():
def email_test():
def run():

2. Test Organization in Files
python

# Group related tests with comments
# === EMAIL PARSING TESTS ===
def test_parse_simple_email(): ...
def test_parse_complex_email(): ...

# === DATE PARSING TESTS ===  
def test_parse_date_utc(): ...
def test_parse_date_with_offset(): ...

3. Use Helpful Assert Messages
python

# Good - helpful error messages
assert len(result) == 3, f"Expected 3 items, got {len(result)}"
assert email in valid_emails, f"{email} not in valid list"

# Bad - no context on failure
assert len(result) == 3
assert email in valid_emails

4. Test Expected Exceptions
python

def test_invalid_input_raises_error():
    """Test that invalid input raises ValueError."""
    with pytest.raises(ValueError) as exc_info:
        process_invalid_input("")
    
    # Check the error message
    assert "cannot be empty" in str(exc_info.value)

🔍 Common Test Patterns
Testing Functions with Global Variables
python

import pytest
from unittest.mock import patch

def test_function_with_globals():
    """When testing functions that use global variables from scrapLog."""
    # Mock the global variables
    with patch('scrapLog.DEBUG_MODE', 1):
        with patch('scrapLog.EMAIL_FILTERING_MODE', 0):
            with patch('scrapLog.list_of_emails_to_filter', []):
                # Now test your function
                result = getAffiliationFromEmail("test@example.com")
                assert result == "example"

Testing File I/O Operations
python

import tempfile
import pytest

def test_read_config_file():
    """Test reading from a configuration file."""
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt') as tmp:
        tmp.write("key=value\n")
        tmp.flush()  # Make sure data is written
        
        # Test the function
        result = read_config(tmp.name)
        assert result["key"] == "value"

Testing NetworkX Graph Functions
python

import networkx as nx

def test_graph_creation():
    """Test creating and manipulating graphs."""
    G = nx.Graph()
    
    # Add nodes and edges
    G.add_node("company1", type="organization")
    G.add_node("company2", type="organization")
    G.add_edge("company1", "company2", weight=5)
    
    # Verify
    assert G.number_of_nodes() == 2
    assert G.number_of_edges() == 1
    assert G["company1"]["company2"]["weight"] == 5

🐛 Debugging Tests
Common Error: Import Issues

If you see: ImportError: No module named 'scrapLog'

Solution 1: Run pytest with correct Python path:
bash

cd /path/to/ScrapLogGit2Net
PYTHONPATH=. python -m pytest tests/ -v

Solution 2: Ensure conftest.py exists in tests/ directory

Solution 3: Add path directly in test file:
python

# Add at top of test file
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

Useful Pytest Commands
bash

# See detailed output
python -m pytest tests/ -v -s

# Show local variables on failure
python -m pytest tests/ --showlocals

# Stop after first failure
python -m pytest tests/ -x

# Run only failed tests from last run
python -m pytest tests/ --lf

# Run tests matching pattern
python -m pytest tests/ -k "email"  # Runs tests with "email" in name

Debug with Python Debugger
bash

# Enter debugger on test failure
python -m pytest tests/ --pdb

# Debug specific test
python -m pytest tests/test_parsing.py::test_specific --pdb

📊 Test Coverage
Generate Coverage Reports
bash

# Terminal coverage report
python -m pytest tests/ --cov=. --cov-report=term-missing

# HTML coverage report (opens in browser)
python -m pytest tests/ --cov=. --cov-report=html
open htmlcov/index.html

# XML coverage report (for CI/CD)
python -m pytest tests/ --cov=. --cov-report=xml

What Coverage Shows

    term-missing: Shows which lines are not covered by tests

    html: Interactive report showing uncovered lines in red

    Aim for 70%+ coverage for critical modules

🤝 Contributing Tests
When to Add Tests

    New Features: Always add tests for new functionality

    Bug Fixes: Add test that reproduces the bug (proves it's fixed)

    Refactoring: Update tests when changing implementation

    Edge Cases: Add tests for boundary conditions

Test Checklist Before Submission

    All tests pass: python -m pytest tests/ -v

    No syntax errors in test files

    Tests are independent (don't rely on execution order)

    Tests clean up after themselves (no leftover files)

    Tests have descriptive names and docstrings

    Edge cases are covered

    Error conditions are tested

🎯 Quick Reference
Common Import Patterns
python

# For modules in project root
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scrapLog import function_name

# For utils modules
from utils.validators import validate_email

# For uutils modules
from uutils.unifiedOutputAndLogger import logger, console

Mocking Patterns
python

# Mock global variables
with patch('scrapLog.DEBUG_MODE', 1):
    # test code

# Mock external API calls
with patch('scrapLog.requests.get') as mock_get:
    mock_get.return_value.json.return_value = {"data": "test"}
    # test code

# Mock file operations
with patch('builtins.open', mock_open(read_data="test content")):
    # test code

Assertion Patterns
python

# Basic equality
assert result == expected

# Check type
assert isinstance(result, dict)

# Check contains
assert "error" in result_message.lower()

# Check raises exception
with pytest.raises(ValueError):
    function_with_invalid_input()

# Check list contents
assert all(item > 0 for item in result_list)

# Check dictionary keys
assert set(result.keys()) == {"key1", "key2", "key3"}

🚨 Troubleshooting
Problem: Tests run but imports fail

Solution: Make sure conftest.py is in tests/ directory and contains:
python

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

Problem: Global variables interfering with tests

Solution: Mock them in each test:
python

from unittest.mock import patch

def test_with_globals():
    with patch('scrapLog.DEBUG_MODE', 0):
        with patch('scrapLog.EMAIL_FILTERING_MODE', 0):
            # Your test code

Problem: Tests leaving temporary files

Solution: Use pytest fixtures or tempfile:
python

import tempfile
import pytest

@pytest.fixture
def temp_config_file():
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("test data")
        yield f.name
    # File automatically deleted after test

📚 Additional Resources
Pytest Documentation

    Official pytest documentation

    pytest-mock plugin

    pytest-cov plugin

Python Testing

    unittest.mock documentation

    Test-driven development with pytest

Project-Specific

    Check existing tests in tests/ directory for examples

    Look at function signatures in scrapLog.py to understand what to test

    Use print() or console.print() for debugging test execution