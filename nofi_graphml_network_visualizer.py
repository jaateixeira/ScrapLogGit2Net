#!/usr/bin/env python3
"""Runs scraplog.viz.nofi_visualizer. Kept so `./nofi_graphml_network_visualizer.py` keeps working; the code lives in the scraplog package."""
import runpy

runpy.run_module("scraplog.viz.nofi_visualizer", run_name="__main__")
