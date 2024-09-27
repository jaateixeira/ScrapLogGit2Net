#!/bin/bash


if [ ! "$BASH_VERSION" ] ; then
    echo "Please do not use sh to run this script ($0), just execute it directly" 1>&2
    exit 1
fi



if [ ! "$BASH_VERSION" ] ; then
    exec /bin/bash "$0" "$@"
fi


source config.cfg
source utils.sh 



echo INPUT=$INPUT
echo FILTERED_FILE=$FILTERED_FILE
echo TOP10_ORG=$TOP10_ORG
echo FOCAL_ORG=$FOCAL_ORG
echo FFV_NO_FI_GRAPHML_SCRIPT=$FFV_NO_FI_GRAPHML_SCRIPT
echo TRANSFORM_GRAPHML_SCRIPT=$TRANSFORM_GRAPHML_SCRIPT
echo COMPANIES_TO_IGNORE=$COMPANIES_TO_IGNORE

INPUT=$FILTERED_FILE
OUTPUT=$TRANSFORMED_FILE


echo -e  "Transforming network $INPUT" "\n"

du -sh $INPUT

echo -r "Taking $FOCAL_ORG as the network we are transforming" "\n"

CMD="$TRANSFORM_GRAPHML_SCRIPT -s $INPUT"


echo -e "Excecutiong:\n  $CMD \n"

exit 

eval $CMD

echo -e "TESTED" "Worked" "\n"

du -sh $INPUT


echo -e "Network is transformed, let's now see  the network \n"
../../../../formatFilterAndViz-nofo-GraphML.py -l $OUTPUT

grep chromium $OUTPUT



