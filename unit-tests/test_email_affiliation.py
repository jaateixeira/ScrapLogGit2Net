import unittest
import sys
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import print as rprint

# Import your function (replace with actual import)
from scrapLog import getAffiliationFromEmail

console = Console(record=True)  # Enable recording for full output capture


class VerboseTestResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_table = Table(title="Test Results", show_header=True, header_style="bold magenta")
        self.test_table.add_column("Status", width=8)
        self.test_table.add_column("Test Case", style="cyan")
        self.test_table.add_column("Input")
        self.test_table.add_column("Expected")
        self.test_table.add_column("Actual", style="red")

    def addSuccess(self, test):
        super().addSuccess(test)
        self.test_table.add_row(
            "[green]✓ PASS[/green]",
            test._testMethodName.replace("_", " ").title(),
            self._get_test_input(test),
            self._get_expected(test),
            self._get_actual(test)
        )

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.test_table.add_row(
            "[red]✗ FAIL[/red]",
            test._testMethodName.replace("_", " ").title(),
            self._get_test_input(test),
            self._get_expected(test),
            self._get_actual(test, err)
        )

    def addError(self, test, err):
        super().addError(test, err)
        self.test_table.add_row(
            "[bold red]⚡ ERROR[/bold red]",
            test._testMethodName.replace("_", " ").title(),
            self._get_test_input(test),
            self._get_expected(test),
            str(err[1])
        )

    def _get_test_input(self, test):
        # Extract test input from docstring or method name
        return getattr(test, 'test_input', test._testMethodName.split('_')[-1])

    def _get_expected(self, test):
        return getattr(test, 'expected_output', 'N/A')

    def _get_actual(self, test, err=None):
        if err:
            return str(err[1])
        return getattr(test, 'actual_output', '[green]Matched[/green]')

    def printErrors(self):
        console.print()
        console.print(Panel.fit(self.test_table, title="[bold]Detailed Test Results[/bold]"))

        # Show failure details
        if self.failures:
            console.print(Panel.fit("\n".join(
                f"[red]{test._testMethodName}[/red]: {err}"
                for test, err in self.failures
            ), title="[bold red]Failure Details[/bold red]"))


class TestGetAffiliationFromEmail(unittest.TestCase):
    """Comprehensive tests for email affiliation extraction"""

    @classmethod
    def setUpClass(cls):
        console.rule("[bold blue]📋 Starting Email Affiliation Test Suite[/bold blue]")
        cls.original_globals = {
            'DEBUG_MODE': globals().get('DEBUG_MODE', 0),
            'EMAIL_FILTERING_MODE': globals().get('EMAIL_FILTERING_MODE', 0),
            'list_of_emails_to_filter': globals().get('list_of_emails_to_filter', []),
            'ibm_email_domains_prefix': globals().get('ibm_email_domains_prefix', [])
        }

    def setUp(self):
        """Initialize test environment"""
        global DEBUG_MODE, EMAIL_FILTERING_MODE, list_of_emails_to_filter, ibm_email_domains_prefix
        DEBUG_MODE = 0
        EMAIL_FILTERING_MODE = 0
        list_of_emails_to_filter = []
        ibm_email_domains_prefix = ['us', 'br', 'linux.vnet', 'zurich']

    def tearDown(self):
        """Clean up after each test"""
        global DEBUG_MODE, EMAIL_FILTERING_MODE, list_of_emails_to_filter, ibm_email_domains_prefix
        for k, v in self.original_globals.items():
            globals()[k] = v

    # --- Test Cases ---
    def test_normal_email(self):
        """Standard email formats"""
        self.test_input = "user@apolinex.com"
        self.expected_output = "apolinex"
        self.actual_output = getAffiliationFromEmail(self.test_input)
        self.assertEqual(self.actual_output, self.expected_output)

    def test_hyphenated_domain(self):
        """Domains with hyphens"""
        self.test_input = "name@university-edu.org"
        self.expected_output = "university-edu"
        self.assertEqual(getAffiliationFromEmail(self.test_input), self.expected_output)

    def test_valid_ibm_domains(self):
        """Valid IBM subdomains"""
        test_cases = [
            ("user@us.ibm.com", "ibm"),
            ("name@linux.vnet.ibm.com", "ibm"),
            ("test@br.ibm.com", "ibm")
        ]
        for email, expected in test_cases:
            with self.subTest(email=email):
                self.test_input = email
                self.expected_output = expected
                self.assertEqual(getAffiliationFromEmail(email), expected)

    def test_invalid_ibm_domain(self):
        """Invalid IBM domains should exit"""
        self.test_input = "user@invalid.ibm.com"
        with self.assertRaises(SystemExit):
            getAffiliationFromEmail(self.test_input)

    def test_email_with_question_mark(self):
        """Emails ending with ?"""
        self.test_input = "user@domain?"
        self.expected_output = "domain"
        self.assertEqual(getAffiliationFromEmail(self.test_input), self.expected_output)

    def test_filtered_emails(self):
        """Email filtering mode"""
        global EMAIL_FILTERING_MODE, list_of_emails_to_filter
        EMAIL_FILTERING_MODE = 1
        list_of_emails_to_filter = ['spam@example.com']

        self.test_input = "spam@example.com"
        self.expected_output = "filtered - included in file passed with -f argument"
        self.assertEqual(getAffiliationFromEmail(self.test_input), self.expected_output)

    def test_invalid_email_format(self):
        """Completely invalid formats"""
        self.test_input = "not-an-email"
        with self.assertRaises(SystemExit):
            getAffiliationFromEmail(self.test_input)

    def test_empty_email(self):
        """Empty string input"""
        self.test_input = ""
        with self.assertRaises(SystemExit):
            getAffiliationFromEmail(self.test_input)

    @classmethod
    def tearDownClass(cls):
        """Print final summary"""
        console.print()
        console.rule("[bold green]✅ Test Suite Completed[/bold green]")
        console.save_html("test_results.html", clear=False)
        console.save_text("test_results.txt", clear=False)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestGetAffiliationFromEmail)
    runner = unittest.TextTestRunner(resultclass=VerboseTestResult, verbosity=2)
    result = runner.run(suite)
    sys.exit(not result.wasSuccessful())