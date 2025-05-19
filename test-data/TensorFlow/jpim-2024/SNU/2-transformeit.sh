#!/bin/bash

if [ ! "$BASH_VERSION" ] ; then
    echo "Please do not use sh to run this script ($0), just execute it directly" 1>&2
    exit 1
fi



if [ ! "$BASH_VERSION" ] ; then
    exec /bin/bash "$0" "$@"
fi


source config.cfg



INPUT=$FILTERED_FILE

OUTPUT=$TRANSFORMED_FILE


echo -e  "Transforming network $INPUT" "\n"

FOCAL_ORG=chromium

TOP10_ORG=google,intel,nvidia,arm,ibm,amd,microsoft,huawei,amazon,naver

du -sh $INPUT

echo -r "Taking $FOCAL_ORG as the network we are transforming" "\n"

CMD="../../../../transform-nofi-2-nofo-GraphML.py -s $INPUT"


echo -e "Excecutiong:\n  $CMD \n"

eval $CMD

echo -e "TESTED" "Worked" "\n"

du -sh $INPUT


echo -e "Network is transformed, let's now see  the network \n"
../../../../formatFilterAndViz-nofo-GraphML.py -l $OUTPUT

grep chromium $OUTPUT



