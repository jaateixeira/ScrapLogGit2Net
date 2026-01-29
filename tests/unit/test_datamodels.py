import pytest
from pytest_mock import mocker

from pathlib import Path
from datetime import datetime


from datamodels import GitEmail, GitName, GitCommitBlock, Repository


# FIXTURES --------------------------------------------------------------------
@pytest.fixture
def valid_commit_data():
    """Fixture providing valid commit data."""
    return {
        'hash': 'abc123',
        'author': GitName("Valid Name"),
        'email': GitEmail("valid@example.com"),
        'timestamp': datetime.now(),
        'message': 'Commit message',
        'files': [Path('file.txt')]
    }


@pytest.fixture
def sample_commit_block(valid_commit_data):
    """Fixture for a sample commit block."""
    return GitCommitBlock(**valid_commit_data)


# GitEmail TESTS --------------------------------------------------------------
def test_gitemail_validation_called(mocker):
    """Test utils validator is properly called."""
    # Arrange
    mock_validate = mocker.patch('utils.validators.validate_git_email')
    mock_validate.return_value = (True, "")

    # Act
    email = GitEmail("test@example.com")

    # Assert
    mock_validate.assert_called_once_with("test@example.com")


def test_gitemail_invalid_email_raises():
    """Test invalid emails raise ValueError."""
    with pytest.raises(ValueError, match="Invalid git email"):
        GitEmail("invalid-email")


def test_gitemail_equality():
    """Test GitEmail equality comparison."""
    email1 = GitEmail("test@example.com")
    email2 = GitEmail("test@example.com")
    email3 = GitEmail("other@example.com")

    assert email1 == email2
    assert email1 != email3


def test_gitemail_hash():
    """Test GitEmail hashing."""
    email1 = GitEmail("test@example.com")
    email2 = GitEmail("test@example.com")

    assert hash(email1) == hash(email2)


# GitName TESTS ---------------------------------------------------------------
def test_gitname_validation_called(mocker):
    """Test name validation integration."""
    mock_validate = mocker.patch('utils.validators.validate_git_name')
    mock_validate.return_value = (True, "")

    name = GitName("Valid Name")

    mock_validate.assert_called_once_with("Valid Name")


def test_gitname_str_repr():
    """Test GitName string representation."""
    name = GitName("John Doe")
    assert str(name) == "John Doe"
    assert "John Doe" in repr(name)


# GitCommitBlock TESTS --------------------------------------------------------
def test_commit_block_from_raw_validation(mocker):
    """Test full block validation in factory method."""
    mock_validate = mocker.patch('utils.validators.validate_git_commit_block')
    mock_validate.return_value = (True, "")

    commit = GitCommitBlock.from_raw("raw log")

    mock_validate.assert_called_once()


def test_commit_block_path_conversion(valid_commit_data):
    """Test string paths are converted to Path objects."""
    # Create commit with string paths
    commit = GitCommitBlock(**{
        **valid_commit_data,
        'files': ['string_path.txt', 'another/file.py']
    })

    # All files should be Path objects
    for file_path in commit.files:
        assert isinstance(file_path, Path)


def test_commit_block_attributes(sample_commit_block):
    """Test commit block has correct attributes."""
    assert sample_commit_block.hash == 'abc123'
    assert sample_commit_block.author.name == "Valid Name"
    assert sample_commit_block.email.email == "valid@example.com"
    assert len(sample_commit_block.files) == 1


def test_commit_block_str_representation(sample_commit_block):
    """Test string representation of commit block."""
    representation = str(sample_commit_block)
    assert "abc123" in representation
    assert "Valid Name" in representation
    assert "Commit message" in representation


# Repository TESTS ------------------------------------------------------------
def test_repository_path_validation_valid(mocker):
    """Test repository path validation with valid path."""
    mock_exists = mocker.patch('pathlib.Path.exists')
    mock_exists.return_value = True

    repo = Repository("/valid/path", "myrepo")

    assert repo.name == "myrepo"
    assert str(repo.path) == "/valid/path"


def test_repository_path_validation_invalid(mocker):
    """Test repository path validation raises error for invalid path."""
    mock_exists = mocker.patch('pathlib.Path.exists')
    mock_exists.return_value = False

    with pytest.raises(ValueError, match="does not exist"):
        Repository("/invalid/path", "repo")


# PARAMETRIZED TESTS ----------------------------------------------------------
@pytest.mark.parametrize("email_input,expected_valid", [
    ("user@example.com", True),
    ("dev@company.co.uk", True),
    ("invalid-email", False),
    ("", False),
    ("@nodomain.com", False),
])
def test_gitemail_validation_parametrized(email_input, expected_valid, mocker):
    """Parametrized test for email validation."""
    mock_validate = mocker.patch('utils.validators.validate_git_email')

    if expected_valid:
        mock_validate.return_value = (True, "")
        email = GitEmail(email_input)
        assert email.email == email_input
    else:
        mock_validate.return_value = (False, "Invalid email")
        with pytest.raises(ValueError):
            GitEmail(email_input)


@pytest.mark.parametrize("name_input,expected_valid", [
    ("John Doe", True),
    ("Jane Smith", True),
    ("", False),
    ("   ", False),
])
def test_gitname_validation_parametrized(name_input, expected_valid, mocker):
    """Parametrized test for name validation."""
    mock_validate = mocker.patch('utils.validators.validate_git_name')

    if expected_valid:
        mock_validate.return_value = (True, "")
        name = GitName(name_input)
        assert name.name == name_input
    else:
        mock_validate.return_value = (False, "Invalid name")
        with pytest.raises(ValueError):
            GitName(name_input)


@pytest.mark.parametrize("email1,email2,expected_equal", [
    ("test@example.com", "test@example.com", True),
    ("test@example.com", "TEST@example.com", False),  # Case sensitive
    ("a@b.com", "x@y.com", False),
])
def test_gitemail_equality_parametrized(email1, email2, expected_equal, mocker):
    """Parametrized test for email equality."""
    mocker.patch('utils.validators.validate_git_email', return_value=(True, ""))

    email_obj1 = GitEmail(email1)
    email_obj2 = GitEmail(email2)

    if expected_equal:
        assert email_obj1 == email_obj2
    else:
        assert email_obj1 != email_obj2


# GROUPING TESTS WITH MARKS ---------------------------------------------------
@pytest.mark.datamodel
def test_all_datamodels_have_repr():
    """Test that all data models have proper string representations."""
    mocker.patch('utils.validators.validate_git_email', return_value=(True, ""))
    mocker.patch('utils.validators.validate_git_name', return_value=(True, ""))

    email = GitEmail("test@example.com")
    name = GitName("Test Name")

    assert repr(email) is not None
    assert repr(name) is not None
    assert str(email) is not None
    assert str(name) is not None


@pytest.mark.slow
def test_large_file_list():
    """Test commit block with many files (marked as slow)."""
    mocker.patch('utils.validators.validate_git_email', return_value=(True, ""))
    mocker.patch('utils.validators.validate_git_name', return_value=(True, ""))

    # Create commit with many files
    many_files = [f"file_{i}.txt" for i in range(1000)]
    commit = GitCommitBlock(
        hash="xyz789",
        author=GitName("Developer"),
        email=GitEmail("dev@company.com"),
        timestamp=datetime.now(),
        message="Massive commit",
        files=many_files
    )

    assert len(commit.files) == 1000
    assert all(isinstance(f, Path) for f in commit.files)


# USING unittest.mock directly (if preferred over mocker) ----------------------
from unittest.mock import patch


def test_gitemail_with_unittest_mock():
    """Example using unittest.mock directly."""
    with patch('utils.validators.validate_git_email') as mock_validate:
        mock_validate.return_value = (True, "")

        email = GitEmail("test@example.com")

        mock_validate.assert_called_once_with("test@example.com")