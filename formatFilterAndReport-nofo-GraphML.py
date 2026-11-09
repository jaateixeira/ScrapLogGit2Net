#!/usr/bin/env python3
"""Runs scraplog.analysis.report_nofo. Kept so `./formatFilterAndReport-nofo-GraphML.py` keeps working; the code lives in the scraplog package."""
import runpy

runpy.run_module("scraplog.analysis.report_nofo", run_name="__main__")
