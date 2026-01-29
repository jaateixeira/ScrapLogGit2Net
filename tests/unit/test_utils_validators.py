import unittest
import time
from utils.validators import validate_git_name, validate_git_email, validate_git_time


class TestGitValidators(unittest.TestCase):
    # --- Name Validation Tests ---
    def test_valid_name_ascii(self):
        """Test standard ASCII name"""
        self.assertTrue(validate_git_name("John Doe")[0])

    def test_valid_name_unicode(self):
        """Test Unicode names"""
        self.assertTrue(validate_git_name("Jan Kowalski")[0])  # Polish
        self.assertTrue(validate_git_name("李伟")[0])  # Chinese
        self.assertTrue(validate_git_name("María García")[0])  # Spanish

    def test_invalid_name_empty(self):
        """Test empty name"""
        valid, msg = validate_git_name("")
        self.assertFalse(valid)
        self.assertIn("cannot be empty", msg)

    def test_invalid_name_special_chars(self):
        """Test names with invalid characters"""
        self.assertFalse(validate_git_name("John@Doe")[0])
        self.assertFalse(validate_git_name("Jane_Doe")[0])

    # --- Email Validation Tests ---
    def test_valid_email_standard(self):
        """Test standard email formats"""
        self.assertTrue(validate_git_email("user@example.com")[0])
        self.assertTrue(validate_git_email("first.last@sub.domain.co.uk")[0])

    def test_invalid_email_missing_at(self):
        """Test malformed emails"""
        valid, msg = validate_git_email("userexample.com")
        self.assertFalse(valid)
        self.assertIn("valid", msg.lower())

    def test_invalid_email_whitespace(self):
        """Test emails with whitespace"""
        self.assertFalse(validate_git_email(" user@example.com ")[0])

    # --- Time Validation Tests ---
    def test_valid_time_utc(self):
        """Test UTC timestamp"""
        self.assertTrue(validate_git_time("1672531200 +0000")[0])

    def test_valid_time_with_offset(self):
        """Test timestamps with timezone offsets"""
        self.assertTrue(validate_git_time("1672531200 -0500")[0])  # EST
        self.assertTrue(validate_git_time("1672531200 +0900")[0])  # JST

    def test_invalid_time_format(self):
        """Test malformed timestamps"""
        tests = [
            ("1672531200", "missing offset"),
            ("1672531200 +12345", "invalid offset"),
            ("notanumber +0000", "non-numeric timestamp"),
            ("-123456789 +0000", "negative timestamp"),
            ("1672531200 0000", "missing offset sign")
        ]

        for time_str, desc in tests:
            with self.subTest(desc=desc):
                valid, _ = validate_git_time(time_str)
                self.assertFalse(valid, f"Should fail: {desc}")

    # --- Edge Cases ---
    def test_name_with_apostrophe(self):
        """Test names with apostrophes"""
        self.assertTrue(validate_git_name("O'Connor")[0])
        self.assertTrue(validate_git_name("D'Angelo")[0])

    def test_email_unicode_local_part(self):
        """Test internationalized email addresses"""
        self.assertTrue(validate_git_email(" Pelé@example.com ")[0])
        self.assertTrue(validate_git_email("用户@例子.软件")[0])  # Chinese email

    def test_time_future_timestamp(self):
        """Test future timestamps (should still validate)"""
        future_ts = str(int(time.time()) + 86400)  # Current time + 1 day
        self.assertTrue(validate_git_time(f"{future_ts} +0000")[0])


if __name__ == "__main__":
    unittest.main()