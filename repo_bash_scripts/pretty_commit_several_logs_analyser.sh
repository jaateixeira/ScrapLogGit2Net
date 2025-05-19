#!/bin/bash

# Check if at least one log file is provided
if [ "$#" -lt 1 ]; then
    echo "Usage: $0 <commit_log_file1> <commit_log_file2> ..."
    exit 1
fi

# Color codes
YELLOW='\033[1;33m'
GREEN='\033[1;32m'
NC='\033[0m' # No Color

# Function to extract shortened name
get_short_name() {
    local filename=$(basename "$1")
    # Extract 'chinook' from patterns like:
    # gl_raw_logs_meta-agl_chinook_20250427_171649.txt.IN_chinook.txt.IN
    # or gl_raw_logs_meta-agl_halibut_*.txt
    if [[ $filename =~ gl_raw_logs_meta-agl_([^_]+)_ ]]; then
        echo "${BASH_REMATCH[1]}"
    else
        # Fallback to basename without extension
        basename "${filename%.*}"
    fi
}

# Function to transform datetime to YYYY-MM-DD
transform_datetime() {
    local datetime_str="$1"
    echo "$datetime_str" | awk '{
        month_index = match("JanFebMarAprMayJunJulAugSepOctNovDec", $2)
        month = sprintf("%02d", (month_index+2)/3)
        year = $5
        day = $3
        printf "%s-%s-%s", year, month, day
    }'
}

# Print header
printf "%-15s %-15s %-25s %-25s\n" "Release" "Total Commits" "First Commit" "Last Commit"
echo "-----------------------------------------------------------------------------------"

# Process each log file
for LOG_FILE in "$@"; do
    # Verify file exists
    if [ ! -f "$LOG_FILE" ]; then
        echo -e "Error: File '$LOG_FILE' not found!" >&2
        continue
    fi

    # Get shortened name
    release_name=$(get_short_name "$LOG_FILE")

    # Initialize variables
    total_commits=0
    first_commit_date=""
    last_commit_date=""
    first_commit_raw=""
    last_commit_raw=""

    # Read the file
    while IFS= read -r line; do
        if [[ "$line" == "=="* ]]; then
            ((total_commits++))

            commit_date_raw=$(echo "$line" | cut -d ';' -f 3 | tr -d '==')

            if [ -z "$first_commit_raw" ]; then
                first_commit_raw="$commit_date_raw"
            fi
            last_commit_raw="$commit_date_raw"
        fi
    done < "$LOG_FILE"

    # Skip if no commits found
    if [ "$total_commits" -eq 0 ]; then
        printf "%-15s %-15s %-25s %-25s\n" \
            "$release_name" \
            "0" \
            "N/A" \
            "N/A"
        continue
    fi

    # Transform dates
    first_commit_date=$(transform_datetime "$first_commit_raw")
    last_commit_date=$(transform_datetime "$last_commit_raw")

    # Print results
    printf "%-15s %-15s ${YELLOW}%-25s${NC} ${GREEN}%-25s${NC}\n" \
        "$release_name" \
        "$total_commits" \
        "$first_commit_date" \
        "$last_commit_date"
done

