"""ScrapLogGit2Net: co-editing networks from git logs."""

from scraplog._version import __version__


def version_text(prog: str) -> str:
    """Text printed by every tool's --version option."""
    return f"{prog} (ScrapLogGit2Net) {__version__}"
