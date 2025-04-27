#!/bin/bash

# Check if the correct number of arguments is provided
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <log_file> <since_date> <until_date>"
    echo "Dates should be in YYYY-MM-DD format."
    exit 1
fi

LOG_FILE=$1
SINCE_DATE=$2
UNTIL_DATE=$3
FILTERED_LOG_FILE="${LOG_FILE%.txt}.filtered.txt"

# Check if the log file exists
if [ ! -f "$LOG_FILE" ]; then
    echo "Error: File '$LOG_FILE' not found!"
    exit 1
fi

# Function to check if a date is outside the range
is_outside_range() {
    local date_str="$1"
    local since="$2"
    local until="$3"

    # Extract the date part and check if it is outside the range
    commit_date=$(echo "$date_str" | awk -F ';' '{print $3}' | xargs -I{} date -d "{}" +"%Y-%m-%d")

    if [[ "$commit_date" < "$since" || "$commit_date" > "$until" ]]; then
        return 0
    else
        return 1
    fi
}

# Open the filtered log file for writing
exec > "$FILTERED_LOG_FILE"

# Read the log file line by line
while IFS= read -r line; do
    # Check if the line is a commit separator
    if [[ "$line" == "=="* ]]; then
        # Check if the commit date is outside the range
        if is_outside_range "$line" "$SINCE_DATE" "$UNTIL_DATE"; then
            echo "$line"
            # Print the subsequent lines until the next commit separator
            while IFS= read -r next_line; do
                if [[ "$next_line" == "=="* ]]; then
                    break
                fi
                echo "$next_line"
            done
        else
            # Skip lines until the next commit separator
            while IFS= read -r next_line; do
                if [[ "$next_line" == "=="* ]]; then
                    break
                fi
            done
        fi
    fi
done < "$LOG_FILE"

# Close the filtered log file
exec > /dev/tty

echo "Filtered log file created: $FILTERED_LOG_FILE"
