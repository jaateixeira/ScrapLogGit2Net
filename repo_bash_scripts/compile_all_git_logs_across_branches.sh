#!/bin/bash
# checkout_and_log_agl_releases.sh

set -eo pipefail

# Configuration
RELEASE_BRANCHES=(
    albacore blowfish chinook dab eel flounder guppy halibut
    icefish jellyfish koi lamprey marlin master needlefish next
    octopus pike quillback ricefish salmon
)
LOG_SCRIPT="/home/apolinex/rep_clones/own-tools/ScrapLogGit2Net/repo_bash_scripts/compileAllLogs.sh"  # Path to your log compilation script
WORKSPACE_ROOT="$PWD"  # Change if needed

# Validate the log script exists
if [[ ! -f "$LOG_SCRIPT" ]]; then
    echo "Error: Log script $LOG_SCRIPT not found!" >&2
    exit 1
fi

# Main processing
for branch in "${RELEASE_BRANCHES[@]}"; do
    echo -e "\n\033[1;34m=== Processing branch: $branch ===\033[0m"
    
    # Checkout the branch across all repos
    checkout_cmd="repo forall -c 'git checkout --quiet $branch || echo \"[WARN] Failed to checkout $branch in \$REPO_PROJECT\"'"
    echo -e "\033[1;33mExecuting: $checkout_cmd\033[0m"
    
    if ! eval "$checkout_cmd"; then
        echo -e "\033[1;31m[ERROR] Checkout failed for branch $branch\033[0m" >&2
        continue  # Skip to next branch instead of exiting
    fi
    
    # Verify branch consistency
    echo -e "\n\033[1;32mVerifying branch consistency...\033[0m"
    repo forall -c '
        current=$(git branch --show-current 2>/dev/null || echo "DETACHED")
        if [[ "$current" != "'"$branch"'" ]]; then
            echo "[WARN] $REPO_PROJECT is on $current (expected $branch)"
        fi
    '
    
    # Compile logs
    echo -e "\n\033[1;36mCompiling logs for $branch...\033[0m"
    "$LOG_SCRIPT" || {
        echo -e "\033[1;31m[ERROR] Log compilation failed for $branch\033[0m" >&2
        continue
    }
    
    # Rename output file with branch name
    latest_log=$(ls -t agl_git_logs_*.txt | head -1)
    if [[ -n "$latest_log" ]]; then
        new_name="${latest_log%.txt}_${branch}.txt"
        mv "$latest_log" "$new_name"
        echo -e "\033[1;32mLogs saved to: $new_name\033[0m"
    fi
done

echo -e "\n\033[1;35m=== All branches processed ===\033[0m"
repo forall -c 'git branch --show-current' | sort | uniq -c | awk '{printf "%-10s: %2d repos\n", $2, $1}'


