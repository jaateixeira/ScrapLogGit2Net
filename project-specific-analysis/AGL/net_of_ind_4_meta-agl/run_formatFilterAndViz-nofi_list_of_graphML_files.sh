#!/bin/bash

# Path to the configuration file
CONFIG_FILE="config.cfg"

# Check if the configuration file exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Configuration file $CONFIG_FILE not found."
    exit 1
fi

# Read the vizNofI path from the configuration file
VIZNOFI_PATH=$(grep -Po '(?<=^vizNofIpath=).+' "$CONFIG_FILE")

# Check if the vizNofI path is valid
if [ ! -x "$VIZNOFI_PATH" ]; then
    echo "formatFilterAndViz-nofi-GraphML.py not found or not executable at path: $VIZNOFI_PATH"
    exit 1
fi

# Check if at least one argument is provided
if [ "$#" -lt 1 ]; then
    echo "Usage: $0 file1 [file2 ... fileN]"
    exit 1
fi

# Loop through each argument and call formatFilterAndViz-nofi-GraphML.py with the specified options
for file in "$@"; do
    if [ -f "$file" ]; then
        "$VIZNOFI_PATH" -nl spring -l  "$file"
    else
        echo "File $file does not exist."
    fi
done

