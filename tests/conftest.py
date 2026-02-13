# tests/conftest.py
import sys
import os
import tempfile
from types import SimpleNamespace

import pytest
import networkx as nx

# Add the project root to sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'utils'))


print ("running conftest.py")
print (f"{sys.path=}")



# Ensure pytest-mock is available
pytest_plugins = ['pytest_mock']




@pytest.fixture
def sample_individual_network():
    """Create a sample network of individuals for testing."""
    G = nx.Graph()

    # Add individuals with affiliations
    G.add_node("dev1", email="dev1@apple.com", affiliation="Apple")
    G.add_node("dev2", email="dev2@apple.com", affiliation="Apple")
    G.add_node("dev3", email="dev3@nokia.com", affiliation="Nokia")
    G.add_node("dev4", email="dev4@nokia.com", affiliation="Nokia")
    G.add_node("dev5", email="dev5@google.com", affiliation="Google")
    G.add_node("isolated_dev", email="isolated@microsoft.com", affiliation="Microsoft")

    # Add edges (collaborations)
    G.add_edge("dev1", "dev3")  # Apple-Nokia collaboration
    G.add_edge("dev1", "dev4")  # Apple-Nokia collaboration
    G.add_edge("dev2", "dev3")  # Apple-Nokia collaboration
    G.add_edge("dev2", "dev4")  # Apple-Nokia collaboration
    G.add_edge("dev3", "dev5")  # Nokia-Google collaboration

    return G


@pytest.fixture
def network_with_isolates():
    """Create network with isolated nodes."""
    G = nx.Graph()

    G.add_node("dev1", affiliation="Apple")
    G.add_node("dev2", affiliation="Apple")
    G.add_node("isolated1", affiliation="IBM")
    G.add_node("isolated2", affiliation="IBM")

    G.add_edge("dev1", "dev2")

    return G


@pytest.fixture
def complex_network():
    """Create a more complex network for testing."""
    G = nx.Graph()

    # Multiple developers from multiple companies
    companies = ["Apple", "Nokia", "Google", "Microsoft", "Amazon"]

    # Add 5 developers per company
    for i, company in enumerate(companies):
        for j in range(5):
            dev_id = f"{company.lower()}_dev_{j}"
            G.add_node(dev_id, affiliation=company, email=f"{dev_id}@{company.lower()}.com")

    # Add inter-company collaborations
    # Apple-Nokia: 3 collaborations
    for i in range(3):
        G.add_edge(f"apple_dev_{i}", f"nokia_dev_{i}")

    # Apple-Google: 2 collaborations
    for i in range(2):
        G.add_edge(f"apple_dev_{i}", f"google_dev_{i}")

    # Nokia-Google: 1 collaboration
    G.add_edge("nokia_dev_0", "google_dev_0")

    # Microsoft-Amazon: 4 collaborations
    for i in range(4):
        G.add_edge(f"microsoft_dev_{i}", f"amazon_dev_{i}")

    return G


@pytest.fixture
def temp_graphml_file(sample_individual_network):
    """Create a temporary GraphML file for testing."""
    with tempfile.NamedTemporaryFile(suffix='.graphML', delete=False) as tmp:
        nx.write_graphml_lxml(sample_individual_network, tmp.name)
        yield tmp.name
    # Clean up
    if os.path.exists(tmp.name):
        os.unlink(tmp.name)


@pytest.fixture
def mock_visualization_script():
    """Mock the visualization script path."""
    return "/mock/path/to/viz.py"



@pytest.fixture
def processing_state():
    """Create a processing state with email aggregation config."""
    state = SimpleNamespace()
    state.verbose_mode = False
    state.email_filtering_mode = False
    state.emails_to_filter = set()

    # Set up email aggregation config
    state.email_aggregation_config = {
        "abo": "abo.fi",
        "mit": "MIT",
        "ibm": "IBM",
    }

    return state