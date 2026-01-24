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


exit

# Process the selected files
if [[ $? -eq 0 ]]; then
    echo "Processing selected files..."
    # $selected contains the file paths
    read -ra files_to_process <<< "$selected"

    for file in "${files_to_process[@]}"; do
        echo "Processing: $file"
        # python "$SCRAPLOG_SCRIPT" -i "$file" -o "output.xml"
    done
fi


exit



echo "size of input:"
du -sh $INPUT
echo 

CMD="$FFV_NO_FI_GRAPHML_SCRIPT  $INPUT --legend_type=top10  -pl --org_list_to_ignore=$COMPANIES_TO_IGNORE --org_list_only=$TOP10_ORG  --save_graphML" 


echo -e "Executing :\n  $CMD \n"

eval $CMD

echo -e "TESTED" "Worked" "\n"

echo -e "Filtered file saved at $FILTERED_FILE" "\n"


exit 

du -sh $INPUT
du -sh $FILTERED_FILE

echo -e "Let's now transform the network \n"

grep chromium $FILTERED_FILE
