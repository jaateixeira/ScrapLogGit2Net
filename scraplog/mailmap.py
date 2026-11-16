"""
Identity merging with a Git mailmap file (--mailmap FILE).

The file uses Git's .mailmap format (see `git help gitmailmap`). Each line maps
the name and/or e-mail a commit was made with to a person's proper name and/or
e-mail:

    Proper Name <commit@email>                             proper name, matched by e-mail
    <proper@email> <commit@email>                          proper e-mail, matched by e-mail
    Proper Name <proper@email> <commit@email>              both, matched by e-mail
    Proper Name <proper@email> Commit Name <commit@email>  both, only for that name and e-mail

As in Git, e-mails and names are matched without regard to case, an entry for a
commit name and e-mail wins over an entry for the e-mail alone, lines starting
with '#' are comments, and text after the last '>' is ignored.

scrapLog applies the map to every commit header right after parsing, before -fe
and before any network is built. The mapped e-mail is the developer's node and
gives the affiliation. Nothing is merged without a mapping; likely duplicates
are listed for the researcher to check (see scraplog.identities_report).
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional, Tuple, Union

_EMAIL = re.compile(r"<([^<>]*)>")


def _key(text: str) -> str:
    return " ".join(text.split()).casefold()


@dataclass
class Mailmap:
    # commit e-mail -> (proper name, proper e-mail); None keeps the commit's value
    by_email: Dict[str, Tuple[Optional[str], Optional[str]]] = field(default_factory=dict)
    # (commit name, commit e-mail) -> (proper name, proper e-mail)
    by_name_and_email: Dict[Tuple[str, str], Tuple[Optional[str], Optional[str]]] = field(default_factory=dict)

    def map(self, name: str, email: str) -> Tuple[str, str]:
        """The proper (name, e-mail) for a commit's name and e-mail; unchanged if not mapped."""
        entry = (self.by_name_and_email.get((_key(name), _key(email)))
                 or self.by_email.get(_key(email)))
        if entry is None:
            return name, email
        proper_name, proper_email = entry
        return (proper_name if proper_name is not None else name,
                proper_email if proper_email is not None else email)

    def __len__(self) -> int:
        return len(self.by_email) + len(self.by_name_and_email)


def parse_mailmap_line(line: str) -> Optional[Tuple[Optional[str], Optional[str], Optional[str], str]]:
    """(proper name, proper e-mail, commit name, commit e-mail) of one line, or None for a
    blank line or comment. Raises ValueError for a line that is not a mailmap entry."""
    if not line.strip() or line.lstrip().startswith("#"):
        return None
    emails = list(_EMAIL.finditer(line))
    if not emails or len(emails) > 2:
        raise ValueError(f"expected one or two <e-mail>: {line.strip()!r}")
    proper_name = line[:emails[0].start()].strip() or None
    if len(emails) == 1:
        return proper_name, None, None, emails[0].group(1).strip()
    commit_name = line[emails[0].end():emails[1].start()].strip() or None
    return proper_name, emails[0].group(1).strip() or None, commit_name, emails[1].group(1).strip()


def load_mailmap(path: Union[str, Path]) -> Mailmap:
    """Read a mailmap file. Raises ValueError (with the line number) for a malformed line.
    For repeated entries, the last one wins, as in Git."""
    mailmap = Mailmap()
    for number, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        try:
            parsed = parse_mailmap_line(line)
        except ValueError as error:
            raise ValueError(f"line {number}: {error}") from None
        if parsed is None:
            continue
        proper_name, proper_email, commit_name, commit_email = parsed
        if not commit_email:
            raise ValueError(f"line {number}: empty commit e-mail")
        if commit_name:
            mailmap.by_name_and_email[(_key(commit_name), _key(commit_email))] = (proper_name, proper_email)
        else:
            mailmap.by_email[_key(commit_email)] = (proper_name, proper_email)
    return mailmap
