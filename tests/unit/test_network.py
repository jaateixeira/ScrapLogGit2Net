import pytest
from unittest.mock import patch, MagicMock
from rich.console import Console
from rich.panel import Panel
from pathlib import Path
import sys


try:
    from scrapLog import agregateByFileItsContributors, getContributorsConnectionsTuplesWSF
    # Also import any global variables the functions might use
    from scrapLog import changeLogData, agreByFileContributors
except ImportError:
    # If module-level imports fail, we'll handle it in tests
    pass

console = Console()


@pytest.fixture
def sample_changelog_data():
    """Fixture providing sample changelog data."""
    return [
        (("2023-01-01", "dev1@a.com", "a"), ["file1"]),
        (("2023-01-02", "dev2@b.com", "b"), ["file1", "file2"]),
        (("2023-01-03", "dev3@c.com", "c"), ["file2"])
    ]


def test_agregateByFileItsContributors(sample_changelog_data):
    """Test aggregation of contributors by file."""
    # Mock the global changeLogData
    with patch('scrapLog.changeLogData', sample_changelog_data):
        # Mock the global agreByFileContributors
        with patch('scrapLog.agreByFileContributors', {}) as mock_agre:
            # Call the function
            agregateByFileItsContributors()

            # Check results
            assert "file1" in mock_agre
            assert "file2" in mock_agre
            assert len(mock_agre["file1"]) == 2
            assert len(mock_agre["file2"]) == 2

            # Verify specific contributors
            assert "dev1@a.com" in mock_agre["file1"]
            assert "dev2@b.com" in mock_agre["file1"]
            assert "dev2@b.com" in mock_agre["file2"]
            assert "dev3@c.com" in mock_agre["file2"]


def test_agregateByFileItsContributors_with_rich_output(sample_changelog_data):
    """Test with rich console output."""
    with patch('scrapLog.changeLogData', sample_changelog_data):
        with patch('scrapLog.agreByFileContributors', {}) as mock_agre:
            agregateByFileItsContributors()

            # Create formatted output
            results = []
            for file, devs in mock_agre.items():
                results.append(f"{file}: {', '.join(sorted(devs))}")

            console.print(Panel.fit(
                "\n".join(results),
                title="File to Contributors Mapping",
                border_style="blue"
            ))

            # Verify assertions
            assert len(mock_agre) == 2
            assert set(mock_agre.keys()) == {"file1", "file2"}


def test_agregateByFileItsContributors_empty_data():
    """Test with empty changelog data."""
    with patch('scrapLog.changeLogData', []):
        with patch('scrapLog.agreByFileContributors', {}) as mock_agre:
            agregateByFileItsContributors()
            assert len(mock_agre) == 0  # Should be empty


def test_agregateByFileItsContributors_single_commit():
    """Test with single commit data."""
    single_data = [
        (("2023-01-01", "dev1@company.com", "company"), ["main.py", "utils.py"])
    ]

    with patch('scrapLog.changeLogData', single_data):
        with patch('scrapLog.agreByFileContributors', {}) as mock_agre:
            agregateByFileItsContributors()

            assert len(mock_agre) == 2
            assert "main.py" in mock_agre
            assert "utils.py" in mock_agre
            assert mock_agre["main.py"] == ["dev1@company.com"]
            assert mock_agre["utils.py"] == ["dev1@company.com"]


# Parameterized tests for different scenarios
@pytest.mark.parametrize("changelog_data,expected_files,expected_contributors", [
    # Test case 1: Basic
    ([
         (("2023-01-01", "dev1@a.com", "a"), ["file1"]),
         (("2023-01-02", "dev2@b.com", "b"), ["file1", "file2"]),
     ],
     ["file1", "file2"],
     {"file1": ["dev1@a.com", "dev2@b.com"], "file2": ["dev2@b.com"]}),

    # Test case 2: Same developer, multiple files
    ([
         (("2023-01-01", "dev@company.com", "company"), ["file1", "file2", "file3"]),
     ],
     ["file1", "file2", "file3"],
     {"file1": ["dev@company.com"], "file2": ["dev@company.com"], "file3": ["dev@company.com"]}),

    # Test case 3: Multiple developers, same file
    ([
         (("2023-01-01", "dev1@a.com", "a"), ["shared.py"]),
         (("2023-01-02", "dev2@b.com", "b"), ["shared.py"]),
         (("2023-01-03", "dev3@c.com", "c"), ["shared.py"]),
     ],
     ["shared.py"],
     {"shared.py": ["dev1@a.com", "dev2@b.com", "dev3@c.com"]}),
])
def test_agregateByFileItsContributors_parametrized(changelog_data, expected_files, expected_contributors):
    """Parameterized test for various scenarios."""
    with patch('scrapLog.changeLogData', changelog_data):
        with patch('scrapLog.agreByFileContributors', {}) as mock_agre:
            agregateByFileItsContributors()

            # Check all expected files are present
            assert set(mock_agre.keys()) == set(expected_files)

            # Check contributors for each file
            for file, expected_devs in expected_contributors.items():
                # Order might not matter, so compare sets
                assert set(mock_agre[file]) == set(expected_devs)


# Tests for getContributorsConnectionsTuplesWSF
def test_getContributorsConnectionsTuplesWSF_basic():
    """Test basic contributor connections."""
    # Setup mock data
    mock_agre_by_file = {
        "file1": ["dev1@a.com", "dev2@b.com", "dev3@c.com"],
        "file2": ["dev2@b.com", "dev3@c.com"],
        "file3": ["dev1@a.com"],
    }

    with patch('scrapLog.agreByFileContributors', mock_agre_by_file):
        # Call the function
        connections = getContributorsConnectionsTuplesWSF()

        # Should return list of tuples
        assert isinstance(connections, list)

        # Each connection should be a tuple
        if connections:
            for conn in connections:
                assert isinstance(conn, tuple)
                assert len(conn) == 3  # (dev1, dev2, file)


def test_getContributorsConnectionsTuplesWSF_single_contributor():
    """Test when files have only single contributor (no connections)."""
    mock_agre_by_file = {
        "file1": ["dev1@a.com"],
        "file2": ["dev2@b.com"],
    }

    with patch('scrapLog.agreByFileContributors', mock_agre_by_file):
        connections = getContributorsConnectionsTuplesWSF()

        # No connections should be created (self-connections are typically filtered)
        assert len(connections) == 0


def test_getContributorsConnectionsTuplesWSF_empty():
    """Test with empty contributor data."""
    with patch('scrapLog.agreByFileContributors', {}):
        connections = getContributorsConnectionsTuplesWSF()
        assert connections == []


# Integrated test: both functions together
def test_integrated_workflow(sample_changelog_data):
    """Test the full workflow from aggregation to connection extraction."""
    # Mock the first global
    with patch('scrapLog.changeLogData', sample_changelog_data):
        with patch('scrapLog.agreByFileContributors', {}) as mock_agre:
            # Step 1: Aggregate
            agregateByFileItsContributors()

            # Verify aggregation
            assert len(mock_agre) == 2

            # Step 2: Get connections
            connections = getContributorsConnectionsTuplesWSF()

            # Verify connections were created
            assert len(connections) > 0

            # Each connection should be between different developers
            for dev1, dev2, file in connections:
                assert dev1 != dev2
                assert file in ["file1", "file2"]


# Using pytest-mock (if installed)
def test_with_pytest_mock(mocker, sample_changelog_data):
    """Example using pytest-mock fixture."""
    # Mock the globals
    mock_change_log = mocker.patch('scrapLog.changeLogData', sample_changelog_data)
    mock_agre = mocker.patch('scrapLog.agreByFileContributors', {})

    # Call function
    agregateByFileItsContributors()

    # Verify
    assert len(mock_agre) == 2
    assert mock_change_log is not None


# Optional: Test with actual module imports
def test_with_module_import():
    """Test that we can import the module."""
    try:
        import scrapLog
        assert hasattr(scrapLog, 'agregateByFileItsContributors')
        assert hasattr(scrapLog, 'getContributorsConnectionsTuplesWSF')
    except ImportError as e:
        pytest.skip(f"Could not import scrapLog: {e}")


# Run tests with: pytest test_file.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
