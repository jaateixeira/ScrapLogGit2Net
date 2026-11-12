# The only place the version is set; pyproject.toml and scraplog/__init__.py read it from here.
# (A separate module: on case-insensitive file systems, setuptools would find scrapLog.py for "scraplog".)
__version__ = "1.1.0"
