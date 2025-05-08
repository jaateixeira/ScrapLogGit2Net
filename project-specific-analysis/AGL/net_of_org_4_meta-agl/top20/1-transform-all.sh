#!/bin/bash

# Directory containing GraphML files
INPUT_DIR="../../net_of_ind_4_meta-agl/top20_graphML"

# Python script to execute
PYTHON_SCRIPT="../../../../transform-nofi-2-nofo-GraphML.py"

# Loop through all .graphML files in the directory
for graphml_file in "$INPUT_DIR"/*.graphML; do
    if [ -f "$graphml_file" ]; then
        echo "Processing: $graphml_file"
        python3 "$PYTHON_SCRIPT" "$graphml_file"
    fi
done

echo "All files processed."
