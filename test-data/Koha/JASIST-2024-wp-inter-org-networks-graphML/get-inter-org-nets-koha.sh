#!/bin/bash

TRANSFORMER=''../../../transform-nofi-2-nofo-GraphML.py''
TRANSFORMER_ARG=''

KOHA_NET_GraphML_PATH="../JASIST-2024-wp-networks-TOP10-graphML"

echo TRANSFORMER=$TRANSFORMER
echo TRANSFORMER_ARG=$TRANSFORMER_ARG
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
                    echo "Calling transformer" $file ":"
                    eval  $TRANSFORMER  $file
              fi

  fi
done



INPUT=$FILTERED_FILE

OUTPUT=$TRANSFORMED_FILE


