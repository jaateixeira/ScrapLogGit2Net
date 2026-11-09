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
python -m pytest tests/unit/test_parsing.py -v

# Run single test function
python -m pytest tests/unit/test_parsing.py::test_processing_statistics -v

# Run tests with coverage
python -m pytest tests/ --cov=. --cov-report=term-missing

📁 Project Structure
text

ScrapLogGit2Net/
├── pyproject.toml              # pytest config ([tool.pytest.ini_options])
├── tests/
│   ├── conftest.py             # Pytest configuration + shared fixtures (critical!)
│   ├── test_guide.md           # This guide
│   ├── unit/                   # pytest unit tests
│   │   ├── test_parsing.py     # Tests for parsing functions
│   │   ├── test_email_affiliation.py
│   │   ├── test_filters.py
│   │   ├── test_datamodels.py
│   │   ├── test_network.py
│   │   ├── test_transform_network.py
│   │   ├── test_parsing_to_temporal_networks.py
│   │   ├── test_extract_temporal_network_from_parsed_change_log_entries.py
│   │   ├── test_nofo_network_visualizer.py
│   │   └── test_utils_validators.py
│   └── acceptance-test-scripts/ # bash end-to-end tests (run from project root)
├── test-data/                  # Input files used by the tests
├── scrapLog.py                 # Main module
├── transform_nofi_2_nofo_graphml.py
├── core/
│   ├── models.py
│   └── types.py
└── utils/
    ├── validators.py
    ├── unified_console.py
    └── unified_logger.py

🔧 Critical: The conftest.py File

tests/conftest.py already exists. Its key part is:
python

# tests/conftest.py
import sys
import os

# Add the project root (and utils/) to Python path so tests can import modules
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'utils'))

🧪 Writing New Tests
Basic Test Template
python

# tests/unit/test_your_feature.py
from scrapLog import ProcessingState, extract_affiliation_from_email

# Test function (no classes needed!)
def test_function_name():
    """Test description goes here."""
    # Arrange: Setup test data
    state = ProcessingState()
    email = "test@example.com"
    expected = "example"

    # Act: Call the function
    result = extract_affiliation_from_email(email, state)

    # Assert: Verify the result
    assert result == expected

Full Example Test File
python

# tests/unit/test_example.py
"""
Example test file showing best practices.
"""

import json
from unittest.mock import patch

import pytest
import networkx as nx

# conftest.py puts the project root on sys.path, so plain imports work
from scrapLog import (
    ProcessingState,
    extract_affiliation_from_email,
    parse_time_name_email_affiliation,
    load_email_aggregation_config,
)


# FIXTURES: Reusable test data
@pytest.fixture
def state():
    """A fresh ProcessingState for each test (no shared globals)."""
    return ProcessingState()


# BASIC TESTS
def test_extract_affiliation_from_email(state):
    """The affiliation is the organisation part of the email domain."""
    result = extract_affiliation_from_email("user@google.com", state)
    assert result == "google"


def test_invalid_email_returns_none(state):
    """Invalid input returns None (callers skip the record); it does not raise."""
    assert extract_affiliation_from_email("not-an-email", state) is None
    assert extract_affiliation_from_email("", state) is None
    assert extract_affiliation_from_email(None, state) is None


# PARAMETERIZED TESTS (multiple inputs)
@pytest.mark.parametrize("email,expected", [
    ("user@google.com", "google"),
    ("dev@us.ibm.com", "ibm"),            # subdomain is skipped
    ("eng@alumni.mit.edu", "mit"),
    ("someone@company.co.uk", "company"), # second-level country domain
    ("user@domain?", "domain"),           # trailing '?' is stripped
])
def test_affiliation_extraction(state, email, expected):
    """Test multiple email cases."""
    assert extract_affiliation_from_email(email, state) == expected


# PARSING A GIT LOG HEADER LINE
def test_parse_time_name_email_affiliation(state):
    """A '==name;email;date==' line is split into its parts."""
    line = "==Jane Doe;jane@google.com;Wed Apr 3 20:54:06 2024 -0700=="
    result = parse_time_name_email_affiliation(line, state)
    assert result == ("Wed Apr 3 20:54:06 2024 -0700", "Jane Doe",
                      "jane@google.com", "google")


# TESTS WITH MOCKING
def test_parse_uses_affiliation_extractor(state):
    """Replace a collaborator to test one function in isolation."""
    with patch("scrapLog.extract_affiliation_from_email", return_value="acme") as mock_extract:
        line = "==Jane Doe;jane@google.com;Wed Apr 3 20:54:06 2024 -0700=="
        result = parse_time_name_email_affiliation(line, state)

    assert result[3] == "acme"
    mock_extract.assert_called_once_with("jane@google.com", state)


# TESTS USING FILES (pytest's tmp_path is cleaned up for you)
def test_load_email_aggregation_config(tmp_path):
    config_file = tmp_path / "aggregation.json"
    config_file.write_text(json.dumps({"ibm": "ibm", "google": "google"}))

    assert load_email_aggregation_config(str(config_file)) == {"ibm": "ibm", "google": "google"}


# TESTING EXPECTED EXITS / EXCEPTIONS
def test_invalid_config_json_exits(tmp_path):
    """Invalid JSON makes the loader call sys.exit(1)."""
    config_file = tmp_path / "broken.json"
    config_file.write_text("{not valid json")

    with pytest.raises(SystemExit) as exc_info:
        load_email_aggregation_config(str(config_file))
    assert exc_info.value.code == 1


# CONFIGURING BEHAVIOUR THROUGH STATE (instead of patching module globals)
def test_aggregation_config_on_state(state):
    state.email_aggregation_config = {"ibm": "ibm"}
    state.verbose_mode = True
    assert extract_affiliation_from_email("user@us.ibm.com", state) == "ibm"


# USING A SHARED FIXTURE FROM conftest.py
def test_sample_network_fixture(sample_individual_network):
    G = sample_individual_network
    assert isinstance(G, nx.Graph)
    assert G.nodes["dev1"]["affiliation"] == "Apple"

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

import pytest
from scrapLog import load_email_aggregation_config

def test_invalid_config_exits(tmp_path):
    """Invalid JSON in the aggregation config makes scrapLog exit with code 1."""
    config_file = tmp_path / "broken.json"
    config_file.write_text("{not valid json")

    with pytest.raises(SystemExit) as exc_info:
        load_email_aggregation_config(str(config_file))

    # Check the exit code
    assert exc_info.value.code == 1

🔍 Common Test Patterns
Configuring Behaviour with ProcessingState
python

# scrapLog keeps its settings (verbose/debug modes, filters, aggregation
# config) on a ProcessingState object instead of module-level globals.
# Build a fresh state per test and set only what you need.
from scrapLog import ProcessingState, extract_affiliation_from_email

def test_with_custom_state():
    state = ProcessingState()
    state.verbose_mode = True
    state.email_aggregation_config = {"ibm": "ibm"}

    result = extract_affiliation_from_email("user@us.ibm.com", state)
    assert result == "ibm"

Testing File I/O Operations
python

import json
from scrapLog import load_email_aggregation_config

def test_read_config_file(tmp_path):
    """Test reading the email aggregation config (a JSON file)."""
    # tmp_path is a pytest fixture: a fresh directory, cleaned up for you
    config_file = tmp_path / "aggregation.json"
    config_file.write_text(json.dumps({"google": "google"}))

    result = load_email_aggregation_config(str(config_file))
    assert result["google"] == "google"

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
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

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
python -m pytest tests/unit/test_parsing.py::test_specific --pdb

📊 Test Coverage
Generate Coverage Reports
bash


# Check that mocks work
pytest tests/ -k "test_main" -v


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
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from scrapLog import function_name

# For utils modules
from utils.validators import validate_git_email

# For console/logger helpers (utils/)
from utils.unified_logger import logger
from utils.unified_console import console

Mocking Patterns
python

from unittest.mock import patch, mock_open

# Replace a function scrapLog calls (patch where it is *used*)
with patch('scrapLog.extract_affiliation_from_email', return_value="acme") as mock_extract:
    result = parse_time_name_email_affiliation(line, state)
    mock_extract.assert_called_once()

# Same thing with the pytest-mock "mocker" fixture
def test_with_mocker(mocker):
    mocker.patch('scrapLog.extract_affiliation_from_email', return_value="acme")
    ...

# Mock file operations
with patch('builtins.open', mock_open(read_data='{"ibm": "ibm"}')):
    config = load_email_aggregation_config("any/path.json")

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

Problem: State leaking between tests

Solution: Never share a ProcessingState between tests; create a new one per test with a fixture:
python

import pytest
from scrapLog import ProcessingState

@pytest.fixture
def state():
    return ProcessingState()

def test_something(state):
    state.email_filtering_mode = True
    # Your test code

Problem: Tests leaving temporary files

Solution: Use pytest's built-in tmp_path fixture:
python

def test_writes_output(tmp_path):
    out_file = tmp_path / "network.graphml"
    # ... code under test writes to out_file ...
    assert out_file.exists()
    # tmp_path is removed by pytest, nothing left behind

📚 Additional Resources
Pytest Documentation

    Official pytest documentation

    pytest-mock plugin

    pytest-cov plugin

Python Testing

    unittest.mock documentation

    Test-driven development with pytest

Project-Specific

    Check existing tests in tests/unit/ directory for examples

    Look at function signatures in scrapLog.py to understand what to test

    Use print() or console.print() for debugging test execution