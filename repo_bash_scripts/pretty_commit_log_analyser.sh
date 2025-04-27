#!/bin/bash
# pretty_commit_log_analyser.sh - Analyzes Git commit logs in custom format


echo pretty_commit_log_analyser.sh - Analyzes Git commit logs in custom format used by ScrapLogGit2Net


#!/bin/bash

# Check if the log file is provided as an argument
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <commit_log_file>"
    exit 1
fi

LOG_FILE=$1

# Check if the log file exists
if [ ! -f "$LOG_FILE" ]; then
    echo "Error: File '$LOG_FILE' not found!"
    exit 1
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
    echo "No commits found in the log file."
    exit 1
fi


# Extract dates from the first and last commits
first_commit_date=$(echo "$first_commit" | cut -d ';' -f 3)
last_commit_date=$(echo "$last_commit" | cut -d ';' -f 3)



# Print the results
echo "Total number of commits: $total_commits"

# Print the results
echo "Total number of commits: $total_commits"
echo "Last commit (newest): $last_commit"
echo "First commit (oldest): $first_commit"
echo -e "Last commit date (newest): \e[32m$last_commit_date\e[0m"
echo -e "First commit date (oldest): \e[32m$first_commit_date\e[0m"


