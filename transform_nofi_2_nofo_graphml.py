#!/usr/bin/env python3
"""Runs scraplog.analysis.transform_nofi_to_nofo. Kept so `./transform_nofi_2_nofo_graphml.py` keeps working; the code lives in the scraplog package."""
import runpy

runpy.run_module("scraplog.analysis.transform_nofi_to_nofo", run_name="__main__")
