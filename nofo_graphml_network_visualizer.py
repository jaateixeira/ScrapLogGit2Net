#!/usr/bin/env python3
"""Runs scraplog.viz.nofo_visualizer. Kept so `./nofo_graphml_network_visualizer.py` keeps working; the code lives in the scraplog package."""
import runpy

runpy.run_module("scraplog.viz.nofo_visualizer", run_name="__main__")
