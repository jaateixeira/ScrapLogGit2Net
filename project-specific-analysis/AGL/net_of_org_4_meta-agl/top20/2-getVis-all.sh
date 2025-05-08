#!/bin/bash

# Python script to execute
PYTHON_SCRIPT="../../../../formatFilterAndViz-nofo-GraphML.py"

# Find all matching files in the current directory
for graphml_file in *filtered-transformed-to-nofo.graphML; do
    if [ -f "$graphml_file" ]; then
        echo "Processing: $graphml_file"
        python3 "$PYTHON_SCRIPT" -l "$graphml_file"
    fi
done

echo "All matching files processed."
