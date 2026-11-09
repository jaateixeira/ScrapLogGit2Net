#!/usr/bin/env python3
"""Runs scraplog.analysis.compare_nofi_sets. Kept so `./compare-set-nofi-GraphML.py` keeps working; the code lives in the scraplog package."""
import runpy

runpy.run_module("scraplog.analysis.compare_nofi_sets", run_name="__main__")
