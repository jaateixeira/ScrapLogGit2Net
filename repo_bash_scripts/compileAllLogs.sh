#!/bin/bash
# compile_all_git_logs.sh - Enhanced AGL repository log collector with detailed format

set -eo pipefail

# Configuration
OUTPUT_FILE="agl_git_logs_$(date +%Y%m%d_%H%M%S).txt"
MAX_LOG_ENTRIES=50  # Reduced due to more verbose output
DATE_FORMAT="%Y-%m-%d %H:%M:%S %z"  # ISO 8601 format with timezone

# Initialize timeline tracking
EARLIEST_DATE=""
LATEST_DATE=""

# Header
{
echo "=== AGL Repository Git Logs ==="
echo "Generated: $(date -u)"
echo "Log Format: ==author name;author email;commit date== followed by changed files"
echo "================================="
} > "$OUTPUT_FILE"

# Process each repository
repo forall -c '
    # Repository header
    echo -e "\n\n[ Repository: $REPO_PROJECT ]"
    echo "Path: $REPO_PATH"
    echo "Branch: $(git branch --show-current)"
    
    # Get timeline data
    FIRST_COMMIT=$(git log --reverse --pretty=format:"%ad" --date=format:"'"$DATE_FORMAT"'" -1 2>/dev/null || echo "N/A")
    LAST_COMMIT=$(git log --pretty=format:"%ad" --date=format:"'"$DATE_FORMAT"'" -1 2>/dev/null || echo "N/A")
    
    echo "First commit: $FIRST_COMMIT"
    echo "Last commit: $LAST_COMMIT"
    
    # Update global timeline
    if [[ "$FIRST_COMMIT" != "N/A" ]]; then
        if [[ -z "$EARLIEST_DATE" ]] || [[ "$FIRST_COMMIT" < "$EARLIEST_DATE" ]]; then
            EARLIEST_DATE="$FIRST_COMMIT"
        fi
    fi
    
    if [[ "$LAST_COMMIT" != "N/A" ]]; then
        if [[ -z "$LATEST_DATE" ]] || [[ "$LAST_COMMIT" > "$LATEST_DATE" ]]; then
            LATEST_DATE="$LAST_COMMIT"
        fi
    fi
    
    # Get detailed logs with changed files
    echo -e "\nCommit History:"
    git log \
        --pretty=format:"==%an;%ae;%ad==" \
        --date=format:"'"$DATE_FORMAT"'" \
        --name-only \
        -'"$MAX_LOG_ENTRIES"'
    
    # Separator
    echo "------------------------------"
' >> "$OUTPUT_FILE" 2>&1 || {
    echo "Error: Failed to gather logs from some repositories" >&2
    exit 1
}

# Summary
REPO_COUNT=$(repo list | wc -l)
{
echo -e "\n\n=== Summary ==="
echo "Total repositories processed: $REPO_COUNT"
echo "Project timeline:"
echo "  First commit in any repo: ${EARLIEST_DATE:-N/A}"
echo "  Last commit in any repo: ${LATEST_DATE:-N/A}"
} >> "$OUTPUT_FILE"

# Calculate duration if possible
if [[ -n "$EARLIEST_DATE" && -n "$LATEST_DATE" ]]; then
    START_SEC=$(date -d "$EARLIEST_DATE" +%s 2>/dev/null || echo "")
    END_SEC=$(date -d "$LATEST_DATE" +%s 2>/dev/null || echo "")
    
    if [[ -n "$START_SEC" && -n "$END_SEC" ]]; then
        DURATION_DAYS=$(( (END_SEC - START_SEC) / 86400 ))
        echo "  Timespan: $DURATION_DAYS days" >> "$OUTPUT_FILE"
    fi
fi

echo -e "\nOutput file: $PWD/$OUTPUT_FILE" >> "$OUTPUT_FILE"

echo -e "\nSuccess! Compiled logs from $REPO_COUNT repositories to $OUTPUT_FILE"
echo "Project spans from ${EARLIEST_DATE:-N/A} to ${LATEST_DATE:-N/A}"
