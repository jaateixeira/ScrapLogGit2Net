import unittest
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datamodels import GitEmail, GitName, GitCommitBlock, Repository

class TestGitEmail(unittest.TestCase):
    @patch('utils.validators.validate_git_email')
    def test_validation_called(self, mock_validate):
        """Test utils validator is properly called"""
        mock_validate.return_value = (True, "")
        email = GitEmail("test@example.com")
        mock_validate.assert_called_once_with("test@example.com")
    
    def test_invalid_email_raises(self):
        """Test invalid emails raise ValueError"""
        with self.assertRaises(ValueError):
            GitEmail("invalid-email")

class TestGitName(unittest.TestCase):
    @patch('utils.validators.validate_git_name')
    def test_validation_called(self, mock_validate):
        """Test name validation integration"""
        mock_validate.return_value = (True, "")
        name = GitName("Valid Name")
        mock_validate.assert_called_once_with("Valid Name")

class TestGitCommitBlock(unittest.TestCase):
    def setUp(self):
        self.valid_data = {
            'hash': 'abc123',
            'author': GitName("Valid Name"),
            'email': GitEmail("valid@example.com"),
            'timestamp': datetime.now(),
            'message': 'Commit message',
            'files': [Path('file.txt')]
        }
    
    @patch('utils.validators.validate_git_commit_block')
    def test_from_raw_validation(self, mock_validate):
        """Test full block validation in factory method"""
        mock_validate.return_value = (True, "")
        commit = GitCommitBlock.from_raw("raw log")
        mock_validate.assert_called_once()
    
    def test_path_conversion(self):
        """Test string paths are converted to Path objects"""
        commit = GitCommitBlock(**{
            **self.valid_data,
            'files': ['string_path.txt']  # Should convert to Path
        })
        self.assertIsInstance(commit.files[0], Path)

class TestRepository(unittest.TestCase):
    @patch('pathlib.Path.exists')
    def test_path_validation(self, mock_exists):
        """Test repository path validation"""
        mock_exists.return_value = True
        repo = Repository("/valid/path", "repo")
        self.assertEqual(repo.name, "repo")
        
        mock_exists.return_value = False
        with self.assertRaises(ValueError):
            Repository("/invalid/path", "repo")

if __name__ == "__main__":
    unittest.main()
