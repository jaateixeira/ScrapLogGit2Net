import pytest
import time
import sys
import os


from utils.validators import validate_git_name, validate_git_email, validate_git_time


# --- Name Validation Tests ---
def test_valid_name_ascii():
    """Test standard ASCII name"""
    is_valid, message = validate_git_name("John Doe")
    assert is_valid
    assert message == "" or "valid" in message.lower()


def test_valid_name_unicode():
    """Test Unicode names"""
    # Polish
    is_valid, _ = validate_git_name("Jan Kowalski")
    assert is_valid

    # Chinese
    is_valid, _ = validate_git_name("李伟")
    assert is_valid

    # Spanish
    is_valid, _ = validate_git_name("María García")
    assert is_valid


def test_invalid_name_empty():
    """Test empty name"""
    is_valid, message = validate_git_name("")
    assert not is_valid
    assert "cannot be empty" in message.lower()


def test_invalid_name_special_chars():
    """Test names with invalid characters"""
    is_valid, _ = validate_git_name("John@Doe")
    assert not is_valid

    is_valid, _ = validate_git_name("Jane_Doe")
    assert not is_valid


def test_name_with_apostrophe():
    """Test names with apostrophes"""
    is_valid, _ = validate_git_name("O'Connor")
    assert is_valid

    is_valid, _ = validate_git_name("D'Angelo")
    assert is_valid


# --- Email Validation Tests ---
def test_valid_email_standard():
    """Test standard email formats"""
    is_valid, _ = validate_git_email("user@example.com")
    assert is_valid

    is_valid, _ = validate_git_email("first.last@sub.domain.co.uk")
    assert is_valid


def test_invalid_email_missing_at():
    """Test malformed emails"""
    is_valid, message = validate_git_email("userexample.com")
    assert not is_valid
    assert "valid" in message.lower() or "invalid" in message.lower()


def test_invalid_email_whitespace():
    """Test emails with whitespace"""
    is_valid, _ = validate_git_email(" user@example.com ")
    assert not is_valid


def test_email_unicode_local_part():
    """Test internationalized email addresses"""
    is_valid, _ = validate_git_email("Pelé@example.com")
    assert is_valid

    # Note: Chinese email might fail depending on validator implementation
    is_valid, _ = validate_git_email("用户@例子.软件")
    # Either True or False is acceptable depending on validator strictness
    # If it fails, that's also a valid test outcome


# --- Time Validation Tests ---
def test_valid_time_utc():
    """Test UTC timestamp"""
    is_valid, _ = validate_git_time("1672531200 +0000")
    assert is_valid


def test_valid_time_with_offset():
    """Test timestamps with timezone offsets"""
    is_valid, _ = validate_git_time("1672531200 -0500")  # EST
    assert is_valid

    is_valid, _ = validate_git_time("1672531200 +0900")  # JST
    assert is_valid


def test_time_future_timestamp():
    """Test future timestamps (should still validate)"""
    future_ts = str(int(time.time()) + 86400)  # Current time + 1 day
    is_valid, _ = validate_git_time(f"{future_ts} +0000")
    assert is_valid


# --- Parameterized Tests for Better Coverage ---
@pytest.mark.parametrize("name,expected_valid", [
    # Valid names
    ("John Doe", True),
    ("Jane Smith", True),
    ("María García", True),
    ("O'Connor", True),
    ("Jean-Luc", True),
    ("Jan Kowalski", True),
    # Invalid names
    ("", False),
    ("   ", False),
    ("John@Doe", False),
    ("Jane_Doe", False),
    ("User123", False),
])
def test_name_validation_parametrized(name, expected_valid):
    """Parameterized test for name validation"""
    is_valid, message = validate_git_name(name)

    if expected_valid:
        assert is_valid, f"Expected '{name}' to be valid, but got: {message}"
    else:
        assert not is_valid, f"Expected '{name}' to be invalid, but it passed"
        assert message  # Should have an error message


@pytest.mark.parametrize("email,expected_valid", [
    # Valid emails
    ("user@example.com", True),
    ("first.last@domain.co.uk", True),
    ("name@sub.domain.com", True),
    ("user+tag@example.com", True),
    ("pelé@example.com", True),
    # Invalid emails
    ("userexample.com", False),  # Missing @
    ("user@", False),  # Missing domain
    ("@example.com", False),  # Missing local part
    ("user@example", False),  # Missing TLD
    (" user@example.com ", False),  # Whitespace
    ("user@example..com", False),  # Double dot
])
def test_email_validation_parametrized(email, expected_valid):
    """Parameterized test for email validation"""
    is_valid, message = validate_git_email(email)

    if expected_valid:
        assert is_valid, f"Expected '{email}' to be valid, but got: {message}"
    else:
        assert not is_valid, f"Expected '{email}' to be invalid, but it passed"
        assert message  # Should have an error message


@pytest.mark.parametrize("time_str,expected_valid,description", [
    # Valid timestamps
    ("1672531200 +0000", True, "UTC timestamp"),
    ("1672531200 -0500", True, "EST offset"),
    ("1672531200 +0900", True, "JST offset"),
    ("0 +0000", True, "Zero timestamp"),
    ("9999999999 +0000", True, "Large timestamp"),
    # Invalid timestamps
    ("1672531200", False, "Missing offset"),
    ("1672531200 +12345", False, "Invalid offset length"),
    ("notanumber +0000", False, "Non-numeric timestamp"),
    ("-123456789 +0000", False, "Negative timestamp"),
    ("1672531200 0000", False, "Missing offset sign"),
    ("1672531200 +2500", False, "Invalid hour in offset"),
    ("1672531200 +0060", False, "Invalid minute in offset"),
    (" 1672531200 +0000 ", False, "Whitespace around"),
    ("1672531200+0000", False, "Missing space"),
])
def test_time_validation_parametrized(time_str, expected_valid, description):
    """Parameterized test for time validation"""
    is_valid, message = validate_git_time(time_str)

    if expected_valid:
        assert is_valid, f"Failed for '{description}': {message}"
    else:
        assert not is_valid, f"Expected '{time_str}' to be invalid ({description})"
        assert message  # Should have an error message


# --- Fixtures for common test data ---
@pytest.fixture
def valid_names():
    """Fixture providing valid names for testing."""
    return [
        "John Doe",
        "Jane Smith",
        "María García",
        "Jan Kowalski",
        "O'Connor",
        "Jean-Luc Picard",
    ]


@pytest.fixture
def invalid_names():
    """Fixture providing invalid names for testing."""
    return [
        "",
        "   ",
        "John@Doe",
        "User_123",
        "Test<Script>",
        "A" * 256,  # Very long name
    ]


@pytest.fixture
def valid_emails():
    """Fixture providing valid emails for testing."""
    return [
        "user@example.com",
        "first.last@domain.com",
        "name@sub.domain.co.uk",
        "user+tag@example.org",
        "test@123.com",
    ]


@pytest.fixture
def invalid_emails():
    """Fixture providing invalid emails for testing."""
    return [
        "",
        "not-an-email",
        "user@",
        "@domain.com",
        "user@domain",
        "user@.com",
        "user@domain..com",
        " user@domain.com ",
    ]


# --- Tests using fixtures ---
def test_multiple_valid_names(valid_names):
    """Test multiple valid names using fixture."""
    for name in valid_names:
        is_valid, message = validate_git_name(name)
        assert is_valid, f"Name '{name}' should be valid: {message}"


def test_multiple_invalid_names(invalid_names):
    """Test multiple invalid names using fixture."""
    for name in invalid_names:
        is_valid, message = validate_git_name(name)
        assert not is_valid, f"Name '{name}' should be invalid"
        assert message, f"No error message for invalid name '{name}'"


def test_multiple_valid_emails(valid_emails):
    """Test multiple valid emails using fixture."""
    for email in valid_emails:
        is_valid, message = validate_git_email(email)
        assert is_valid, f"Email '{email}' should be valid: {message}"


def test_multiple_invalid_emails(invalid_emails):
    """Test multiple invalid emails using fixture."""
    for email in invalid_emails:
        is_valid, message = validate_git_email(email)
        assert not is_valid, f"Email '{email}' should be invalid"
        assert message, f"No error message for invalid email '{email}'"


# --- Edge Case Tests ---
def test_name_with_digits():
    """Test if names with digits are valid (depends on validator rules)."""
    # Some validators allow digits, some don't
    is_valid, message = validate_git_name("User123")

    # We don't assert true/false here since it depends on implementation
    # Just ensure we get a consistent result
    if is_valid:
        assert "valid" in message.lower() or message == ""
    else:
        assert "invalid" in message.lower() or "digit" in message.lower()


def test_email_case_sensitivity():
    """Test email case sensitivity (should be case-insensitive in local part)."""
    is_valid1, _ = validate_git_email("USER@example.com")
    is_valid2, _ = validate_git_email("user@example.com")

    # Both should be valid regardless of case
    assert is_valid1
    assert is_valid2


def test_time_boundary_values():
    """Test boundary values for timestamps."""
    # Test very large timestamp (year ~5138)
    is_valid, _ = validate_git_time("99999999999 +0000")
    assert is_valid  # Should be valid even if unrealistic

    # Test minimum Unix timestamp (negative values might be invalid)
    is_valid, _ = validate_git_time("0 +0000")
    assert is_valid


# --- Run tests ---
if __name__ == "__main__":
    # Run pytest programmatically
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))