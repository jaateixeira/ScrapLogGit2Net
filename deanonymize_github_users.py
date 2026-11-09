#!/usr/bin/env python3
"""Runs scraplog.tools.deanonymize_github_users. Kept so `./deanonymize_github_users.py` keeps working; the code lives in the scraplog package."""
import runpy

runpy.run_module("scraplog.tools.deanonymize_github_users", run_name="__main__")
