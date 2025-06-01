#!/bin/bash

FILTER=''../../../formatFilterAndViz-nofi-GraphML.py''
FILTER_ARG='-ot=top10 --save_graphML '

KOHA_NET_GraphML_PATH="../JASIST-2024-wp-networks-graphML"

echo TRANSFORMER=$TRANSFORMER
echo FILTER_ARG=$FILTER_ARG
echo KOHA_NET_GraphML_PATH=$KOHA_NET_GraphML_PATH


if [ ! "$BASH_VERSION" ] ; then
    echo "Please do not use sh to run this script ($0), just execute it directly" 1>&2
    exit 1
fi


echo Checking  if the target is not a directory
if [ ! -d "$KOHA_NET_GraphML_PATH" ]; then
  exit 1
fi

echo Loop through files in the developer networks directory
for file in "$KOHA_NET_GraphML_PATH"/*; do
  if [ -f "$file" ]; then
    echo "$file"

    if [[ $file == *.graphML ]]       #  this is the snag
              then
                    echo "Getting top10 for"  $file ":"
                    CMD="$FILTER $FILTER_ARG $file"

                    echo CMD = $CMD
                    exit
                    eval $CMD

              fi

  fi
done



INPUT=$FILTERED_FILE

OUTPUT=$TRANSFORMED_FILE


