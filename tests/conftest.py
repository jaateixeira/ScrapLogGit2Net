# tests/conftest.py
import sys
import os
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
