"""
Error paths must work outside PyCharm too.

scraplog.utils.unified_console exports a name `traceback` that is Python's
traceback module inside PyCharm but rich.traceback elsewhere (which has no
format_exc()/print_exc()). parsing.py and output.py used that name, so outside
PyCharm (normal terminals, GitHub Actions) their error paths crashed with
AttributeError. The test runs scrapLog in a clean environment, without the
variables PyCharm sets, so it fails the same way GitHub Actions did.

Run with:
    pytest tests/unit/test_errors_outside_pycharm.py -v
"""

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# No PYCHARM_HOSTED / TERMINAL_EMULATOR / ... : behave like a normal terminal or CI
CLEAN_ENV = {"PYTHONPATH": str(PROJECT_ROOT), "MPLBACKEND": "Agg", "PATH": "", "COLUMNS": "200"}

# The first block has no "==name;email;date==" header
MALFORMED_LOG = """src/orphan_file.py

==Alice;alice@example.com;Mon Jan 1 10:00:00 2024 +0000==
shared.py

"""


def test_block_without_header_exits_cleanly_outside_pycharm(tmp_path):
    log = tmp_path / "malformed.IN"
    log.write_text(MALFORMED_LOG)

    result = subprocess.run(
        [sys.executable, "-m", "scraplog.scraplog", "-r", str(log), "-o", str(tmp_path / "out.graphml")],
        cwd=tmp_path, capture_output=True, text=True, env=CLEAN_ENV,
    )
    output = result.stdout + result.stderr

    assert "Not in PyCharm terminal" in output  # the environment really is non-PyCharm
    assert "AttributeError" not in output
    assert "does not start with '=='" in output
    assert result.returncode == 1


def test_parsing_and_output_use_the_standard_traceback_module():
    """Checked in a clean environment, where unified_console.traceback is rich.traceback."""
    code = (
        "import traceback, scraplog.parsing, scraplog.output, scraplog.analysis.report_nofo; "
        "assert scraplog.parsing.traceback is traceback; "
        "assert scraplog.output.traceback is traceback; "
        "assert scraplog.analysis.report_nofo.traceback is traceback; "
        "print('ok')"
    )
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, env=CLEAN_ENV)

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.strip().endswith("ok")
