#!/bin/bash


if [ ! "$BASH_VERSION" ] ; then
    echo "Please do not use sh to run this script ($0), just execute it directly" 1>&2
    exit 1
fi



if [ ! "$BASH_VERSION" ] ; then
    exec /bin/bash "$0" "$@"
fi


source config.cfg


source config.cfg
source utils.sh


test_config


DIR_4_RAW_GIT_LOGS="../raw-inputs"


echo -e "${CYAN}Checking if directory with raw inputs exist"
echo -e "${CYAN}Checking $DIR_4_RAW_GIT_LOGS${NC}"

    # Check if directory exists
    if [[ ! -d "$DIR_4_RAW_GIT_LOGS" ]]; then
        echo -e "${YELLOW}Directory '$DIR_4_RAW_GIT_LOGS' does not exist.${NC}"
        exit 1
    fi





echo "hello"

select_files_for_processing "$DIR_4_RAW_GIT_LOGS"


echo "${selected_files[@]}"

print_selected_files "${selected_files[@]}"



echo -e "Checking if there are files to process "
    # Check if array is empty
    if [[ ${#selected_files[@]} -eq 0 ]]; then
        echo -e "${YELLOW}⚠ No files to process${NC}"
        return 1
    fi


echo "🙂"


echo -e "Checking the ScrapLogGit2Net script exists "

    # Check if SCRAPLOG_SCRIPT exists
    if [[ ! -f "$SCRAPLOG_SCRIPT" ]]; then
        echo -e "${RED}✗ ERROR: scrapLog.py not found at: $SCRAPLOG_SCRIPT${NC}"
        return 1
    fi


echo "🙂"

    echo -e "${CYAN}════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}        Processing with ScrapLogGit2Net${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}Script: ${YELLOW}$SCRAPLOG_SCRIPT${NC}"
    echo -e "${BLUE}Files to process: ${GREEN}${#selected_files[@]}${NC}"
    echo ""

    success_count=0
    fail_count=0
     processed_files=()

    # Loop through all selected files
    for file in "${selected_files[@]}"; do
        selected_filename_to_scraplog=$(basename "$file")

        echo -e "${MAGENTA}── Processing: ${YELLOW}$selected_filename_to_scraplog${NC} ──${NC}"

        # Check if file exists
        if [[ ! -f "$file" ]]; then
            echo -e "${RED}✗ File not found: $file${NC}"
            ((fail_count++))
            continue
        fi

        # Show file info
        file_size=$(du -h "$file" 2>/dev/null | cut -f1 || echo "unknown")
        line_count=$(wc -l < "$file" 2>/dev/null || echo "0")
        echo -e "${BLUE}Size: ${YELLOW}$file_size${NC}, ${BLUE}Lines: ${YELLOW}$line_count${NC}"
        echo -e "${BLUE}Path: ${CYAN}$file${NC}"


        # Run the scrapLog.py script with -r flag
        echo -e "${BLUE}Running command:${NC}"
        echo -e "${YELLOW}python \"$SCRAPLOG_SCRIPT\" -r \"$file\"${NC}"
        echo ""

        # Execute the command
        echo -e "${CYAN}Processing...${NC}"

        python_command="python3"

        # Capture output and error
        if $python_command "$SCRAPLOG_SCRIPT" -r "$file" 2>&1; then
            echo -e "${GREEN}✓ Successfully processed: $selected_filename_to_scraplog${NC}"
            ((success_count++))
            processed_files+=("$file")
        else
            exit_code=$?
            echo -e "${RED}✗ Failed to process: $selected_filename_to_scraplog (exit code: $exit_code)${NC}"
            ((fail_count++))
        fi

        echo ""
        echo -e "${CYAN}────────────────────────────────────────────────${NC}"
        echo ""


        echo -e "verifying ScrapLogGit2Net output "
        verify_and_visualize_graphml "$file"


    done

    # Summary
    echo -e "${CYAN}════════════════════════════════════════════════════${NC}"
    echo -e "${MAGENTA}Processing Summary:${NC}"
    echo -e "${BLUE}Total files: ${YELLOW}${#selected_files[@]}${NC}"
    echo -e "${GREEN}Successful: ${YELLOW}$success_count${NC}"

    if [[ $fail_count -gt 0 ]]; then
        echo -e "${RED}Failed: ${YELLOW}$fail_count${NC}"
    fi

    # List processed files
    if [[ $success_count -gt 0 ]]; then
        echo ""
        echo -e "${GREEN}Successfully processed files:${NC}"
        for processed_file in "${processed_files[@]}"; do
            echo -e "  ${YELLOW}$(basename "$processed_file")${NC}"
        done
    fi

    echo -e "${CYAN}════════════════════════════════════════════════════${NC}"

    if [[ $fail_count -eq 0 ]]; then
        echo -e "${GREEN}✅ All files processed successfully${NC}"
    else
        echo -e "${YELLOW}⚠ Processing completed with $fail_count failure(s)${NC}"
        exit 1
    fi







echo -e "You can now filter, visualize, analyze or transform the network \n"
exit 0
