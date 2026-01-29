import pytest
import sys
from unittest.mock import patch, MagicMock
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import print as rprint

# Import your function (replace with actual import)
# Note: You'll need to handle the import based on your project structure
try:
    from scrapLog import getAffiliationFromEmail
except ImportError:
    # Fallback for testing
    import sys
    import os

    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from scrapLog import getAffiliationFromEmail

console = Console(record=True)


# Pytest fixtures for setup and teardown
@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment before each test."""
    # Save original globals
    original_globals = {
        'DEBUG_MODE': globals().get('DEBUG_MODE', 0),
        'EMAIL_FILTERING_MODE': globals().get('EMAIL_FILTERING_MODE', 0),
        'list_of_emails_to_filter': globals().get('list_of_emails_to_filter', []),
        'ibm_email_domains_prefix': globals().get('ibm_email_domains_prefix', [])
    }

    # Set defaults
    globals()['DEBUG_MODE'] = 0
    globals()['EMAIL_FILTERING_MODE'] = 0
    globals()['list_of_emails_to_filter'] = []
    globals()['ibm_email_domains_prefix'] = ['us', 'br', 'linux.vnet', 'zurich']

    yield

    # Restore original globals
    for k, v in original_globals.items():
        globals()[k] = v


@pytest.fixture(scope="session", autouse=True)
def print_test_banner():
    """Print test suite banner at start and end."""
    console.rule("[bold blue]📋 Starting Email Affiliation Test Suite[/bold blue]")
    yield
    console.print()
    console.rule("[bold green]✅ Test Suite Completed[/bold green]")
    console.save_html("test_results.html", clear=False)
    console.save_text("test_results.txt", clear=False)


# Test functions (no classes needed!)
def test_normal_email():
    """Standard email formats"""
    email = "user@apolinex.com"
    expected = "apolinex"
    result = getAffiliationFromEmail(email)
    assert result == expected


def test_hyphenated_domain():
    """Domains with hyphens"""
    email = "name@university-edu.org"
    expected = "university-edu"
    result = getAffiliationFromEmail(email)
    assert result == expected


# Use pytest.mark.parametrize for multiple test cases
@pytest.mark.parametrize("email,expected", [
    ("user@us.ibm.com", "ibm"),
    ("name@linux.vnet.ibm.com", "ibm"),
    ("test@br.ibm.com", "ibm"),
])
def test_valid_ibm_domains(email, expected):
    """Valid IBM subdomains"""
    result = getAffiliationFromEmail(email)
    assert result == expected


def test_invalid_ibm_domain():
    """Invalid IBM domains should exit"""
    email = "user@invalid.ibm.com"
    with pytest.raises(SystemExit):
        getAffiliationFromEmail(email)


def test_email_with_question_mark():
    """Emails ending with ?"""
    email = "user@domain?"
    expected = "domain"
    result = getAffiliationFromEmail(email)
    assert result == expected


def test_filtered_emails():
    """Email filtering mode"""
    # Set filtering mode
    globals()['EMAIL_FILTERING_MODE'] = 1
    globals()['list_of_emails_to_filter'] = ['spam@example.com']

    email = "spam@example.com"
    expected = "filtered - included in file passed with -f argument"
    result = getAffiliationFromEmail(email)
    assert result == expected


def test_invalid_email_format():
    """Completely invalid formats"""
    email = "not-an-email"
    with pytest.raises(SystemExit):
        getAffiliationFromEmail(email)


def test_empty_email():
    """Empty string input"""
    email = ""
    with pytest.raises(SystemExit):
        getAffiliationFromEmail(email)


# Using pytest-mock for mocking
def test_with_mocking(mocker):
    """Example using pytest-mock for mocking dependencies"""
    # Mock external dependencies if needed
    mock_external = mocker.patch('some_module.some_function')
    mock_external.return_value = "mocked_value"

    email = "test@example.com"
    result = getAffiliationFromEmail(email)
    # Your assertions here


# Advanced: Custom test output with rich
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook to create rich test reports."""
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call":
        if rep.failed:
            status = "[red]✗ FAIL[/red]"
        elif rep.passed:
            status = "[green]✓ PASS[/green]"
        else:
            status = "[yellow]SKIP[/yellow]"

        # You could create a rich table here similar to unittest version
        if hasattr(item, 'callspec'):
            test_input = str(item.callspec.params)
        else:
            test_input = item.name.replace("test_", "").replace("_", " ")

        # Create a simple test results table (simplified version)
        if rep.failed:
            console.print(f"{status} {item.name}: {rep.longreprtext}")


# Optional: Session-scoped table for summary
@pytest.fixture(scope="session")
def test_results_table():
    """Create a table to collect test results."""
    table = Table(title="Test Results", show_header=True, header_style="bold magenta")
    table.add_column("Status", width=8)
    table.add_column("Test Case", style="cyan")
    table.add_column("Input")
    table.add_column("Expected")
    table.add_column("Actual", style="red")
    return table


# Example of using the table fixture
def test_with_table_report(test_results_table):
    """Example test that adds to the results table."""
    email = "test@example.com"
    expected = "example"

    try:
        result = getAffiliationFromEmail(email)
        assert result == expected
        test_results_table.add_row(
            "[green]✓ PASS[/green]",
            "test_with_table_report",
            email,
            expected,
            "[green]Matched[/green]"
        )
    except Exception as e:
        test_results_table.add_row(
            "[red]✗ FAIL[/red]",
            "test_with_table_report",
            email,
            expected,
            str(e)
        )
        raise


# Run all tests with a custom session fixture
def pytest_sessionfinish(session, exitstatus):
    """Hook called after all tests are run."""
    # Print summary if we have a test_results_table
    for item in session.items:
        if hasattr(item.function, '__test_results_table__'):
            console.print()
            console.print(Panel.fit(
                item.function.__test_results_table__,
                title="[bold]Detailed Test Results[/bold]"
            ))
            break


# To run from command line, just use: pytest test_file.py
# But we can also add a main block for running directly
if __name__ == "__main__":
    # Run pytest programmatically
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))