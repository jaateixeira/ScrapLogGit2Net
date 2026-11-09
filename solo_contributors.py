#!/usr/bin/env python3
"""Runs scraplog.analysis.solo_contributors. Kept so `./solo_contributors.py` keeps working; the code lives in the scraplog package."""
import runpy

runpy.run_module("scraplog.analysis.solo_contributors", run_name="__main__")
