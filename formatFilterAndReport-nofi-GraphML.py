#!/usr/bin/env python3
"""Runs scraplog.analysis.report_nofi. Kept so `./formatFilterAndReport-nofi-GraphML.py` keeps working; the code lives in the scraplog package."""
import runpy

runpy.run_module("scraplog.analysis.report_nofi", run_name="__main__")
