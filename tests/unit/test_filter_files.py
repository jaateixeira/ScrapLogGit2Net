"""
Tests for -ff / --filter-files: ignore files listed in a text file.

The filter file has one entry per line: an exact path as it appears in the
git log, or a shell-style wildcard pattern ('*.md', 'docs/*'). Blank lines
and lines starting with '#' are ignored. A missing or unreadable filter file
is a fatal error.

Run with:
    pytest tests/unit/test_filter_files.py -v
"""

import pytest

from scraplog.core.models import ProcessingState
from scraplog.parsing import extract_files_from_block, is_filtered_file, load_file_filter_file, process_commit_block


def write_filter_file(tmp_path, content):
    path = tmp_path / "files_to_ignore.txt"
    path.write_text(content, encoding="utf-8")
    return path


def state_with_filter(tmp_path, content):
    state = ProcessingState()
    state.file_filtering_mode = True
    load_file_filter_file(state, write_filter_file(tmp_path, content))
    return state


# =============================================================================
# Loading the filter file
# =============================================================================

def test_load_separates_exact_paths_and_patterns(tmp_path):
    state = state_with_filter(tmp_path, "src/main.py\n*.md\ndocs/*\nBUILD\n")

    assert state.files_to_filter == {"src/main.py", "BUILD"}
    assert sorted(state.file_filter_patterns) == ["*.md", "docs/*"]


def test_load_ignores_blank_lines_comments_and_whitespace(tmp_path):
    content = (
        "# generated files\n"
        "\n"
        "   src/generated.py   \n"
        "\t\n"
        "  # indented comment\n"
        "*.pb.go\n"
    )
    state = state_with_filter(tmp_path, content)

    assert state.files_to_filter == {"src/generated.py"}
    assert state.file_filter_patterns == ["*.pb.go"]


def test_load_empty_file_filters_nothing(tmp_path):
    state = state_with_filter(tmp_path, "# nothing to ignore yet\n\n")

    assert state.files_to_filter == set()
    assert state.file_filter_patterns == []


def test_load_missing_file_exits(tmp_path):
    state = ProcessingState()

    with pytest.raises(SystemExit) as exc_info:
        load_file_filter_file(state, tmp_path / "does_not_exist.txt")

    assert exc_info.value.code == 1


def test_load_unreadable_file_exits(tmp_path):
    """A directory or a binary file cannot be read as a filter list."""
    state = ProcessingState()

    with pytest.raises(SystemExit):
        load_file_filter_file(state, tmp_path)  # a directory

    binary = tmp_path / "binary.bin"
    binary.write_bytes(b"\xff\xfe\x00\x81")
    with pytest.raises(SystemExit):
        load_file_filter_file(state, binary)


# =============================================================================
# Matching
# =============================================================================

@pytest.mark.parametrize("filename,expected", [
    # exact paths
    ("src/main.py", True),
    ("src/main.pyc", False),
    ("other/src/main.py", False),       # exact paths match the full path only
    # '*.md' matches markdown files in any directory ('*' also matches '/')
    ("README.md", True),
    ("docs/guide/intro.md", True),
    ("README.MD", False),               # matching is case-sensitive, like git paths
    ("notes.mdx", False),
    # 'docs/*' matches everything under docs/
    ("docs/api.rst", True),
    ("docs/deep/nested/file.txt", True),
    ("mydocs/api.rst", False),
    # '?' and '[]' wildcards
    ("third_party/lib1/x.c", True),
    ("third_party/lib10/x.c", False),
    ("test_a.py", True),
    ("test_d.py", False),
])
def test_is_filtered_file(tmp_path, filename, expected):
    state = state_with_filter(
        tmp_path,
        "src/main.py\n*.md\ndocs/*\nthird_party/lib?/*\ntest_[abc].py\n",
    )

    assert is_filtered_file(filename, state) is expected


def test_extract_files_from_block_applies_patterns(tmp_path):
    state = state_with_filter(tmp_path, "*.md\nBUILD\n")
    block = ["README.md\n", "src/main.py\n", "BUILD\n", "src/BUILD\n", "docs/guide.md\n", "\n"]

    files = extract_files_from_block(block, state)

    assert files == ["src/main.py", "src/BUILD"]


def test_filtering_mode_off_keeps_all_files(tmp_path):
    state = state_with_filter(tmp_path, "*.md\n")
    state.file_filtering_mode = False

    files = extract_files_from_block(["README.md\n", "src/main.py\n", "\n"], state)

    assert files == ["README.md", "src/main.py"]


def test_commit_touching_only_filtered_files_is_skipped(tmp_path):
    state = state_with_filter(tmp_path, "*.md\n")
    block = ["==Jane Doe;jane@example.com;Thu Feb 20 03:56:00 2014 +0000==", "README.md", "docs/a.md"]

    assert process_commit_block(block, state, 0) is False
    assert state.parsed_change_log_entries == []
