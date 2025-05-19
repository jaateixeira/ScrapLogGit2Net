import pytest
from rich.console import Console
from rich.panel import Panel

from pathlib import Path
import sys 

sys.path.insert(0, str(Path(__file__).parent.parent))


from scraplog import agregateByFileItsContributors, getContributorsConnectionsTuplesWSF

console = Console()

@pytest.fixture
def sample_changelog_data():
    return [
        (("2023-01-01", "dev1@a.com", "a"), ["file1"]),
        (("2023-01-02", "dev2@b.com", "b"), ["file1", "file2"]),
        (("2023-01-03", "dev3@c.com", "c"), ["file2"])
    ]

def test_agregateByFileItsContributors(sample_changelog_data):
    global agreByFileContributors
    agreByFileContributors = {}
    
    # Need to mock the global changeLogData
    original_data = globals().get('changeLogData', [])
    globals()['changeLogData'] = sample_changelog_data
    
    agregateByFileItsContributors()
    
    results = []
    for file, devs in agreByFileContributors.items():
        results.append(f"{file}: {', '.join(devs)}")
    
    console.print(Panel.fit(
        "\n".join(results),
        title="File to Contributors Mapping",
        border_style="blue"
    ))
    
    assert "file1" in agreByFileContributors
    assert len(agreByFileContributors["file1"]) == 2
    
    # Restore original data
    globals()['changeLogData'] = original_data
