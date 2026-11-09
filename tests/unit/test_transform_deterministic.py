"""
The nofi -> nofo transformer must give byte-identical output for the same input.

Organization pairs are kept in frozensets; the order of a frozenset of strings
changes between Python runs (hash randomization), which used to change the
edge orientation and node order in the output file.

Run with:
    pytest tests/unit/test_transform_deterministic.py -v
"""

import os
import subprocess
import sys
from pathlib import Path

import networkx as nx

PROJECT_ROOT = Path(__file__).resolve().parents[2]

ORGANIZATIONS = ["google", "ibm", "intel", "nvidia", "amd", "arm"]


def write_individual_network(path):
    """Two developers per organization, linked across organizations in a ring
    and a star, so there are several inter-organizational edges."""
    graph = nx.Graph()
    for org in ORGANIZATIONS:
        for i in (1, 2):
            graph.add_node(f"dev{i}@{org}.com", affiliation=org)
    for a, b in zip(ORGANIZATIONS, ORGANIZATIONS[1:] + ORGANIZATIONS[:1]):
        graph.add_edge(f"dev1@{a}.com", f"dev2@{b}.com")
    for org in ORGANIZATIONS[1:]:
        graph.add_edge("dev1@google.com", f"dev1@{org}.com")
    graph.add_edge("dev1@ibm.com", "dev2@ibm.com")  # intra-organizational, ignored
    nx.write_graphml(graph, path)


def transform_with_hash_seed(input_file, output_dir, seed):
    output = output_dir / f"seed{seed}"
    env = {**os.environ, "PYTHONHASHSEED": str(seed), "MPLBACKEND": "Agg"}
    subprocess.run(
        [sys.executable, "-m", "scraplog.analysis.transform_nofi_to_nofo", str(input_file), "-o", str(output)],
        cwd=output_dir, env={**env, "PYTHONPATH": str(PROJECT_ROOT)},
        capture_output=True, text=True, check=True,
    )
    return Path(f"{output}.graphML")


def test_transformer_output_does_not_depend_on_hash_seed(tmp_path):
    input_file = tmp_path / "individuals.graphml"
    write_individual_network(input_file)

    outputs = [transform_with_hash_seed(input_file, tmp_path, seed) for seed in (1, 2, 3, 4)]
    contents = [out.read_bytes() for out in outputs]

    org_network = nx.read_graphml(outputs[0])
    assert sorted(org_network.nodes) == sorted(ORGANIZATIONS)
    assert org_network.number_of_edges() == 9  # 6 ring + 5 star - 2 shared (google-ibm, arm-google)
    assert all(content == contents[0] for content in contents[1:])
