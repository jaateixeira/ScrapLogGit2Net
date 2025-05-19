import pytest
from rich import print
from pathlib import Path

@pytest.fixture(scope="session")
def test_data_dir():
    return Path(__file__).parent / "fixtures"

@pytest.fixture
def sample_gitlog_path(test_data_dir):
    path = test_data_dir / "sample_gitlog.txt"
    print(f"\nUsing test gitlog from: {path}")
    return path

@pytest.fixture(autouse=True)
def reset_globals():
    """Reset global variables before each test"""
    from scraplog import (
        agreByFileContributors,
        agreByConnWSF,
        changeLogData,
        affiliations
    )
    
    original_values = {
        'agreByFileContributors': agreByFileContributors.copy(),
        'agreByConnWSF': agreByConnWSF.copy(),
        'changeLogData': changeLogData.copy(),
        'affiliations': affiliations.copy()
    }
    
    yield
    
    # Restore original values
    agreByFileContributors = original_values['agreByFileContributors']
    agreByConnWSF = original_values['agreByConnWSF']
    changeLogData = original_values['changeLogData']
    affiliations = original_values['affiliations']

