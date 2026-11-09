#!/usr/bin/env python3
"""Runs scraplog.tools.scrap_repo_logs. Kept so `./scrap_repo_repositories_logs.py` keeps working; the code lives in the scraplog package."""
import runpy

runpy.run_module("scraplog.tools.scrap_repo_logs", run_name="__main__")
