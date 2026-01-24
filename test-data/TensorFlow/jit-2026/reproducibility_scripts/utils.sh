#!/bin/bash

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to test configuration
test_config() {
    echo -e "${CYAN}=== Testing Configuration Variables ===${NC}"
    echo ""

    # Test the first 3 variables for file existence and execution
    local file_vars=("SCRAPLOG_SCRIPT" "FFV_NO_FI_GRAPHML_SCRIPT" "TRANSFORM_GRAPHML_SCRIPT")

    for var_name in "${file_vars[@]}"; do
        local file_path="${!var_name}"

        echo -e "${BLUE}Testing ${var_name}: ${NC}"
        echo -e "  Path: ${YELLOW}${file_path}${NC}"

        # Test 1: Check if file exists
        if [[ -f "$file_path" ]]; then
            echo -e "  File exists: ${GREEN}✓${NC}"
        else
            echo -e "  File exists: ${RED}✗${NC}"
            echo -e "  ${RED}ERROR: File not found!${NC}"
            continue
        fi

        # Test 2: Check if it's executable
        if [[ -x "$file_path" ]]; then
            echo -e "  Is executable: ${GREEN}✓${NC}"
        else
            echo -e "  Is executable: ${RED}✗${NC}"
            echo -e "  ${YELLOW}WARNING: File is not executable. Consider running 'chmod +x ${file_path}'${NC}"
        fi

        # Test 3: Check if it's a Python file
        if [[ "$file_path" == *.py ]] || head -n 1 "$file_path" 2>/dev/null | grep -q "^#!.*python"; then
            echo -e "  Python file: ${GREEN}✓${NC}"
        else
            echo -e "  Python file: ${YELLOW}?${NC}"
            echo -e "  ${YELLOW}Note: This may not be a Python script${NC}"
        fi

        echo ""
    done

    # Display the last 2 variables with color
    echo -e "${CYAN}=== Displaying Configuration Variables ===${NC}"
    echo ""

    echo -e "${MAGENTA}TOP10_ORG:${NC}"
    echo -e "${GREEN}${TOP10_ORG}${NC}"
    echo ""

    echo -e "${MAGENTA}COMPANIES_TO_IGNORE:${NC}"
    echo -e "${GREEN}${COMPANIES_TO_IGNORE}${NC}"
    echo ""

    echo -e "${CYAN}=== Configuration Test Complete ===${NC}"
}

# Function to validate git repository clone
is_valid_git_repository_clone() {
    local repo_path="$REPOSITORY_TO_MINE_PATH"

    echo -e "${CYAN}=== Testing Git Repository Clone ===${NC}"
    echo ""

    if [[ -z "$repo_path" ]]; then
        echo -e "${RED}ERROR: REPOSITORY_TO_MINE_PATH is not set${NC}"
        return 1
    fi

    echo -e "${BLUE}Testing repository path:${NC}"
    echo -e "  Path: ${YELLOW}${repo_path}${NC}"
    echo ""

    # Test 1: Check if it's a directory
    echo -e "${BLUE}Test 1: Checking if path is a directory...${NC}"
    if [[ -d "$repo_path" ]]; then
        echo -e "  Directory exists: ${GREEN}✓${NC}"
    else
        echo -e "  Directory exists: ${RED}✗${NC}"
        echo -e "  ${RED}ERROR: '$repo_path' is not a directory${NC}"
        return 1
    fi
    echo ""

    # Test 2: Check if it's a git repository
    echo -e "${BLUE}Test 2: Checking if it's a git repository...${NC}"
    if [[ -d "$repo_path/.git" ]]; then
        echo -e "  .git directory found: ${GREEN}✓${NC}"
    else
        echo -e "  .git directory found: ${RED}✗${NC}"
        echo -e "  ${RED}ERROR: '$repo_path' is not a git repository (no .git directory)${NC}"
        return 1
    fi
    echo ""

    # Test 3: Check git status
    echo -e "${BLUE}Test 3: Checking git status...${NC}"
    if git -C "$repo_path" status &>/dev/null; then
        echo -e "  Git status successful: ${GREEN}✓${NC}"
    else
        echo -e "  Git status successful: ${RED}✗${NC}"
        echo -e "  ${RED}ERROR: Cannot run git commands in '$repo_path'${NC}"
        return 1
    fi
    echo ""

    # Test 4: Check for git log (should have commits)
    echo -e "${BLUE}Test 4: Checking for commits...${NC}"
    local commit_count=$(git -C "$repo_path" log --oneline 2>/dev/null | wc -l)
    if [[ "$commit_count" -gt 0 ]]; then
        echo -e "  Has commits (${commit_count}): ${GREEN}✓${NC}"
    else
        echo -e "  Has commits: ${YELLOW}⚠${NC}"
        echo -e "  ${YELLOW}WARNING: Repository has no commits or git history${NC}"
    fi
    echo ""

    # Test 5: Check remote URL (if any)
    echo -e "${BLUE}Test 5: Checking for remote repository...${NC}"
    local remote_url=$(git -C "$repo_path" remote get-url origin 2>/dev/null)
    if [[ -n "$remote_url" ]]; then
        echo -e "  Remote URL found: ${GREEN}✓${NC}"
        echo -e "  Origin URL: ${YELLOW}${remote_url}${NC}"
    else
        echo -e "  Remote URL found: ${YELLOW}⚠${NC}"
        echo -e "  ${YELLOW}WARNING: No remote 'origin' configured (may be a local clone)${NC}"
    fi
    echo ""

    echo -e "${GREEN}✅ Git repository validation passed!${NC}"
    echo -e "${CYAN}Repository '$repo_path' is a valid git clone.${NC}"
    return 0
}


check_dir_writable() {
    local dir_path="$1"

    if [[ -z "$dir_path" ]]; then
        echo -e "${RED}Error: No directory path provided${NC}"
        return 1
    fi

    if [[ ! -d "$dir_path" ]]; then
        echo -e "${RED}Error: Directory '$dir_path' does not exist${NC}"
        return 1
    fi

    if [[ ! -w "$dir_path" ]]; then
        echo -e "${RED}Error: Directory '$dir_path' is not writable${NC}"
        return 1
    fi

    echo -e "${GREEN}Success: Directory '$dir_path' exists and is writable${NC}"
    return 0
}


select_files_for_processing() {
    local search_dir="$1"
    local max_files=20


    echo -e "${CYAN}════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}        Select Files for Network Processing${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════${NC}"

    # Check if directory exists
    if [[ ! -d "$search_dir" ]]; then
        echo -e "${RED}✗ ERROR: Directory '$search_dir' does not exist${NC}"
        return 1
    fi

    echo -e "${BLUE}Searching in: ${YELLOW}$search_dir${NC}"

    # Find files ending with .IN.TXT (case insensitive)
    local files=()
    while IFS= read -r -d '' file; do
        files+=("$file")
        if [[ ${#files[@]} -ge $max_files ]]; then
            break
        fi
    done < <(find "$search_dir" -maxdepth 2 -type f -iname "*.IN.TXT" -print0 2>/dev/null)

    # Check if any files were found
    if [[ ${#files[@]} -eq 0 ]]; then
        echo -e "${YELLOW}⚠ No files ending with '.IN.TXT' found in $search_dir${NC}"
        return 1
    fi

    echo -e "${GREEN}✓ Found ${#files[@]} file(s)${NC}"
    echo ""

    # Display files with numbers
    echo -e "${MAGENTA}Available files:${NC}"
    local i=1
    for file in "${files[@]}"; do
        local file_name=$(basename "$file")
        local file_dir=$(dirname "$file")
        local file_size=$(du -h "$file" 2>/dev/null | cut -f1 || echo "unknown")
        local line_count=$(wc -l < "$file" 2>/dev/null || echo "0")
        local mod_date=$(date -r "$file" "+%Y-%m-%d %H:%M" 2>/dev/null || echo "unknown")

        echo -e "${BLUE}[$i] ${YELLOW}$file_name${NC}"
        echo -e "    Directory: ${YELLOW}$file_dir${NC}"
        echo -e "    Size: ${GREEN}$file_size${NC} | Lines: ${GREEN}$line_count${NC} | Modified: ${GREEN}$mod_date${NC}"

        # Show first line as preview
        local first_line=$(head -1 "$file" 2>/dev/null | cut -c1-80)
        if [[ -n "$first_line" ]]; then
            echo -e "    Preview: ${YELLOW}$first_line...${NC}"
        fi
        echo ""
        ((i++))
    done

    # Ask user for selection
    echo -e "${MAGENTA}Select files to process with ScrapLogGit2Net:${NC}"
    echo -e "${BLUE}Options:${NC}"
    echo -e "  ${GREEN}all${NC}      - Process all files"
    echo -e "  ${GREEN}1,3,5${NC}    - Process specific files (comma-separated)"
    echo -e "  ${GREEN}1-3${NC}      - Process a range"
    echo -e "  ${GREEN}none${NC}     - Skip processing"
    echo -e "  ${GREEN}quit${NC}     - Exit function"
    echo ""

    while true; do
        echo -e "${BLUE}Enter your selection: ${NC}"
        read -r selection

        # Convert to lowercase
        selection_lower=$(echo "$selection" | tr '[:upper:]' '[:lower:]')

        case "$selection_lower" in
            "all")
                selected_files=("${files[@]}")
                echo -e "${GREEN}✓ Selected all ${#files[@]} files${NC}"
                break
                ;;
            "none")
                echo -e "${YELLOW}⚠ No files selected${NC}"
                selected_files=()
                return 0
                ;;
            "quit")
                echo -e "${YELLOW}Exiting selection${NC}"
                return 1
                ;;
            *)
                # Validate the selection
                if validate_selection "$selection" "${#files[@]}"; then
                    mapfile -t selected_indices < <(parse_selection "$selection")
                    selected_files=()

                    for idx in "${selected_indices[@]}"; do
                        selected_files+=("${files[$((idx-1))]}")
                    done

                    echo -e "${GREEN}✓ Selected ${#selected_files[@]} file(s)${NC}"
                    break
                else
                    echo -e "${RED}✗ Invalid selection. Please try again.${NC}"
                fi
                ;;
        esac
    done

    # Show confirmation
    echo ""
    echo -e "${MAGENTA}Selected files:${NC}"
    for i in "${!selected_files[@]}"; do
        echo -e "  ${GREEN}$((i+1))${NC}. ${YELLOW}$(basename "${selected_files[$i]}")${NC}"
        echo -e "      Path: ${BLUE}${selected_files[$i]}${NC}"
    done

    echo ""
    echo -e  "${BLUE}Confirm processing these files? (y/n): ${NC}"
    read -r confirm

    if [[ "$confirm" =~ ^[Yy]([Ee][Ss])?$ ]]; then
        echo -e "${GREEN}✓ Proceeding with processing${NC}"
        # Return the selected files as an array
        echo "${selected_files[@]}"
        return 0
    else
        echo -e "${YELLOW}⚠ Selection cancelled${NC}"
        return 1
    fi
}

# Helper function to validate selection
validate_selection() {
    local selection="$1"
    local max_num="$2"

    # Remove spaces
    selection=$(echo "$selection" | tr -d ' ')

    # Check if it's empty
    [[ -z "$selection" ]] && return 1

    # Check for range format (e.g., 1-3)
    if [[ "$selection" =~ ^[0-9]+-[0-9]+$ ]]; then
        local start=${selection%-*}
        local end=${selection#*-}
        if [[ $start -le 0 || $end -gt $max_num || $start -gt $end ]]; then
            return 1
        fi
        return 0
    fi

    # Check for comma-separated list
    if [[ "$selection" =~ ^[0-9]+(,[0-9]+)*$ ]]; then
        IFS=',' read -ra nums <<< "$selection"
        for num in "${nums[@]}"; do
            if [[ $num -le 0 || $num -gt $max_num ]]; then
                return 1
            fi
        done
        return 0
    fi

    # Check for single number
    if [[ "$selection" =~ ^[0-9]+$ ]]; then
        if [[ $selection -ge 1 && $selection -le $max_num ]]; then
            return 0
        fi
    fi

    return 1
}

# Helper function to parse selection into indices
parse_selection() {
    local selection="$1"

    # Remove spaces
    selection=$(echo "$selection" | tr -d ' ')

    # Handle range
    if [[ "$selection" =~ ^[0-9]+-[0-9]+$ ]]; then
        local start=${selection%-*}
        local end=${selection#*-}
        seq "$start" "$end"
        return
    fi

    # Handle comma-separated or single number
    echo "$selection" | tr ',' '\n'
}




print_selected_files() {
    local selected_files=("$@")  # Get all arguments as an array

    # Color definitions
    local RED='\033[0;31m'
    local GREEN='\033[0;32m'
    local YELLOW='\033[1;33m'
    local BLUE='\033[0;34m'
    local MAGENTA='\033[0;35m'
    local CYAN='\033[0;36m'
    local NC='\033[0m' # No Color

    # Check if array is empty
    if [[ ${#selected_files[@]} -eq 0 ]]; then
        echo -e "${YELLOW}⚠ No files selected${NC}"
        return 1
    fi

    echo -e "${CYAN}════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}        Selected Files for Processing${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}Total files: ${GREEN}${#selected_files[@]}${NC}"
    echo ""

    local total_size_bytes=0
    local total_lines=0

    # Loop through files with index
    for i in "${!selected_files[@]}"; do
        local file="${selected_files[$i]}"
        local file_num=$((i+1))

        # Get file info
        local file_name=$(basename "$file")
        local file_dir=$(dirname "$file")

        # Get file size in human readable format and bytes
        local file_size_human=""
        local file_size_bytes=0

        if [[ -f "$file" ]]; then
            # Human readable size (KB, MB, GB)
            file_size_human=$(du -h "$file" 2>/dev/null | cut -f1)

            # Size in bytes (for total calculation)
            file_size_bytes=$(stat -c%s "$file" 2>/dev/null || wc -c < "$file" 2>/dev/null || echo 0)

            # Line count
            local line_count=$(wc -l < "$file" 2>/dev/null || echo "0")
            total_lines=$((total_lines + line_count))
        else
            file_size_human="(file not found)"
            file_size_bytes=0
        fi

        # Add to total size
        total_size_bytes=$((total_size_bytes + file_size_bytes))

        # Convert bytes to human readable for display
        local size_display="$file_size_human"
        if [[ $file_size_bytes -gt 0 ]]; then
            size_display="$file_size_human (${file_size_bytes} bytes)"
        fi

        # Print file info with formatting
        echo -e "${MAGENTA}File #${file_num}:${NC}"
        echo -e "  ${BLUE}Name:${NC}     ${YELLOW}$file_name${NC}"
        echo -e "  ${BLUE}Path:${NC}     ${CYAN}$file_dir/${NC}"
        echo -e "  ${BLUE}Size:${NC}     ${GREEN}$size_display${NC}"

        # Show additional info if file exists
        if [[ -f "$file" ]]; then
            local mod_time=$(date -r "$file" "+%Y-%m-%d %H:%M:%S" 2>/dev/null || echo "unknown")
            echo -e "  ${BLUE}Modified:${NC} ${YELLOW}$mod_time${NC}"
            echo -e "  ${BLUE}Lines:${NC}    ${GREEN}$line_count${NC}"

            # Show first commit as preview
            local first_line=$(head -1 "$file" 2>/dev/null | cut -c1-60)
            if [[ -n "$first_line" ]]; then
                echo -e "  ${BLUE}Preview:${NC}  ${YELLOW}$first_line...${NC}"
            fi
        else
            echo -e "  ${RED}⚠ File not found${NC}"
        fi

        echo ""
    done

    # Print summary
    echo -e "${CYAN}════════════════════════════════════════════════════${NC}"
    echo -e "${MAGENTA}Summary of files to be processed:${NC}"

    # Convert total bytes to human readable
    local total_size_human=""
    if [[ $total_size_bytes -lt 1024 ]]; then
        total_size_human="${total_size_bytes} bytes"
    elif [[ $total_size_bytes -lt 1048576 ]]; then
        total_size_human="$((total_size_bytes / 1024)) KB"
    elif [[ $total_size_bytes -lt 1073741824 ]]; then
        total_size_human="$((total_size_bytes / 1048576)) MB"
    else
        total_size_human="$((total_size_bytes / 1073741824)) GB"
    fi

    echo -e "  ${BLUE}Total files:${NC}    ${GREEN}${#selected_files[@]}${NC}"
    echo -e "  ${BLUE}Total size:${NC}     ${GREEN}$total_size_human${NC}"
    echo -e "  ${BLUE}Total lines:${NC}    ${GREEN}$total_lines${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════${NC}"
}




# Example usage after sourcing utils.sh:
# source config.cfg
# run_all_tests
# OR test specific function:
# is_valid_git_repository_clone