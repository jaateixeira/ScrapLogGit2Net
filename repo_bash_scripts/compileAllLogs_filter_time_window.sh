#!/bin/bash
# compile_all_git_logs.sh - Minimalist AGL git log collector

set -eo pipefail

# Configuration
OUTPUT_FILE="agl_raw_logs_$(basename "$PWD")_$(git branch --show-current)_$(date +%Y%m%d_%H%M%S).txt.IN"
CURRENT_CHECKED_OUT_RELEASE=$(git branch --show-current)


# Console header
echo "=== AGL Git Log Collector ==="
echo "Started: $(date -u)"
echo "Output will contain only raw git log data"
echo "Processing all repositories..."
echo "Current checked out release = "$CURRENT_CHECKED_OUT_RELEASE

# Initialize counters
TOTAL_REPOS=0
PROCESSED_REPOS=0
FAILED_REPOS=0


# Function to process repositories and extract git log data
#!/bin/bash

# Function to process repositories and extract git log data within a date range
process_repositories() {
    local output_file="$1"
    local since="$2"
    local until="$3"

    # Check if the required parameters are provided
    if [[ -z "$output_file" || -z "$since" || -z "$until" ]]; then
        echo "Usage: process_repositories <output_file> <since> <until>"
        return 1
    fi

    # Initialize failure counter
    local failed_repos=0

    # Iterate over each repository using repo forall
    repo forall -c '
        # Only output the raw git log data to file
        {
            # echo -e "\n\n[START_REPO:$REPO_PROJECT]"
            git log \
            --since="'"$since"'" --until="'"$until"'" \
            --pretty=format:"==%an;%ae;%ad==" --name-only
            # echo -e "[END_REPO:$REPO_PROJECT]"
        } >> "'"$output_file"'"

        # Count success
        exit 0
    ' || {
        # Count failures
        failed_repos=$((failed_repos + 1))
    }

    # Output the number of failed repositories
    if [[ $failed_repos -eq 0 ]]; then
        echo "All repositories processed successfully."
    else
        echo "$failed_repos repositories failed to process."
    fi
}

# Example usage
# process_repositories "git_log_output.txt" "2023-01-01" "2023-12-31"

echo -e "See https://wiki.automotivelinux.org/schedule for docs in documentation"

# Check if CURRENT_CHECKED_OUT_RELEASE matches any of the specified values
if [[ "$CURRENT_CHECKED_OUT_RELEASE" == "albacore" ]]; then
    echo "CURRENT_CHECKED_OUT_RELEASE is albacore."
     process_repositories $OUTPUT_FILE 09-06-2015  2016-12-2
elif [[ "$CURRENT_CHECKED_OUT_RELEASE" == "blowfish" ]]; then
    echo "CURRENT_CHECKED_OUT_RELEASE is blowfish."
    process_repositories $OUTPUT_FILE 2016-12-2  2017-06-28
elif [[ "$CURRENT_CHECKED_OUT_RELEASE" == "chinook" ]]; then
    echo "CURRENT_CHECKED_OUT_RELEASE is chinook."
    process_repositories $OUTPUT_FILE  2017-06-28 2018-10-8
elif [[ "$CURRENT_CHECKED_OUT_RELEASE" == "dab" ]]; then
    echo "CURRENT_CHECKED_OUT_RELEASE is dab."
    process_repositories $OUTPUT_FILE  2018-10-8 2018-11-23
elif [[ "$CURRENT_CHECKED_OUT_RELEASE" == "eel" ]]; then
    echo "CURRENT_CHECKED_OUT_RELEASE is eel."
    process_repositories $OUTPUT_FILE  2018-11-23 2019-09-9
elif [[ "$CURRENT_CHECKED_OUT_RELEASE" == "flounder" ]]; then
    echo "CURRENT_CHECKED_OUT_RELEASE is flounder."
    process_repositories $OUTPUT_FILE  2019-09-9 2020-03-13
elif [[ "$CURRENT_CHECKED_OUT_RELEASE" == "guppy" ]]; then
    process_repositories $OUTPUT_FILE  2020-03-13 2020-05-4
elif [[ "$CURRENT_CHECKED_OUT_RELEASE" == "halibut" ]]; then
  echo "CURRENT_CHECKED_OUT_RELEASE is halibut."
  process_repositories $OUTPUT_FILE  2020-05-4 2021-06-14
elif [[ "$CURRENT_CHECKED_OUT_RELEASE" == "icefish" ]]; then
    echo "CURRENT_CHECKED_OUT_RELEASE is icefish."
    process_repositories $OUTPUT_FILE   2021-06-14 2022-08-23
elif [[ "$CURRENT_CHECKED_OUT_RELEASE" == "jellyfish" ]]; then
    echo "CURRENT_CHECKED_OUT_RELEASE is jellyfish."
    process_repositories $OUTPUT_FILE   2021-06-14 2022-08-23
elif [[ "$CURRENT_CHECKED_OUT_RELEASE" == "koi" ]]; then
    echo "CURRENT_CHECKED_OUT_RELEASE is koi."
    process_repositories $OUTPUT_FILE    2022-08-23 2023-05-9
elif [[ "$CURRENT_CHECKED_OUT_RELEASE" == "lamprey" ]]; then
    echo "CURRENT_CHECKED_OUT_RELEASE is lamprey."
    process_repositories $OUTPUT_FILE    2023-05-9 2023-09-19
elif [[ "$CURRENT_CHECKED_OUT_RELEASE" == "marlin" ]]; then
    echo "CURRENT_CHECKED_OUT_RELEASE is marlin."
    process_repositories $OUTPUT_FILE     2024-05-10 2024-11-28
elif [[ "$CURRENT_CHECKED_OUT_RELEASE" == "needlefish" ]]; then
    echo "CURRENT_CHECKED_OUT_RELEASE is needlefish."
    process_repositories $OUTPUT_FILE     2024-11-28 2025-03-24
elif [[ "$CURRENT_CHECKED_OUT_RELEASE" == "next" ]]; then
    echo "CURRENT_CHECKED_OUT_RELEASE is next."
    process_repositories $OUTPUT_FILE      2025-03-24 2025-04-1
elif [[ "$CURRENT_CHECKED_OUT_RELEASE" == "octopus" ]]; then
    echo "CURRENT_CHECKED_OUT_RELEASE is octopus."
    process_repositories $OUTPUT_FILE      2025-03-24 2025-04-1
elif [[ "$CURRENT_CHECKED_OUT_RELEASE" == "pike" ]]; then
    echo "CURRENT_CHECKED_OUT_RELEASE is pike."
    process_repositories $OUTPUT_FILE      2025-03-24 2025-04-1
elif [[ "$CURRENT_CHECKED_OUT_RELEASE" == "quillback" ]]; then
    echo "CURRENT_CHECKED_OUT_RELEASE is quillback."
    process_repositories $OUTPUT_FILE      2025-03-24 2025-04-1
elif [[ "$CURRENT_CHECKED_OUT_RELEASE" == "ricefish" ]]; then
    echo "CURRENT_CHECKED_OUT_RELEASE is ricefish."
    process_repositories $OUTPUT_FILE      2025-03-24 2025-04-1
elif [[ "$CURRENT_CHECKED_OUT_RELEASE" == "salmon" ]]; then
  process_repositories $OUTPUT_FILE      2025-03-24 2025-04-1
    echo "CURRENT_CHECKED_OUT_RELEASE is salmon."
else
    echo "CURRENT_CHECKED_OUT_RELEASE does not match any of the specified values."
fi




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