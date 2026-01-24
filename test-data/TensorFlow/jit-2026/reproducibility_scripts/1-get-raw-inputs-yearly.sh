#!/bin/bash

# Gets the raw git logs from TensorFlow#
# Those will be the main input for ScrapLogGit2Net
# Year after year


echo  -e "1-get-raw-inputs.sh  - Gets the raw git logs from TensorFlow - year after year"

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

output_file="${DIR_4_RAW_GIT_LOGS}/${PROJECT_TO_MINE}_${today}_all.IN.TXT"


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


echo -e "${CYAN}════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}        Yearly Network Extraction${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════${NC}"

# Ask user if they want to extract yearly logs
echo -e "${BLUE}Do you want to extract yearly networks? (y/n): ${NC}"
read extract_yearly_response

if [[ "$extract_yearly_response" =~ ^[Yy]([Ee][Ss])?$ ]]; then
    # Create yearly logs directory
    yearly_dir="${DIR_4_RAW_GIT_LOGS}/yearly_logs"
    echo -e "${BLUE}Creating yearly logs directory: ${YELLOW}$yearly_dir${NC}"

    # Try to create the directory with error handling
    if mkdir -p "$yearly_dir" 2>/dev/null; then
        echo -e "${GREEN}✓ Directory created successfully${NC}"
    else
        echo -e "${RED}✗ Failed to create yearly logs directory${NC}"
        exit 1
    fi
else
  echo -e "${RED}✗ Aborted by the user - no need for  network year after year${NC}"
  exit 1
fi

    # Check if directory is writable
    if [ -w "$yearly_dir" ]; then
        echo -e "${GREEN}✓ Directory is writable${NC}"
    else
        echo -e "${RED}✗ Directory is not writable: $yearly_dir${NC}"
        exit 1
    fi


    echo -e "${MAGENTA}── Determining project timeline ──${NC}"

    # Get the first commit date in the repository
    first_commit_date=$(git -C "$repo_path" log --reverse --pretty=format:"%ad" --date=short | head -1)

    if [[ -z "$first_commit_date" ]]; then
        echo -e "${RED}✗ ERROR: Could not get first commit date${NC}"
        exit 1
    fi

    first_year=$(echo "$first_commit_date" | cut -d'-' -f1)
    current_year=$(date +"%Y")

    echo -e "${GREEN}✓ First commit: ${YELLOW}$first_commit_date${NC}"
    echo -e "${GREEN}✓ First year: ${YELLOW}$first_year${NC}"
    echo -e "${GREEN}✓ Current year: ${YELLOW}$current_year${NC}"

    # Calculate total years
    total_years=$((current_year - first_year + 1))
    echo -e "${BLUE}Total years to extract: ${YELLOW}$total_years${NC}"
    echo ""

    # Ask for confirmation
    echo  -e "${YELLOW}This will create ${total_years} yearly files. Continue? (y/n): ${NC}"
    read confirmation

    if [[ ! "$confirmation" =~ ^[Yy]([Ee][Ss])?$ ]]; then
        echo -e "${YELLOW}Yearly extraction cancelled${NC}"
        exit 0
    fi

    echo -e "${MAGENTA}── Extracting yearly logs ──${NC}"

    success_count=0
    skip_count=0

    # Loop through each year from first to current
    for ((year=first_year; year<=current_year; year++)); do
        year_start="${year}-01-01"
        year_end="${year}-12-31"

        # For the first year, start from the actual first commit date
        if [[ "$year" == "$first_year" ]]; then
            year_start="$first_commit_date"
        fi

        # For current year, end today
        if [[ "$year" == "$current_year" ]]; then
            today=$(date +"%Y-%m-%d")
            year_end="$today"
        fi

        output_file="${yearly_dir}/${PROJECT_TO_MINE}_${year}_network.IN.TXT"

        echo -e "${BLUE}Year ${YELLOW}$year${BLUE} (${year_start} to ${year_end})${NC}"

        # Check if file already exists
        if [[ -f "$output_file" ]]; then
            echo -e "${YELLOW}  ⚠ File already exists${NC}"
            printf "%s" "${YELLOW}  Overwrite? (y/n/skip): ${NC}"
            read response

            if [[ "$response" =~ ^[Nn][Oo]?$ ]]; then
                echo -e "${YELLOW}  Skipping $year (file kept)${NC}"
                ((skip_count++))
                continue
            elif [[ "$response" =~ ^[Ss]([Kk][Ii][Pp])?$ ]]; then
                echo -e "${YELLOW}  Skipping $year${NC}"
                ((skip_count++))
                continue
            fi
        fi

        # Run git log for the specific year
        echo -e "${BLUE}  Extracting...${NC}"

        if git -C "$repo_path" log \
            --since="$year_start 00:00:00" \
            --until="$year_end 23:59:59" \
            --pretty=format:"==%an;%ae;%ad==" \
            --name-only \
            > "$output_file" 2>&1; then

            # Check if file has content
            if [[ -s "$output_file" ]]; then
                line_count=$(wc -l < "$output_file")
                file_size=$(du -h "$output_file" 2>/dev/null | cut -f1 || echo "0")
                echo -e "${GREEN}  ✓ Extracted ${line_count} lines (${file_size})${NC}"
                ((success_count++))
            else
                echo -e "${YELLOW}  ⚠ No commits found for $year${NC}"
                rm "$output_file" 2>/dev/null  # Remove empty file
                ((skip_count++))
            fi
        else
            echo -e "${RED}  ✗ Failed to extract $year${NC}"
            ((skip_count++))
        fi

        echo ""
    done

    # Summary
    echo -e "${MAGENTA}── Yearly Extraction Summary ──${NC}"
    echo -e "${BLUE}Total years processed: ${YELLOW}$total_years${NC}"
    echo -e "${GREEN}Successfully extracted: ${YELLOW}$success_count${NC}"
    echo -e "${YELLOW}Skipped/failed: ${YELLOW}$skip_count${NC}"

    # List generated files
    echo -e "${BLUE}Generated files in ${YELLOW}$yearly_dir/${NC}:"
    if ls -la "$yearly_dir/"*.IN.TXT 2>/dev/null | grep -q .; then
        ls -lh "$yearly_dir/"*.IN.TXT 2>/dev/null | while read -r line; do
            echo -e "${YELLOW}  $line${NC}"
        done
    else
        echo -e "${YELLOW}  No yearly files generated${NC}"
    fi

    echo -e "${CYAN}════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}✅ Yearly extraction completed${NC}"
    echo ""

    # Offer to create a summary file
    printf "%s" "${BLUE}Create summary of yearly files? (y/n): ${NC}"
    read create_summary

    if [[ "$create_summary" =~ ^[Yy]([Ee][Ss])?$ ]]; then
        summary_file="${DIR_4_RAW_GIT_LOGS}/yearly_summary_$(date +%Y%m%d).txt"
        echo -e "${BLUE}Creating summary: ${YELLOW}$summary_file${NC}"

        echo "Yearly Git Log Extraction Summary" > "$summary_file"
        echo "Generated on: $(date)" >> "$summary_file"
        echo "Project: $PROJECT_TO_MINE" >> "$summary_file"
        echo "Repository: $REPOSITORY_TO_MINE_PATH" >> "$summary_file"
        echo "First year: $first_year" >> "$summary_file"
        echo "Current year: $current_year" >> "$summary_file"
        echo "==========================================" >> "$summary_file"
        echo "" >> "$summary_file"

        for file in "$yearly_dir/"*.IN.TXT; do
            if [[ -f "$file" ]]; then
                year=$(basename "$file" | grep -o '[0-9]\{4\}')
                line_count=$(wc -l < "$file" 2>/dev/null || echo "0")
                file_size=$(du -h "$file" 2>/dev/null | cut -f1 || echo "0")
                echo "$year: $line_count lines, $file_size" >> "$summary_file"
            fi
        done

        echo -e "${GREEN}✓ Summary created: $summary_file${NC}"
    fi
else
    echo -e "${YELLOW}Yearly extraction skipped by user${NC}"
fi

echo -e "${CYAN}════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ All operations completed successfully${NC}"
echo ""
echo -e "Next steps:"
echo -e "1. Run scrapLog.py to extract networks"

exit 0


