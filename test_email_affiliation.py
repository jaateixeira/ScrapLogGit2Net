import unittest
import sys
from io import StringIO
from contextlib import redirect_stdout

from scrapLog import getAffiliationFromEmail  # Replace with actual import


class TestGetAffiliationFromEmail(unittest.TestCase):
    def setUp(self):
        # Backup globals
        self.original_debug = globals().get('DEBUG_MODE', 0)
        self.original_filter_mode = globals().get('EMAIL_FILTERING_MODE', 0)
        self.original_filter_list = globals().get('list_of_emails_to_filter', [])
        self.original_ibm_domains = globals().get('ibm_email_domains_prefix', [])

        # Set test defaults
        global DEBUG_MODE, EMAIL_FILTERING_MODE, list_of_emails_to_filter, ibm_email_domains_prefix
        DEBUG_MODE = 0
        EMAIL_FILTERING_MODE = 0
        list_of_emails_to_filter = []
        ibm_email_domains_prefix = ['us', 'br', 'linux.vnet', 'zurich']

    def tearDown(self):
        # Restore globals
        global DEBUG_MODE, EMAIL_FILTERING_MODE, list_of_emails_to_filter, ibm_email_domains_prefix
        DEBUG_MODE = self.original_debug
        EMAIL_FILTERING_MODE = self.original_filter_mode
        list_of_emails_to_filter = self.original_filter_list
        ibm_email_domains_prefix = self.original_ibm_domains

    def test_normal_email(self):
        self.assertEqual(getAffiliationFromEmail('user@apolinex.com'), 'apolinex')
        self.assertEqual(getAffiliationFromEmail('name@university-edu.org'), 'university-edu')

    def test_ibm_domains(self):
        global ibm_email_domains_prefix
        test_cases = [
            ('user@us.ibm.com', 'ibm'),
            ('name@linux.vnet.ibm.com', 'ibm'),
            ('test@br.ibm.com', 'ibm')
        ]
        for email, expected in test_cases:
            self.assertEqual(getAffiliationFromEmail(email), expected)

    def test_invalid_ibm_domain(self):
        global ibm_email_domains_prefix
        with self.assertRaises(SystemExit):
            getAffiliationFromEmail('user@invalid.ibm.com')

    def test_email_with_question_mark(self):
        self.assertEqual(getAffiliationFromEmail('user@domain?'), 'domain')

    def test_filtered_emails(self):
        global EMAIL_FILTERING_MODE, list_of_emails_to_filter
        EMAIL_FILTERING_MODE = 1
        list_of_emails_to_filter = ['spam@example.com']

        self.assertEqual(
            getAffiliationFromEmail('spam@example.com'),
            'filtered - included in file passed with -f argument'
        )

    def test_invalid_email_format(self):
        with self.assertRaises(SystemExit):
            getAffiliationFromEmail('not-an-email')

    def test_debug_output(self):
        global DEBUG_MODE
        DEBUG_MODE = 1

        with redirect_stdout(StringIO()) as output:
            getAffiliationFromEmail('test@domain.com')
            self.assertIn('getAffiliationFromEmail(test@domain.com)', output.getvalue())

    def test_empty_email(self):
        with self.assertRaises(SystemExit):
            getAffiliationFromEmail('')


if __name__ == '__main__':
    unittest.main()