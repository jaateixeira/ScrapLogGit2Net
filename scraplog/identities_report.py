"""
The identities report: <output>.identities.csv, written on every scrapLog run.

One row per identity found in the commit headers (after -fe), sorted by e-mail:

    original_name, original_email   as written in the log
    name, email                     after --mailmap (the same without a mapping);
                                    email is the developer's node
    commits                         number of commits with this original identity
    possible_duplicate              why this person may be the same as another, for the
                                    researcher to check and add to the mailmap:
                                    'same_name' (the same name, ignoring case and spaces,
                                    is used with another e-mail), 'email_case' (another
                                    e-mail differs only in case), both joined by '+', or empty

Nothing is merged automatically; the column only suggests.
"""

import csv
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Optional, Tuple, Union

# (original name, original e-mail, name, e-mail) -> number of commits
Identity = Tuple[str, str, str, str]

COLUMNS = ("original_name", "original_email", "name", "email", "commits", "possible_duplicate")


def _name_key(name: str) -> str:
    return " ".join(name.split()).casefold()


def possible_duplicates(identities: Iterable[Identity]) -> Dict[str, str]:
    """For each (mapped) e-mail that may belong to the same person as another e-mail, the reason."""
    identities = list(identities)
    emails_by_name = defaultdict(set)
    emails_by_casefold = defaultdict(set)
    for _, _, name, email in identities:
        if name.strip():
            emails_by_name[_name_key(name)].add(email)
        emails_by_casefold[email.casefold()].add(email)

    reasons = defaultdict(list)
    for emails in emails_by_name.values():
        if len(emails) > 1:
            for email in emails:
                reasons[email].append("same_name")
    for emails in emails_by_casefold.values():
        if len(emails) > 1:
            for email in emails:
                reasons[email].append("email_case")
    return {email: "+".join(dict.fromkeys(why)) for email, why in reasons.items()}


def identity_rows(identity_commits: Mapping[Identity, int]) -> List[tuple]:
    duplicates = possible_duplicates(identity_commits)
    rows = [(on.strip(), oe, n.strip(), e, count, duplicates.get(e, ""))
            for (on, oe, n, e), count in identity_commits.items()]
    return sorted(rows, key=lambda row: (row[3], row[1], row[2], row[0]))


def write_identities_csv(path: Union[str, Path], identity_commits: Mapping[Identity, int],
                         metadata: Optional[Mapping[str, str]] = None) -> None:
    """The report, after '# name: value' lines for the metadata, as in the edge list."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        for name, value in (metadata or {}).items():
            f.write(f"# {name}: {value}\n")
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(COLUMNS)
        writer.writerows(identity_rows(identity_commits))
