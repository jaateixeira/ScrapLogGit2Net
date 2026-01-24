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



# Example usage after sourcing utils.sh:
# source config.cfg
# run_all_tests
# OR test specific function:
# is_valid_git_repository_clone