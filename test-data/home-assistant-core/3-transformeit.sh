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


INPUT=$FILTERED_FILE

OUTPUT=core.NetworkFile.out-filtered-transformed-to-nofo.graphML

file_exists_and_is_not_empty "$INPUT"
print_happy_smile
command_exists "$TRANSFORM_NO_FI_GRAPHML_SCRIPT" 
print_happy_smile


echo -e "We have a network file and a transformer"

print_heart     

echo -e  "Transforming network $INPUT" "\n"




CMD="$TRANSFORM_NO_FI_GRAPHML_SCRIPT  --show $INPUT"


echo -e "Excecutiong:\n  $CMD \n"

eval $CMD

echo -e "TESTED" "Worked" "\n"


echo -e "Network is transformed, let's now see  the network \n"

file_exists_and_is_not_empty "$OUTPUT"

print_happy_smile

