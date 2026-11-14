"""
Network files did not record the tool version or the options they were made
with. Every network writer (scrapLog for the three network types, the
nofi-to-nofo transformer and the deanonymizer) now writes graph-level GraphML
attributes: scraplog_tool, scraplog_version, scraplog_parameters (JSON) and
scraplog_inputs (JSON: path and SHA-256 of each input file). There is no
timestamp, so the same input still gives byte-identical files.

Run with:
    pytest tests/unit/test_output_metadata.py -v
"""

import hashlib
import io
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import networkx as nx
import pytest

import scraplog
from scraplog.metadata import add_metadata_to_graphml_file, insert_graphml_metadata, run_metadata

PROJECT_ROOT = Path(__file__).resolve().parents[2]
LOG = PROJECT_ROOT / "test-data" / "ExtensionFiltering" / "extfilter-tc1-include-py-only.IN"
ENV = {"PYTHONPATH": str(PROJECT_ROOT), "PATH": "", "COLUMNS": "200"}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(cwd, *args):
    result = subprocess.run([sys.executable, *map(str, args)], cwd=cwd, capture_output=True, text=True,
                            env=ENV, timeout=300)
    assert result.returncode == 0, result.stdout + result.stderr
    return result


def read_network(path):
    """The graph in a GraphML file, or in the (single) GraphML file of a temporal .zip."""
    if path.suffix == ".zip":
        with zipfile.ZipFile(path) as archive:
            (name,) = archive.namelist()
            return nx.read_graphml(io.BytesIO(archive.read(name)))
    return nx.read_graphml(path)


@pytest.fixture
def log(tmp_path):
    shutil.copy(LOG, tmp_path / "t.IN")
    (tmp_path / "filter.txt").write_text("nobody@example.com\n")
    return tmp_path


@pytest.mark.parametrize("network_type, output", [
    ("inter_individual_graph_unweighted", "t.NetworkFile.graphML"),
    ("inter_individual_graph_weighted", "t.WeightedNetwork.graphML"),
    ("inter_individual_graph_temporal", "t.temporal.graphml.zip"),
])
def test_scraplog_records_version_options_and_inputs(log, network_type, output):
    run(log, PROJECT_ROOT / "scrapLog.py", "-r", "t.IN", "-t", network_type, "-fe", "filter.txt")
    first = (log / output).read_bytes()
    run(log, PROJECT_ROOT / "scrapLog.py", "-r", "t.IN", "-t", network_type, "-fe", "filter.txt")

    assert (log / output).read_bytes() == first  # still byte-identical
    meta = read_network(log / output).graph
    assert meta["scraplog_tool"] == "scrapLog.py"
    assert meta["scraplog_version"] == scraplog.__version__
    parameters = json.loads(meta["scraplog_parameters"])
    assert parameters["type_of_network"] == network_type
    assert parameters["raw"] == "t.IN"
    assert "output_file" not in parameters and "verbose" not in parameters
    assert json.loads(meta["scraplog_inputs"]) == {
        "filter_emails": {"path": "filter.txt", "sha256": sha256(log / "filter.txt")},
        "raw": {"path": "t.IN", "sha256": sha256(log / "t.IN")},
    }


def test_transformer_records_its_own_metadata(log):
    run(log, PROJECT_ROOT / "scrapLog.py", "-r", "t.IN")
    run(log, PROJECT_ROOT / "transform_nofi_2_nofo_graphml.py", "t.NetworkFile.graphML", "-o", "org.graphML")

    meta = nx.read_graphml(log / "org.graphML").graph
    assert '<data key="d0">1</data>' in (log / "org.graphML").read_text()  # weight keeps its key id
    assert meta["scraplog_tool"] == "transform_nofi_2_nofo_graphml.py"
    assert meta["scraplog_version"] == scraplog.__version__
    assert "outfile" not in json.loads(meta["scraplog_parameters"])  # the output name is not recorded
    # the input's hash links this file to the scrapLog file, whose metadata describes that step
    assert json.loads(meta["scraplog_inputs"]) == {
        "file": {"path": "t.NetworkFile.graphML", "sha256": sha256(log / "t.NetworkFile.graphML")}}


RUN_DEANONYMIZER = """
import sys
import scraplog.tools.deanonymize_github_users as d
d.validate_configuration_and_api_access = lambda path: {"token": "secret-token"}
sys.argv = ["deanonymize_github_users.py", "in.graphml", "--no-cache"]
d.main()
"""


def test_deanonymizer_replaces_the_metadata_of_its_input(tmp_path):
    g = nx.Graph([("1", "2")])
    g.add_node("1", **{"e-mail": "alice@google.com", "affiliation": "google"})  # no lookup needed
    g.add_node("2", **{"e-mail": "bob@ibm.com", "affiliation": "ibm"})
    nx.write_graphml(g, tmp_path / "in.graphml")
    add_metadata_to_graphml_file(tmp_path / "in.graphml", {
        "scraplog_tool": "scrapLog.py", "scraplog_version": "0.9", "scraplog_parameters": "{}",
        "scraplog_inputs": "{}"})

    run(tmp_path, "-c", RUN_DEANONYMIZER)

    meta = nx.read_graphml(tmp_path / "in.out.graphml").graph
    assert meta["scraplog_tool"] == "deanonymize_github_users.py"
    assert meta["scraplog_version"] == scraplog.__version__
    assert json.loads(meta["scraplog_parameters"])["no_cache"] is True
    assert json.loads(meta["scraplog_inputs"]) == {
        "input": {"path": "in.graphml", "sha256": sha256(tmp_path / "in.graphml")}}
    assert "secret-token" not in (tmp_path / "in.out.graphml").read_text()


def test_metadata_is_escaped(tmp_path):
    (tmp_path / "a&b.IN").write_text("x")
    meta = run_metadata("tool<1>", {"o": "a&b.IN"}, {"raw": tmp_path / "a&b.IN"})
    g = nx.Graph([("a", "b")])
    nx.write_graphml(g, tmp_path / "plain.graphml")

    text = insert_graphml_metadata((tmp_path / "plain.graphml").read_text(), meta)
    (tmp_path / "with_meta.graphml").write_text(text)

    assert nx.read_graphml(tmp_path / "with_meta.graphml").graph["scraplog_tool"] == "tool<1>"
    assert json.loads(nx.read_graphml(tmp_path / "with_meta.graphml").graph["scraplog_parameters"]) == {
        "o": "a&b.IN"}


@pytest.mark.parametrize("network_type, output", [
    ("inter_individual_graph_unweighted", "t.NetworkFile.graphML"),
    ("inter_individual_graph_weighted", "t.WeightedNetwork.graphML"),
])
def test_scraplog_output_with_metadata_is_valid_graphml(log, network_type, output):
    xmllint = shutil.which("xmllint")
    if xmllint is None:
        pytest.skip("xmllint is not installed")
    schema = PROJECT_ROOT / "tests" / "acceptance-test-scripts" / "graphml-schema" / "graphml.xsd"

    run(log, PROJECT_ROOT / "scrapLog.py", "-r", "t.IN", "-t", network_type)

    result = subprocess.run([xmllint, "--noout", "--schema", str(schema), str(log / output)],
                            capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stdout + result.stderr
