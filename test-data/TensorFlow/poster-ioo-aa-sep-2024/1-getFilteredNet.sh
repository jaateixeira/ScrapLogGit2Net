#!/bin/bash


if [ ! "$BASH_VERSION" ] ; then
    echo "Please do not use sh to run this script ($0), just execute it directly" 1>&2
    exit 1
fi



if [ ! "$BASH_VERSION" ] ; then
    exec /bin/bash "$0" "$@"
fi


source config.cfg



echo INPUT=$INPUT
echo FILTERED_FILE=$FILTERED_FILE
echo TOP10_ORG=$TOP10_ORG
echo FOCAL_ORG=$FOCAL_ORG
echo FFV_NO_FI_GRAPHML_SCRIPT=$FFV_NO_FI_GRAPHML_SCRIPT
echo COMPANIES_TO_IGNORE=$COMPANIES_TO_IGNORE
echo 


echo "size of input:"
du -sh $INPUT
echo 

CMD="$FFV_NO_FI_GRAPHML_SCRIPT  $INPUT --legend_type=top10  -pl --org_list_to_ignore=$COMPANIES_TO_IGNORE --org_list_only=$TOP10_ORG  --save_graphML" 



echo -e "Executing :\n  $CMD \n"

exit 
eval $CMD

echo -e "TESTED" "Worked" "\n"

echo -e "Filtered file saved at $FILTERED_FILE" "\n"


exit 

du -sh $INPUT
du -sh $FILTERED_FILE

echo -e "Let's now transform the network \n"

grep chromium $FILTERED_FILE
