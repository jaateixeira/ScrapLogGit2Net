"""
Tests for inferring a developer's affiliation from their commit email.

Covers scrapLog.extract_affiliation_from_email(email, state), which returns:
  - the organisation inferred from the email domain (lower case),
  - "unknown_by_ScrapLog" for a valid record whose organisation can't be resolved,
  - None for invalid input (callers skip the record).

Email filtering (-f) is no longer part of affiliation extraction; it happens
later in scrapLog.apply_email_filtering, which is tested at the end.

Run with:
    pytest tests/unit/test_email_affiliation.py -v
"""

import networkx as nx
import pytest

from scraplog.scraplog import ProcessingState, apply_email_filtering, extract_affiliation_from_email


@pytest.fixture
def state():
    """A fresh ProcessingState per test, so settings never leak between tests."""
    return ProcessingState()


# Standard formats
def test_normal_email(state):
    assert extract_affiliation_from_email("user@apolinex.com", state) == "apolinex"


def test_hyphenated_domain(state):
    assert extract_affiliation_from_email("name@university-edu.org", state) == "university-edu"


def test_affiliation_is_lower_case(state):
    assert extract_affiliation_from_email("USER@Google.COM", state) == "google"


def test_email_with_question_mark(state):
    """A trailing '?' (seen in some git logs) is stripped."""
    assert extract_affiliation_from_email("user@domain?", state) == "domain"


# Subdomains
@pytest.mark.parametrize("email,expected", [
    ("user@us.ibm.com", "ibm"),
    ("name@linux.vnet.ibm.com", "ibm"),
    ("test@br.ibm.com", "ibm"),
    ("eng@alumni.mit.edu", "mit"),
])
def test_subdomains_resolve_to_organisation(state, email, expected):
    assert extract_affiliation_from_email(email, state) == expected


def test_unknown_ibm_subdomain_still_resolves_to_ibm(state):
    """Earlier versions exited on IBM subdomains not on an allow-list; now any
    subdomain of ibm.com resolves to 'ibm'."""
    assert extract_affiliation_from_email("user@invalid.ibm.com", state) == "ibm"


@pytest.mark.parametrize("email,expected", [
    ("someone@company.co.uk", "company"),
    ("someone@university.ac.uk", "university"),
])
def test_second_level_country_domains(state, email, expected):
    assert extract_affiliation_from_email(email, state) == expected


# Email aggregation config (-a)
def test_aggregation_config(state):
    state.email_aggregation_config = {"ibm": "ibm"}
    assert extract_affiliation_from_email("user@us.ibm.com", state) == "ibm"


# Invalid input returns None instead of exiting
@pytest.mark.parametrize("email", ["not-an-email", "", None])
def test_invalid_input_returns_none(state, email):
    assert extract_affiliation_from_email(email, state) is None


def test_verbose_mode_does_not_change_result(state):
    state.verbose_mode = True
    state.very_verbose_mode = True
    assert extract_affiliation_from_email("user@apolinex.com", state) == "apolinex"


# Email filtering (-f)
def test_filtered_emails_are_removed_from_network(state):
    """Filtered developers are removed from the network, along with any
    developers left isolated by that removal."""
    state.email_filtering_mode = True
    state.emails_to_filter = {"spam@example.com"}
    state.dev_to_dev_network = nx.Graph()
    state.dev_to_dev_network.add_edge("spam@example.com", "lonely@example.com")
    state.dev_to_dev_network.add_edge("alice@example.com", "bob@example.com")

    apply_email_filtering(state)

    assert set(state.dev_to_dev_network.nodes()) == {"alice@example.com", "bob@example.com"}


def test_filtering_disabled_keeps_network(state):
    state.email_filtering_mode = False
    state.emails_to_filter = {"spam@example.com"}
    state.dev_to_dev_network = nx.Graph()
    state.dev_to_dev_network.add_edge("spam@example.com", "alice@example.com")

    apply_email_filtering(state)

    assert state.dev_to_dev_network.has_node("spam@example.com")
