#!/bin/bash
# compile_all_git_logs.sh - Minimalist AGL git log collector

set -eo pipefail

# Configuration
OUTPUT_FILE="agl_raw_logs_$(git branch --show-current)_$(date +%Y%m%d_%H%M%S).txt"

# Console header
echo "=== AGL Git Log Collector ==="
echo "Started: $(date -u)"
echo "Output will contain only raw git log data"
echo "Processing all repositories..."

# Initialize counters
TOTAL_REPOS=0
PROCESSED_REPOS=0
FAILED_REPOS=0

# Process repositories
repo forall -c '
    # Only output the raw git log data to file
    {
        # echo -e "\n\n[START_REPO:$REPO_PROJECT]"
        git log \
        --pretty=format:"==%an;%ae;%ad==" --name-only
            --pretty=format:"==%an;%ae;%ad=="
            --name-only
        # echo -e "[END_REPO:$REPO_PROJECT]"
    } >> "'"$OUTPUT_FILE"'"

    # Count success
    exit 0
' || {
    # Count failures
    FAILED_REPOS=$((FAILED_REPOS + 1))
}

# Get total repo count
TOTAL_REPOS=$(repo list | wc -l)
PROCESSED_REPOS=$((TOTAL_REPOS - FAILED_REPOS))

# Console summary
echo -e "\n=== Processing Complete ==="
echo "Total repositories: $TOTAL_REPOS"
echo "Successfully processed: $PROCESSED_REPOS"
echo "Failed: $FAILED_REPOS"
echo "Raw output file: $PWD/$OUTPUT_FILE"
echo "Finished: $(date -u)"