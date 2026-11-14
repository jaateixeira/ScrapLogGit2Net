"""
Provenance metadata written into every network file.

Each network file records which tool wrote it, the ScrapLogGit2Net version,
the options it was run with and the SHA-256 of the input files that shaped
it, as graph-level GraphML attributes (<data> elements of <graph>). There is
no timestamp, so the same input and options still give byte-identical files.

    scraplog_tool        program name, e.g. scrapLog.py
    scraplog_version     ScrapLogGit2Net version
    scraplog_parameters  the options, as JSON with sorted keys (paths as given);
                         options that only choose the output file name or how
                         much is printed are left out, so writing the same
                         network to another file gives the same bytes
    scraplog_inputs      {option: {"path": ..., "sha256": ...}}, as JSON

A tool that reads a network file and writes a new one (the transformer, the
deanonymizer) writes its own attributes; those of its input are not copied. The input's SHA-256
links the new file to the one it was made from, whose attributes describe the
earlier step.

Reading them back:  networkx.read_graphml(f).graph["scraplog_version"];
in R (igraph):      graph_attr(read_graph(f, format = "graphml"), "scraplog_version").
"""

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional, Union
from xml.sax.saxutils import escape, quoteattr

from scraplog._version import __version__

PathLike = Union[str, Path]


def file_sha256(path: PathLike) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def run_metadata(tool: str, parameters: Mapping[str, Any],
                 input_files: Mapping[str, Optional[PathLike]],
                 not_recorded: Iterable[str] = ()) -> dict[str, str]:
    """Metadata for one run. Options named in not_recorded, and input files that are None
    (option not given), are left out."""
    skip = set(not_recorded)
    parameters = {name: value for name, value in parameters.items() if name not in skip}
    inputs = {name: {"path": str(path), "sha256": file_sha256(path)}
              for name, path in sorted(input_files.items()) if path is not None}
    return {
        "scraplog_tool": tool,
        "scraplog_version": __version__,
        "scraplog_parameters": json.dumps(parameters, sort_keys=True, default=str),
        "scraplog_inputs": json.dumps(inputs, sort_keys=True),
    }


def add_metadata_to_graphml_file(path: PathLike, metadata: Mapping[str, str]) -> None:
    """Add the metadata to a GraphML file written by networkx. It is added to the text rather
    than to graph.graph, so the ids of the other keys (d0, d1, ...) stay as they were."""
    graphml = Path(path).read_text(encoding="utf-8")
    Path(path).write_text(insert_graphml_metadata(graphml, metadata), encoding="utf-8")


def graphml_metadata_keys(metadata: Mapping[str, str]) -> str:
    """<key> elements for the metadata; they go before <graph>."""
    return "".join(f'<key id={quoteattr(name)} for="graph" attr.name={quoteattr(name)} attr.type="string"/>\n'
                   for name in metadata)


def graphml_metadata_data(metadata: Mapping[str, str]) -> str:
    """<data> elements for the metadata; they go right after the <graph ...> opening tag."""
    return "".join(f"\t<data key={quoteattr(name)}>{escape(value)}</data>\n" for name, value in metadata.items())


def insert_graphml_metadata(graphml: str, metadata: Mapping[str, str]) -> str:
    """Add the metadata to GraphML text written by another library (e.g. networkx-temporal)."""
    start = graphml.index("<graph ")
    line_start = graphml.rfind("\n", 0, start) + 1
    end = graphml.index(">", start) + 1
    return (graphml[:line_start] + graphml_metadata_keys(metadata) + graphml[line_start:end] + "\n"
            + graphml_metadata_data(metadata) + graphml[end:].lstrip("\n"))
