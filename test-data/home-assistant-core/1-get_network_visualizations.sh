if [ ! "$BASH_VERSION" ] ; then
    echo "Please do not use sh to run this script ($0), just execute it directly" 1>&2
    exit 1
fi



if [ ! "$BASH_VERSION" ] ; then
    exec /bin/bash "$0" "$@"
fi


source config.cfg
source utils.sh 



file_exists_and_is_not_empty  "$INPUT"
print_happy_smile
command_exists "$FFV_NO_FI_GRAPHML_SCRIPT"
print_happy_smile 

echo ""
echo "1) VAR FFV_NO_FI_GRAPHML_SCRIPT= $FFV_NO_FI_GRAPHML_SCRIPT"
echo "2) VAR INPUT = $INPUT"
echo "3) VAR COMPANIES_TO_IGNORE = $COMPANIES_TO_IGNORE"
echo "4) VAR TOP_10_COMPANIES $TOP_10_COMPANIES"
echo ""

echo -e "Invoking the $FFV_NO_FI_GRAPHML_SCRIPT with save_graphML so we can later transform it"

CMD="$FFV_NO_FI_GRAPHML_SCRIPT  $INPUT -pl --org_list_to_ignore $COMPANIES_TO_IGNORE --org_list_only $TOP_10_COMPANIES --save_graphML" 


echo -e "Excecutiong:\n  $CMD \n"

eval $CMD

echo -e "TESTED" "Worked" "\n"

echo -e "Filtered file saved at $FILTERED_FILE" "\n"

file_exists_and_is_not_empty  "$INPUT"


du sh $INPUT
du sh $FILTERED_FILE


