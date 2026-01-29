# tests/test_parsing.py


import pytest

from scrapLog import getDateEmailAffiliation, getAffiliationFromEmail, findFilesOnBlock


from rich.console import Console
from rich.table import Table
from loguru import logger
from utils import  unified_logger as logger

console = Console()


@pytest.fixture
def sample_commit_block():
    return [
        "==John Doe;john@example.com;Thu Feb 20 03:56:00 2014 +0000==\n",
        "file1.txt\n",
        "dir/file2.py\n",
        "\n"
    ]


def test_getDateEmailAffiliation_normal_case():
    line = "==Alice;alice@company.com;Mon Jan 15 12:34:56 2024 +0000=="
    date, email, affiliation = getDateEmailAffiliation(line)

    assert email == "alice@company.com"
    assert affiliation == "company"
    assert "Jan 15" in date


def test_getAffiliationFromEmail_ibm_special_case():
    ibm_emails = [
        ("user@ibm.com", "ibm"),
        ("user@au1.ibm.com", "ibm"),
        ("user@linux.vnet.ibm.com", "ibm")
    ]

    table = Table(title="IBM Email Special Cases")
    table.add_column("Email")
    table.add_column("Expected")
    table.add_column("Actual")

    for email, expected in ibm_emails:
        actual = getAffiliationFromEmail(email)
        print(f"email: {email=},{expected=},actual={actual=}")
        table.add_row(email, expected, actual)

        assert actual == expected

    console.print(table)


def test_findFilesOnBlock(sample_commit_block):
    files = findFilesOnBlock(sample_commit_block[1:])

    table = Table(title="File Detection Results")
    table.add_column("Expected File")
    table.add_column("Found in Output")

    expected_files = ["file1.txt", "dir/file2.py"]
    for expected in expected_files:
        found = expected in files
        table.add_row(expected, "✓" if found else "✗")
        assert expected in files

    console.print(table)
