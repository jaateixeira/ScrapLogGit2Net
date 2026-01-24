#!/bin/bash

# Gets the raw git logs from TensorFlow#
# Those will be the main input for ScrapLogGit2Net



echo  -e "1-get-raw-inputs.sh  - Gets the raw git logs from TensorFlow"

if [ ! "$BASH_VERSION" ] ; then
    echo "Please do not use sh to run this script ($0), just execute it directly" 1>&2
    exit 1
fi



if [ ! "$BASH_VERSION" ] ; then
    exec /bin/bash "$0" "$@"
fi



source config.cfg
source utils.sh

REPOSITORY_TO_MINE_PATH="./tensorflow"

test_config
is_valid_git_repository_clone

echo -e "${CYAN}Checking $DIR_4_RAW_GIT_LOGS${NC}"

    # Check if directory exists
    if [[ ! -d "$DIR_4_RAW_GIT_LOGS" ]]; then
        echo -e "${YELLOW}Directory '$DIR_4_RAW_GIT_LOGS' does not exist.${NC}"

        # Ask user if they want to create it
        echo -e "${BLUE}Do you want to create this directory? (y/n): ${NC}"
        read -r response

        if [[ "$response" =~ ^[Yy]([Ee][Ss])?$ ]]; then
            echo -e "${CYAN}Creating directory: $DIR_4_RAW_GIT_LOGS${NC}"

            # Try to create the directory
            if mkdir -p "$DIR_4_RAW_GIT_LOGS"; then
                echo -e "${GREEN}✓ Directory created successfully${NC}"
            else
                echo -e "${RED}✗ Failed to create directory${NC}"
                return 1
            fi
        else
            echo -e "${RED}✗ Directory not created. Cannot proceed without directory.${NC}"
            return 1
        fi
    fi

check_dir_writable "$DIR_4_RAW_GIT_LOGS"


repo_path="$REPOSITORY_TO_MINE_PATH"
#output_file="${PROJECT_TO_MINE}_all.IN.TXT"  # Optional output file parameter

today=$(date +"%Y-%m-%d")

output_file="${DIR_4_RAW_GIT_LOGS}${PROJECT_TO_MINE}_${today}_all.IN.TXT"


    echo -e "${CYAN}════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}        Git Log Extraction Process${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════${NC}"

    # Check if repository path is set
    if [[ -z "$repo_path" ]]; then
        echo -e "${RED}✗ ERROR: REPOSITORY_TO_MINE_PATH is not set${NC}"
        return 1
    fi

    echo -e "${BLUE} Repository path: ${YELLOW}$repo_path${NC}"
    echo -e "${BLUE} Output dir: ${YELLOW}$DIR_4_RAW_GIT_LOGS ${NC}"
    echo -e "${BLUE} Output file : ${YELLOW}$output_file${NC}"

    # Check if directory exists and is a git repo
    if [[ ! -d "$repo_path/.git" ]]; then
        echo -e "${RED}✗ ERROR: Not a git repository: $repo_path${NC}"
        return 1
    fi

    echo -e "${GREEN}✓ Valid git repository found${NC}"

    # Create the git log command
    git_cmd="git -C \"$repo_path\" log --pretty=format:\"==%an;%ae;%ad==\" --name-only > $output_file"
    echo -e "${BLUE}Running command:${NC}"
    echo -e "${YELLOW}$git_cmd${NC}"
    echo ""

    # Run git log command
    echo -e "${MAGENTA}── Extracting git log data ──${NC}"

    # Simple check with overwrite/cancel
if [[ -n "$output_file" ]]; then
    echo -e "${BLUE}Output will be saved to: ${YELLOW}$output_file${NC}"
    echo ""

    if [[ -f "$output_file" ]]; then
        echo -e "${YELLOW}⚠ Warning: File already exists!${NC}"
        echo -e "${YELLOW}  $output_file${NC}"

        file_size=$(du -h "$output_file" 2>/dev/null | cut -f1)
        echo -e "${BLUE}  Size: ${YELLOW}$file_size${NC}"
        echo ""

        read -p "Overwrite? (y/n): " overwrite_response

        if [[ ! "$overwrite_response" =~ ^[Yy]([Ee][Ss])?$ ]]; then
            echo -e "${RED}✗ Operation cancelled${NC}"
            exit 1
        fi

        echo -e "${YELLOW}Overwriting existing file...${NC}"
        echo ""
    fi
fi

   # Execute the command
    echo -e "${BLUE}Running...${NC}"

    # Option 2: Direct execution (recommended)
    if git -C "$repo_path" log --pretty=format:"==%an;%ae;%ad==" --name-only > "$output_file" 2>&1; then
        echo -e "${GREEN}✓ Command completed${NC}"
        exit_code=0
    else
        echo -e "${RED}✗ Command failed with code: 1 (error)${NC}"

        exit 1
    fi


    echo ""
    echo -e "${MAGENTA}── Results ──${NC}"

    # Check the results
    if [[ $exit_code -eq 0 ]]; then
        echo -e "${GREEN}✓ Git log command executed successfully${NC}"

        if [[ -n "$output_file" ]]; then
            # Count lines in output file
            if [[ -f "$output_file" ]]; then
                line_count=$(wc -l < "$output_file")
                file_size=$(du -h "$output_file" | cut -f1)

                echo -e "${GREEN}✓ Output saved to: $output_file${NC}"
                echo -e "${BLUE}  File size: ${YELLOW}$file_size${NC}"
                echo -e "${BLUE}  Line count: ${YELLOW}$line_count${NC}"

                # Show sample of output
                if [[ $line_count -gt 0 ]]; then
                    echo -e "${BLUE}  First few lines:${NC}"
                    echo -e "${YELLOW}$(head -5 "$output_file")${NC}"
                    echo -e "${YELLOW}...${NC}"
                else
                    echo -e "${YELLOW}⚠ Warning: Output file is empty${NC}"
                fi
            else
                echo -e "${RED}✗ ERROR: Output file was not created${NC}"
                exit 1
            fi
        fi
    else
        echo -e "${RED}✗ ERROR: Git log command failed with exit code: $exit_code${NC}"

        # Try to get error details
        if [[ -n "$output_file" && -f "$output_file" ]]; then
            echo -e "${RED}Error output:${NC}"
            tail -10 "$output_file" | while IFS= read -r line; do
                echo -e "${RED}  $line${NC}"
            done
        fi


    fi

    echo -e "${CYAN}════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}✅ Git log extraction completed successfully${NC}"

echo -e "you can now transform them year by year"
exit 0


