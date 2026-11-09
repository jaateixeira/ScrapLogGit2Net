#!/usr/bin/env python3
"""Runs scraplog.analysis.compare_nofi_metrics. Kept so `./compare-two-nofi-GraphML-metrics.py` keeps working; the code lives in the scraplog package."""
import runpy

runpy.run_module("scraplog.analysis.compare_nofi_metrics", run_name="__main__")
