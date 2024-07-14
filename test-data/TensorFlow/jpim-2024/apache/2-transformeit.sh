#!/bin/bash

source config.cfg



INPUT=$FILTERED_FILE

OUTPUT=$TRANSFORMED_FILE


echo -e  "Transforming network $INPUT" "\n"


TOP10_ORG=google,intel,nvidia,arm,ibm,amd,microsoft,huawei,amazon,naver

du -sh $INPUT

echo -r "Taking $FOCAL_ORG as the network we are transforming" "\n"

CMD="../../../../transform-nofi-2-nofo-GraphML.py -s $INPUT"


echo -e "Excecutiong:\n  $CMD \n"

eval $CMD

echo -e "TESTED" "Worked" "\n"

du -sh $INPUT


echo -e "Network is transformed, let's now see  the network \n"

echo "executing:"
echo ../../../../formatFilterAndViz-nofo-GraphML.py -v -l -ff $FOCAL_ORG $OUTPUT

../../../../formatFilterAndViz-nofo-GraphML.py -v -l -ff $FOCAL_ORG $OUTPUT


grep  $FOCAL_ORG $OUTPUT



