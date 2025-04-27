#!/bin/bash

# Check if at least one log file is provided as an argument
if [ "$#" -lt 1 ]; then
    echo "Usage: $0 <commit_log_file1> <commit_log_file2> ..."
    exit 1
fi

# Function to format date
format_date() {
    local date_str="$1"
    # Extract the date part and format it
    echo "$date_str" | grep -oP '(?<===).*(?==)' | xargs -I{} date -d "{}" +"%Y-%m-%d"
}

# Print header for the table
echo -e "Log File\tTotal Commits\tFirst Commit Date\tLast Commit Date"

# Loop through each log file provided as an argument
for LOG_FILE in "$@"; do
    # Check if the log file exists
    if [ ! -f "$LOG_FILE" ]; then
        echo "Error: File '$LOG_FILE' not found!"
        continue
    fi

    # Initialize variables
    total_commits=0
    first_commit=""
    last_commit=""

    # Read the log file line by line
    while IFS= read -r line; do
        # Check if the line is a commit separator
        if [[ "$line" == "=="* ]]; then
            # Increment the commit count
            ((total_commits++))

            # Update the last commit
            last_commit="$line"

            # If it's the first commit, update the first commit
            if [ -z "$first_commit" ]; then
                first_commit="$line"
            fi
        fi
    done < "$LOG_FILE"

    # Check if any commits were found
    if [ "$total_commits" -eq 0 ]; then
        echo -e "$LOG_FILE\tNo commits found"
        continue
    fi

    # Extract and format dates from the first and last commits
    first_commit_date=$(format_date "$first_commit")
    last_commit_date=$(format_date "$last_commit")

    # Print the results in a tabulated format
    echo -e "$LOG_FILE\t$total_commits\t\e[32m$first_commit_date\e[0m\t\e[32m$last_commit_date\e[0m"
done

