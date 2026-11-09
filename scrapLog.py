#!/usr/bin/env python3
"""Runs scraplog.scraplog. Kept so `./scrapLog.py` keeps working; the code lives in the scraplog package."""
import runpy

runpy.run_module("scraplog.scraplog", run_name="__main__")
