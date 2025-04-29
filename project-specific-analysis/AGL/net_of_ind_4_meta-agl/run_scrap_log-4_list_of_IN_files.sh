#!/bin/bash

# Path to the configuration file
CONFIG_FILE="config.cfg"

# Check if the configuration file exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Configuration file $CONFIG_FILE not found."
    exit 1
fi

# Read the scrapLog path from the configuration file
SCRAPLOG_PATH=$(grep -Po '(?<=^path=).+' "$CONFIG_FILE")

# Check if the scrapLog path is valid
if [ ! -x "$SCRAPLOG_PATH" ]; then
    echo "scrapLog.py not found or not executable at path: $SCRAPLOG_PATH"
    exit 1
fi

# Check if at least one argument is provided
if [ "$#" -lt 1 ]; then
    echo "Usage: $0 file1 [file2 ... fileN]"
    exit 1
fi

# Loop through each argument and call scrapLog.py -r
for file in "$@"; do
    if [ -f "$file" ]; then
        "$SCRAPLOG_PATH" -r "$file"
    else
        echo "File $file does not exist."
    fi
done

